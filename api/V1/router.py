"""API route"""

from fastapi import APIRouter

from features.lms.routers import (
    certificate_router,
    lesson_router,
    module_router,
    review_router,
    student_router,
    course_router,
    instructor_router,
    note_router
)
router = APIRouter()

lms_routers = [
    certificate_router,
    lesson_router,
    module_router,
    review_router,
    student_router,
    course_router,
    instructor_router,
    note_router
]

for this_router in lms_routers:
    router.include_router(this_router, prefix="/lms", tags=["lms"])
