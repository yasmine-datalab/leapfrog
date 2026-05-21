"""Course APIs Module"""

from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    File,
    UploadFile,
    Body,
    BackgroundTasks,
)
from fastapi.exceptions import RequestValidationError
from fastapi_keycloak import OIDCUser
from fastapi_pagination import Page
from pydantic import UUID4, ValidationError
from pydantic_core import PydanticCustomError, InitErrorDetails

from ..models import Course, CourseProgress, Lesson, Note
from ..schemas import (
    Course as CourseBase,
    CourseUpdate,
    CourseCreate,
    CourseProgram,
    CourseProgress as CourseProgressBase,
    CourseProgressUpdate,
    Roles,
)

from utils import CustomParams, paginate_model

from core import idp, get_keycloak_user

from ..services import (
    complete_lesson,
    save_in_minio,
    generate_certificate,
)

from .instructor import get_instructor_by_id, get_instructor_by_user_id, InstructorOut
from .student import get_student_profile


######################### OUT MODEL #############################


class CourseOut(CourseBase):
    """Course Out schema"""

    instructor: InstructorOut


class CourseProgramOut(CourseProgram):
    """Course Program Out schema"""

    instructor: InstructorOut


class CourseProgressOut(CourseProgressBase):
    """Course Progress Out schema"""

    course: CourseOut


######################### VIEWS #############################

course_router = APIRouter(prefix="/courses")


@course_router.post("/", response_model=CourseOut)
async def create_course(
    course_create: CourseCreate = Body(...),
    image: UploadFile = File(...),
    video: Optional[UploadFile] = File(None),
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Create course"""

    instructor_id = course_create.instructor_id

    if Roles.STAFF in current_user.roles:
        if instructor_id is None:
            errors = InitErrorDetails(
                type=PydanticCustomError(
                    "missing",
                    "Instructor id is required.",
                ),
                loc=["instructor_id"],
            )

            raise RequestValidationError(
                errors=ValidationError.from_exception_data(
                    line_errors=[errors], title="Validation Error"
                ).errors()
            )
        instructor = await get_instructor_by_id(
            instructor_id=instructor_id, current_user=current_user
        )

    else:

        user = get_keycloak_user(
            current_user=current_user,
            fetch_user=True,
            required_roles=[Roles.INSTRUCTOR],
        )
        instructor = await get_instructor_by_user_id(user_id=user.id)
        course_create.instructor_id = instructor.id

    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File Type not allowed. Upload image",
        )

    image_path = await save_in_minio(file=image)

    course = Course(
        **course_create.model_dump(), image=image_path, instructor=instructor
    )

    if video is not None:
        if not video.content_type.startswith("video/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File Type not allowed. Upload video",
            )
        course.video = await save_in_minio(file=video)

    course = await course.insert()
    return course


@course_router.get("/", response_model=Page[CourseOut])
async def read_courses_or_by_instructor(
    params: CustomParams = Depends(),
    instructor_id: Optional[UUID4] = None,
    full_load: bool = False,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Get all courses or only instructor courses"""

    query = Course.find(fetch_links=True)

    if Roles.STAFF not in current_user.roles:
        k_user = get_keycloak_user(
            current_user=current_user,
            required_roles=[Roles.INSTRUCTOR],
            fetch_user=True,
        )

        instructor = await get_instructor_by_user_id(k_user.id)
        instructor_id = instructor.id

    if instructor_id:
        query = Course.find(Course.instructor == instructor_id, fetch_links=True)

    return await paginate_model(
        query=query, params=params, full_load=full_load, fetch_links=True
    )


@course_router.get("/{course_id}", response_model=CourseOut)
async def read_course_by_id(
    course_id: UUID4, current_user: OIDCUser = Depends(idp.get_current_user())
):
    """Read course by Id"""

    return await get_course_by_id(course_id, current_user=current_user)


@course_router.patch("/{course_id}", response_model=CourseOut)
async def update_course(
    course_id: UUID4,
    course_update: CourseUpdate = Body(...),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    current_user: OIDCUser = Depends(
        idp.get_current_user(required_roles=[Roles.INSTRUCTOR])
    ),
):
    """Update instcutor course"""

    course = await get_course_by_id(course_id=course_id, current_user=current_user)

    fields = course_update.model_dump(exclude_unset=True, exclude_none=True)
    course_updated = course.model_copy(update=fields)

    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File Type not allowed. Upload image",
            )
        course_updated.image = await save_in_minio(file=image)

    if video:
        if not video.content_type.startswith("video/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File Type not allowed. Upload video",
            )

        course_updated.video = await save_in_minio(file=video)

    await course_updated.save()

    return course_updated


@course_router.delete("/{course_id}")
async def delete_course(
    course_id: UUID4, current_user: OIDCUser = Depends(idp.get_current_user())
):
    """Delete course"""

    course = await get_course_by_id(course_id=course_id, current_user=current_user)

    await course.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


