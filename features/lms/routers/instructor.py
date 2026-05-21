"""Instructor APIs module"""

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

from ..models import Instructor
from ..schemas import (
    InstructorCreate,
    Instructor as InstructorBase,
    InstructorUpdate,
    Roles,
)

from core import idp, get_keycloak_user, verify_user_id, logger

from utils import CustomParams, paginate_model

######################### OUT MODEL #############################


class InstructorOut(InstructorBase):
    """Instructor Out schema"""

    last_name: str | None = None
    first_name: str | None = None
    email: str | None = None

    @model_validator(mode="before")
    @classmethod
    def fetch_name(cls, data):
        """Fetch Instructor Names"""

        if isinstance(data, Instructor):
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

instructor_router = APIRouter(prefix="/instructors")


@instructor_router.post("/", response_model=InstructorOut)
async def create_instructor(
    instructor_create: InstructorCreate,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Create instructor profile"""

    user_id = instructor_create.user_id
    if Roles.STAFF in current_user.roles:
        await verify_user_id(user_id=user_id)

    else:
        user = get_keycloak_user(
            current_user=current_user,
            fetch_user=True,
        )
        instructor_create.user_id = user.id
        user_id = user.id

    if existing_profile := await Instructor.get_user_id(user_id=user_id):
        instructor = existing_profile.model_copy(
            update=instructor_create.model_dump(
                mode="json", exclude_none=True, exclude_unset=True
            )
        )
    else:

        instructor = Instructor(
            **instructor_create.model_dump(mode="json"),
        )

    await instructor.save()

    idp.add_user_roles(roles=[Roles.INSTRUCTOR], user_id=user_id)

    return instructor


@instructor_router.get("/", response_model=Page[InstructorOut])
async def read_instructors(
    params: CustomParams = Depends(),
    full_load: bool = False,
    _: OIDCUser = Depends(idp.get_current_user(required_roles=[Roles.STAFF])),
):
    """Read All instructor"""

    query = Instructor.find_all()

    return await paginate_model(
        query=query, params=params, full_load=full_load, fetch_links=True
    )


@instructor_router.get("/{instructor_id}", response_model=InstructorOut)
async def read_instructor_by(
    instructor_id: UUID4,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Read instructor by Id"""

    return await get_instructor_by_id(
        instructor_id=instructor_id, current_user=current_user
    )


@instructor_router.get("/me/profile", response_model=InstructorOut)
async def instructor_profile(
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Read Profile"""

    k_user = get_keycloak_user(current_user=current_user, fetch_user=True)

    return await get_instructor_by_user_id(user_id=k_user.id)


@instructor_router.patch("/{instructor_id}", response_model=InstructorOut)
async def update_instructor(
    instructor_id: str,
    instructor_update: InstructorUpdate,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Update instructor"""

    instructor = await get_instructor_by_id(
        instructor_id=instructor_id, current_user=current_user
    )
    fields = instructor_update.model_dump(exclude_unset=True, exclude_none=True)
    instructor = instructor.model_copy(update=fields)
    await instructor.save()

    return instructor


@instructor_router.delete("/{instructor_id}")
async def delete_instructor(
    instructor_id: UUID4,
    current_user: OIDCUser = Depends(
        idp.get_current_user(required_roles=[Roles.STAFF])
    ),
):
    """Delete instructor"""

    instructor = await get_instructor_by_id(
        instructor_id=instructor_id, current_user=current_user
    )
    await instructor.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def get_instructor_by_id(instructor_id: UUID4, current_user: OIDCUser):
    """Get instructor by Id from Db"""

    instructor = await Instructor.get(instructor_id)

    if instructor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found"
        )

    if Roles.STAFF not in current_user.roles:

        user = get_keycloak_user(current_user=current_user, fetch_user=True)

        if instructor.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found"
            )

    return instructor


async def get_instructor_by_user_id(user_id: str):
    """get instructor by Id from Db"""

    instructor = await Instructor.get_user_id(user_id=user_id)

    if instructor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found"
        )

    return instructor
