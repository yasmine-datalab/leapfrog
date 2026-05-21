"""Module APIs module"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import UUID4
from fastapi_pagination import Page
from fastapi_keycloak import OIDCUser

from beanie import DeleteRules
from ..models import Module  # Course
from ..schemas import Module as ModuleOut, ModuleUpdate, ModuleCreate

from utils import CustomParams, paginate_model
from core import idp
from .course import get_course_by_id


module_router = APIRouter(prefix="/modules")


@module_router.post("/", response_model=ModuleOut)
async def create_module(
    module_create: ModuleCreate,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Add module to a course"""

    course = await get_course_by_id(
        course_id=module_create.course_id, current_user=current_user
    )
    module = Module(**module_create.model_dump(mode="json"))

    await module.insert()

    course.modules.append(module)
    await course.save()
    return module


@module_router.get("/course/{course_id}", response_model=Page[ModuleOut])
async def read_modules_by_course_id(
    course_id: UUID4,
    full_load: bool = False,
    params: CustomParams = Depends(),
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Read modules by courses Id"""

    course = await get_course_by_id(course_id=course_id, current_user=current_user)

    query = Module.get_course_id(course_id=course.id)

    return await paginate_model(
        query=query, params=params, full_load=full_load, fetch_links=True
    )


@module_router.get("/{module_id}", response_model=ModuleOut)
async def read_module_by_id(
    module_id: UUID4, current_user: OIDCUser = Depends(idp.get_current_user())
):
    """Get Module by Id"""

    _, module = await get_module_by_id(module_id=module_id, current_user=current_user)
    return module


@module_router.patch("/{module_id}", response_model=ModuleOut)
async def update_module(
    module_id: UUID4,
    update: ModuleUpdate,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Update module"""

    _, module = await get_module_by_id(module_id=module_id, current_user=current_user)
    fields = update.model_dump(exclude_unset=True, exclude_none=True)
    module_updated = module.model_copy(update=fields)
    await module_updated.save()
    return module_updated


@module_router.delete("/{module_id}")
async def delete_module(
    module_id: UUID4,
    current_user: OIDCUser = Depends(idp.get_current_user()),
):
    """Delete module"""

    _, module = await get_module_by_id(module_id=module_id, current_user=current_user)

    await module.delete(link_rule=DeleteRules.DELETE_LINKS)

    # new_modules = [m for m in course.modules if m.id != module_id]
    # print(new_modules)
    # await course.update({Course.modules: new_modules})

    return Response(status_code=status.HTTP_204_NO_CONTENT)


####################### COMMONS TOOLS #############################


async def get_module_by_id(module_id: UUID4, current_user: OIDCUser):
    """get Module by Id from Db"""

    module = await Module.get(module_id, fetch_links=True)

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    course = await get_course_by_id(
        course_id=module.course_id, current_user=current_user
    )

    return course, module