#################### STUDENT COURSE PROGRESS ##############################


@course_router.get(
    "/progress/{course_id}",
    response_model=CourseProgressOut
)
async def get_course_progress(
    course_id: UUID4,
    student_id: Optional[UUID4] = None,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Enroll/Start or Progress of a course by student"""
    if Roles.STAFF in current_user.roles:

        if student_id is None:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student id is required.",
            )

    else:

        _, student = await get_student_profile(current_user=current_user)
        student_id = student.id

    progress = await CourseProgress.get_course_student_id(
        student_id=student_id,
        course_id=course_id,
    )

    if progress is None:

        if Roles.STAFF in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course progress not found (student has not started yet)",
            )

        course = await get_course_by_id(course_id=course_id)

        progress = CourseProgress(
            student_id=student_id, course_id=course_id, course=course
        )
        await progress.insert()

    return progress


@course_router.get(
    "/progress/student/all",
    response_model=Page[CourseProgressOut]
)
async def read_student_all_courses_process(
    student_id: Optional[UUID4] = None,
    full_load: bool = False,
    params: CustomParams = Depends(),
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Get course progresses for a student"""

    if Roles.STAFF in current_user.roles:

        if student_id is None:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student id is required.",
            )

    else:
        _, student = await get_student_profile(current_user=current_user)
        student_id = student.id

    query = CourseProgress.get_all_courses_student_id(student_id=student_id)

    return await paginate_model(
        query=query, params=params, full_load=full_load, fetch_links=True
    )


@course_router.patch(
    "/progress/{progress_id}",
    response_model=CourseProgressOut
)
async def update_course_progress(
    progress_id: UUID4,
    progress_update: CourseProgressUpdate,
    current_user: OIDCUser = Depends(idp.get_current_user(Roles.STUDENT)),
):
    """Update course progress"""
    progress = await get_progress_by_id(progress_id=progress_id, current_user=current_user)
    fields = progress_update.model_dump(exclude_unset=True, exclude_none=True)
    progress_updated = progress.model_copy(update=fields)
    await progress_updated.save()
    return progress_updated


@course_router.post(
    "/progress/{course_id}/lessons/{lesson_id}/complete",
    response_model=CourseProgressOut
)
async def mark_lesson_complete(
    course_id: UUID4,
    lesson_id: UUID4,
    background_task: BackgroundTasks,
    current_user: OIDCUser = Depends(idp.get_current_user(Roles.STUDENT)),
):
    """Complete a lesson by student"""

    lesson = await Lesson.get(lesson_id)

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    user, student = await get_student_profile(current_user=current_user)
    student_id = student.id

    progress = await CourseProgress.get_course_student_id(
        student_id=student_id,
        course_id=course_id,
    )

    if progress is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not started this course yet)",
        )

    updated_progress = await complete_lesson(progress=progress, lesson=lesson)

    if updated_progress.overall_progress == 1.0:
        background_task.add_task(generate_certificate, updated_progress, user)

    return updated_progress


#################### COURSE CATALOG ##############################


@course_router.get(
    "/catalog/program",
    response_model=Page[CourseProgramOut]
)
async def get_courses_catalog(
    params: CustomParams = Depends(),
    full_load: bool = False,
):
    """read All courses uin the catalog"""

    query = Course.find(fetch_links=True)

    return await paginate_model(
        query=query, params=params, full_load=full_load, fetch_links=True
    )


@course_router.get(
    "/catalog/program/{course_id}",
    response_model=CourseProgramOut
)
async def get_course_program_by_id(course_id: UUID4):
    """Read course by id in the catalog"""

    return await get_course_by_id(course_id=course_id)


################ COMMONS TOOLS ########################################""


async def get_course_by_id(course_id: UUID4, current_user: OIDCUser = None):
    """get course by Id from Db"""

    course = await Course.get(course_id, fetch_links=True)

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    if current_user and Roles.STAFF not in current_user.roles:

        user = get_keycloak_user(
            current_user=current_user,
            required_roles=[Roles.INSTRUCTOR],
            fetch_user=True,
        )

        instructor = await get_instructor_by_user_id(user_id=user.id)

        if course.instructor.id != instructor.id:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )
    return course


async def get_note_by_id(note_id: UUID4, current_user: OIDCUser):
    """get course by Id from Db"""

    note = await Note.get(note_id)

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )

    progress = await CourseProgress.get(note.progress_id)

    _, student = await get_student_profile(current_user=current_user)

    if progress.student_id != student.id:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return note


async def get_progress_by_id(progress_id: UUID4, current_user: OIDCUser):
    """Get progress by ID from DB"""
    _, student = await get_student_profile(current_user=current_user)
    student_id = student.id

    progress = await CourseProgress.get_course_student_id(
        student_id=student_id,
        course_id=progress_id,
    )

    if progress is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not started this course yet)",
        )
    return progress
