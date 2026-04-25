"""Course service """

from datetime import datetime
from fastapi import HTTPException, status
from pydantic import UUID4

from models import CourseProgress, Course, Lesson, Module


async def complete_lesson(progress: CourseProgress, lesson: Lesson):
    """Complete a lesson"""

    module_id = lesson.module_id

    if module_id not in progress.module_progress:
        progress.module_progress[module_id] = []

    lesson_id = lesson.id

    if lesson_id not in progress.module_progress[module_id]:
        progress.module_progress[module_id].append(lesson_id)

    await progress.update(
        {
            "$set": {
                "module_progress": progress.module_progress,
                "last_accessed": datetime.now(),
            }
        },
    )
    return await update_module_progress(progress=progress, module_id=module_id)


async def update_module_progress(progress: CourseProgress, module_id: UUID4):
    """Update module progress"""

    module: Module = next(
        [m for m in progress.course.modules if m.id == module_id], None
    )
    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    total_lessons = (
        len(module.lessons) if hasattr(module, "lessons") and module.lessons else 0
    )

    completed_lessons = len(progress.module_progress.get(module_id, []))

    module_progress = (completed_lessons / total_lessons) if total_lessons else 0.0

    if module_progress == 1.0 and module_id not in progress.completed_modules:
        await progress.update(
            {
                "$set": {"last_accessed": datetime.now()},
                "$push": {"completed_modules": module_id},
            }
        )

    await progress.update(
        {
            "$set": {
                "module_progress."
                + str(module_id): progress.module_progress.get(module_id, []),
                "last_accessed": datetime.now(),
            }
        }
    )
    return await update_overall_progress(progress=progress)


async def update_overall_progress(progress: CourseProgress):
    """Update course overall progress"""

    course = await Course.get(progress.course_id, fetch_links=True)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    total_modules = len(course.modules)

    completed_modules = len(progress.completed_modules) if progress else 0

    overall_progress = (completed_modules / total_modules) if total_modules else 0.0
    if overall_progress == 1.0:
        await progress.update(
            {
                "$set": {
                    "overall_progress": overall_progress,
                    "last_accessed": datetime.now(),
                    "end_date": datetime.now(),
                }
            },
        )

    await progress.update(
        {
            "$set": {
                "overall_progress": overall_progress,
                "last_accessed": datetime.now(),
            }
        },
    )

    return progress
