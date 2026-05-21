"""Course Review APIs"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import UUID4
from fastapi_pagination import Page
from fastapi_keycloak import OIDCUser

from ..models import Review, Course, CourseProgress
from ..schemas import Review as ReviewOut, ReviewUpdate, ReviewCreate, Roles

from utils import CustomParams, paginate_model
from core import idp

from .student import get_student_profile


review_router = APIRouter(prefix="/reviews")


@review_router.post("/", response_model=ReviewOut)
async def review_course(
    review_create: ReviewCreate,
    current_user: OIDCUser = Depends(
        idp.get_current_user(required_roles=[Roles.STUDENT])
    ),
):
    """Add review to a course"""

    _, student = await get_student_profile(
        current_user=current_user, check_subscription=False
    )
    student_id = student.id

    progress = await CourseProgress.get_course_student_id(
        student_id=student_id,
        course_id=review_create.course_id,
    )

    if progress is None or (progress and progress.overall_progress != 1.0):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You can not review this course. You must complete first",
        )

    course: Course = progress.course

    review = Review(**review_create.model_dump(mode="json"), student_id=student_id)

    await review.insert()
    course.reviews.append(review)

    await course.save()
    return review


@review_router.get("/course/{course_id}", response_model=Page[ReviewOut])
async def read_reviews_by_course_id(
    course_id: UUID4,
    full_load: bool = False,
    params: CustomParams = Depends(),
):
    """Read reviews by courses Id"""

    query = Review.get_course_id(course_id=course_id)

    return await paginate_model(
        query=query, params=params, full_load=full_load, fetch_links=True
    )


@review_router.get("/{review_id}", response_model=ReviewOut)
async def read_review(review_id: UUID4):
    """Get review by Id"""

    return await get_review_by_id(review_id=review_id)


@review_router.patch("/{review_id}", response_model=ReviewOut)
async def update_review(
    review_id: UUID4,
    update: ReviewUpdate,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Update review"""

    review = await get_review_by_id(review_id=review_id, current_user=current_user)
    fields = update.model_dump(exclude_unset=True, exclude_none=True)
    review_updated = review.model_copy(update=fields)
    await review_updated.save()
    return review_updated


@review_router.delete("/{review_id}")
async def delete_review(
    review_id: UUID4,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Delete review"""

    review = await get_review_by_id(review_id=review_id, current_user=current_user)

    await review.delete()

    # course = await Course.get(review.course_id)
    # new_reviews = [r for r in course.reviews if r.id != review.id]
    # await course.set({Course.reviews: new_reviews})

    return Response(status_code=status.HTTP_204_NO_CONTENT)


####################### COMMONS TOOLS #############################


async def get_review_by_id(review_id: UUID4, current_user: OIDCUser = None):
    """get Review by Id from Db"""

    review = await Review.get(review_id, fetch_links=True)

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    if current_user:
        _, student = await get_student_profile(
            current_user=current_user, check_subscription=False
        )
        if review.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
            )

    return review
