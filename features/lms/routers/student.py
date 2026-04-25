"""Student APIs module"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
)
from fastapi_keycloak import OIDCUser
from fastapi_pagination import Page
from pydantic import UUID4, model_validator

from models import Student
from schemas import (
    StudentCreate,
    Student as StudentBase,
    StudentUpdate,
    Roles,
    SubscriptionStatus,
)

from core import idp, get_keycloak_user, verify_user_id, logger
from services import get_user_subscription
from utils import CustomParams, paginate_model


######################### OUT MODEL #############################


class StudentOut(StudentBase):
    """Student Out schema"""

    last_name: str | None = None
    first_name: str | None = None
    email: str | None = None

    @model_validator(mode="before")
    @classmethod
    def fetch_name(cls, data):
        """Fetch Stduent Names"""

        if isinstance(data, Student):
            data_dict = data.model_dump()
            user_id = data_dict.get("user_id")
        elif isinstance(data, dict):
            data_dict = data
            user_id = data.get("user_id")
        else:
            raise ValueError("Data must be an Instructor object or a dictionary")

        if user_id:
            try:
                user = idp.get_user(user_id=user_id)
                data_dict["last_name"] = user.lastName
                data_dict["first_name"] = user.firstName
                data_dict["email"] = user.email
            # pylint: disable=W0718
            except Exception as e:

                logger.error("Error fetching user data: %s", e)
                data_dict["last_name"] = "Unknown"
                data_dict["first_name"] = "Unknown"
                data_dict["email"] = "Unknown"
        return data_dict


######################### VIEWS #############################

student_router = APIRouter(prefix="/students", tags=["Students"])


@student_router.post("/", response_model=StudentOut)
async def create_student(
    student_create: StudentCreate,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Create Student profile"""

    user_id = student_create.user_id

    if Roles.STAFF in current_user.roles:
        await verify_user_id(user_id=user_id)

    else:
        user = get_keycloak_user(
            current_user=current_user,
            fetch_user=True,
        )
        student_create.user_id = user.id
        user_id = user.id

    if existing_profile := await Student.get_user_id(user_id=user_id):
        student = existing_profile.model_copy(
            update=student_create.model_dump(
                mode="json", exclude_none=True, exclude_unset=True
            )
        )
    else:

        student = Student(
            **student_create.model_dump(mode="json"),
        )

    await student.save()

    idp.add_user_roles(roles=[Roles.STUDENT], user_id=user_id)

    return student


@student_router.get("/", response_model=Page[StudentOut])
async def read_students(
    params: CustomParams = Depends(),
    full_load: bool = False,
    _: OIDCUser = Depends(idp.get_current_user(required_roles=[Roles.STAFF])),
):
    """Read All student"""

    query = Student.find_all()

    return await paginate_model(
        query=query, params=params, full_load=full_load, fetch_links=True
    )


@student_router.get("/{student_id}", response_model=StudentOut)
async def read_student_by_id(
    student_id: UUID4,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Read Student by Id"""

    return await get_student_by_id(student_id=student_id, current_user=current_user)


@student_router.get("/me/profile", response_model=StudentOut)
async def student_profile(
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Read Profile"""

    k_user = get_keycloak_user(current_user=current_user, fetch_user=True)
    return await get_student_by_user_id(user_id=k_user.id)


@student_router.patch("/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: str,
    student_update: StudentUpdate,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Update student"""
    student = await get_student_by_id(student_id=student_id, current_user=current_user)
    fields = student_update.model_dump(exclude_unset=True, exclude_none=True)
    student = student.model_copy(update=fields)
    await student.save()

    return student


@student_router.delete("/{student_id}")
async def delete_student(
    student_id: UUID4,
    current_user: OIDCUser = Depends(
        idp.get_current_user(required_roles=[Roles.STAFF])
    ),
):
    """Delete student"""

    student = await get_student_by_id(student_id=student_id, current_user=current_user)
    await student.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


################ COMMONS TOOLS ########################################


async def get_student_profile(current_user: OIDCUser, check_subscription: bool = True):
    """Fetch student profile and check his subscription"""
    user = get_keycloak_user(
        current_user=current_user,
        fetch_user=True,
        required_roles=[Roles.STUDENT],
    )
    student = await get_student_by_user_id(user_id=user.id)

    if check_subscription:
        await student_has_suscribed(user_id=user.id)

    return user, student


async def student_has_suscribed(user_id: str) -> bool:
    """Verify is student has valid subscription"""

    subscription = await get_user_subscription(user_id=user_id)

    if subscription is None or subscription.status != SubscriptionStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="You need valid subscription to take course",
        )

    return subscription


async def get_student_by_id(student_id: UUID4, current_user: OIDCUser):
    """Get student by Id from Db"""

    student = await Student.get(student_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    if Roles.STAFF not in current_user.roles:

        user = get_keycloak_user(current_user=current_user, fetch_user=True)

        if student.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )

    return student


async def get_student_by_user_id(user_id: str):
    """get student by Id from Db"""

    student = await Student.get_user_id(user_id=user_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    return student
