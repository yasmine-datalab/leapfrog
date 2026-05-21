"""Lesson APIs"""

from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    Body,
    UploadFile,
    File,
)
from pydantic import UUID4
from fastapi_pagination import Page
from fastapi_keycloak import OIDCUser


from ..models import Lesson  # Module
from ..schemas import Lesson as LessonOut, LessonUpdate, LessonCreate

from utils import CustomParams, paginate_model
from ..services import save_in_minio
from core import idp

from .module import get_module_by_id

lesson_router = APIRouter(prefix="/lessons")


@lesson_router.post("/", response_model=LessonOut)
async def create_lesson(
    lesson_create: LessonCreate = Body(...),
    video: Optional[UploadFile] = File(None),
    resources: Optional[list[UploadFile]] = None,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Create Lesson"""

    course, module = await get_module_by_id(
        module_id=lesson_create.module_id, current_user=current_user
    )

    lesson = Lesson(**lesson_create.model_dump(mode="json"), course_id=course.id)

    if video:
        if not video.content_type.startswith("video/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File Type not allowed. Upload video",
            )

        lesson.video = await save_in_minio(file=video)

    if resources:
        for file in resources:
            lesson.resources.append(await save_in_minio(file=file))

    await lesson.insert()
    module.lessons.append(lesson)
    await module.save()
    return lesson


@lesson_router.get("/module/{module_id}", response_model=Page[LessonOut])
async def read_lessons_by_module(
    module_id: UUID4,
    full_load: bool = False,
    params: CustomParams = Depends(),
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Read lessons by module Id"""

    _, module = await get_module_by_id(module_id=module_id, current_user=current_user)

    query = Lesson.get_module_id(module_id=module.id)

    return await paginate_model(
        query=query, params=params, full_load=full_load, fetch_links=True
    )


@lesson_router.get("/{lesson_id}", response_model=LessonOut)
async def read_lesson(
    lesson_id: UUID4, current_user: OIDCUser = Depends(idp.get_current_user())
):
    """Get lesson by Id"""

    _, lesson = await get_lesson_by_id(lesson_id=lesson_id, current_user=current_user)

    return lesson


@lesson_router.patch("/{lesson_id}", response_model=LessonOut)
async def update_lesson(
    lesson_id: UUID4,
    update: LessonUpdate,
    video: Optional[UploadFile] = File(None),
    resources: Optional[list[UploadFile]] = None,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Update lesson"""

    _, lesson = await get_lesson_by_id(lesson_id=lesson_id, current_user=current_user)
    fields = update.model_dump(exclude_unset=True, exclude_none=True)
    lesson_updated = lesson.model_copy(update=fields)

    if video:
        if not video.content_type.startswith("video/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File Type not allowed. Upload video",
            )
        lesson_updated.video = await save_in_minio(file=video)

    if resources:
        for file in resources:
            lesson_updated.resources.append(await save_in_minio(file=file))

    await lesson_updated.save()
    return lesson_updated


@lesson_router.delete("/{lesson_id}")
async def delete_lesson(
    lesson_id: UUID4,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Delete course"""

    _, lesson = await get_lesson_by_id(lesson_id=lesson_id, current_user=current_user)

    await lesson.delete()
    # new_lessons = [l for l in module.lessons if l.id != lesson.id]
    # await module.set({Module.lessons: new_lessons})

    return Response(status_code=status.HTTP_204_NO_CONTENT)


####################### COMMONS TOOLS #############################


async def get_lesson_by_id(lesson_id: UUID4, current_user: OIDCUser):
    """get Module by Id from Db"""

    lesson = await Lesson.get(lesson_id)

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )

    _, module = await get_module_by_id(
        module_id=lesson.module_id, current_user=current_user
    )
    return module, lesson
