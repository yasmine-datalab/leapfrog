"""Certificate APIs Module"""

from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
)
from pydantic import UUID4
from fastapi_pagination import Page
from fastapi_keycloak import OIDCUser

from ..models import Certificate
from ..schemas import Certificate as CertificateOut, Roles

from utils import CustomParams, paginate_model

from core import idp
from .student import get_student_profile

certificate_router = APIRouter(prefix="/certificates")

# Need certficate generation trigger endpoint ?

@certificate_router.get("/", response_model=Page[CertificateOut])
async def reads_certificates_or_by_course(
    student_id: Optional[UUID4] = None,
    params: CustomParams = Depends(),
    full_load: bool = False,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Get all certificates or only studuent certificates"""

    query = Certificate.find(fetch_links=True)

    if Roles.STAFF not in current_user.roles:

        _, student = await get_student_profile(
            current_user=current_user, check_subscription=False
        )
        student_id = student.id

    if student_id:
        query = Certificate.get_student_id(student_id=student_id)

    return await paginate_model(
        query=query, params=params, full_load=full_load, fetch_links=True
    )


@certificate_router.get("/{certificate_id}", response_model=CertificateOut)
async def read_certficate_by_id(
    certificate_id: UUID4,
    current_user: OIDCUser = Depends(
        idp.get_current_user(required_roles=[Roles.STAFF])
    ),
):
    """Read certficate by Id"""

    return await get_certificate_by_id(
        certificate_id=certificate_id, current_user=current_user
    )


@certificate_router.delete("/{certificate_id}")
async def delete_certficate(
    certificate_id: UUID4,
    current_user: OIDCUser = Depends(
        idp.get_current_user(required_roles=[Roles.ADMIN])
    ),
):
    """Delete certificate"""

    certficate = await get_certificate_by_id(
        certificate_id=certificate_id, current_user=current_user
    )

    await certficate.delete()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


####################### COMMONS TOOLS #############################


async def get_certificate_by_id(certificate_id: UUID4, current_user: OIDCUser = None):
    """get Review by Id from Db"""

    certificate = await Certificate.get(certificate_id)

    if certificate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found"
        )

    if Roles.STAFF not in current_user.roles:
        _, student = await get_student_profile(
            current_user=current_user, check_subscription=False
        )

        if certificate.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found"
            )

    return certificate
