"""Note api"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi_keycloak import OIDCUser
from fastapi_pagination import Page
from pydantic import UUID4
from models import Note, CourseProgress
from schemas import (
    Roles,
    Note as NoteOut,
    NoteCreate,
    NoteUpdate,
)
from utils import CustomParams, paginate_model

from core import idp


from .student import get_student_profile


################ Notes management #######################

course_router = APIRouter(prefix="/notes", tags=["Student Courses notes"])


@course_router.post(
    "/",
    response_model=NoteOut,
)
async def create_note(
    note_create: NoteCreate,
    current_user: OIDCUser = Depends(idp.get_current_user(Roles.STUDENT)),
):
    """Add note to course"""

    progress = await get_progress_by_id(
        progress_id=note_create.progress_id, current_user=current_user
    )
    note = Note(**note_create.model_dump(mode="json"))
    await note.insert()
    progress.notes.append(note)
    await progress.save()
    return progress


@course_router.get("progress/{progress_id}", response_model=Page[NoteOut])
async def read_note(
    progress_id: UUID4,
    params: CustomParams = Depends(),
    current_user: OIDCUser = Depends(idp.get_current_user(Roles.STUDENT)),
):
    """Read all student notes"""

    _ = await get_progress_by_id(progress_id=progress_id, current_user=current_user)

    query = await Note.find(Note.progress_id == progress_id)

    return await paginate_model(query=query, params=params)


@course_router.patch(
    "/{note_id}",
    response_model=NoteOut,
)
async def update_note(
    note_id: UUID4,
    note_update: NoteUpdate,
    current_user: OIDCUser = Depends(idp.get_current_user(Roles.STUDENT)),
):
    """Update course note"""
    note = await get_note_by_id(note_id, current_user=current_user)

    fields = note_update.model_dump(exclude_unset=True, exclude_none=True)
    note_updated = note.model_copy(update=fields)
    await note_updated.save()
    return note_updated


@course_router.delete(
    "/{note_id}",
)
async def delete_note(
    note_id: UUID4,
    current_user: OIDCUser = Depends(idp.get_current_user(Roles.STUDENT)),
):
    """Update course note"""
    note = await get_note_by_id(note_id, current_user=current_user)
    await note.delete()
    # delete note from progress note liste
    return Response(status_code=status.HTTP_204_NO_CONTENT)


################ COMMONS TOOLS ########################################""


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
