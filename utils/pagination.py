""" Pagination utils
"""

from fastapi_pagination import Params
from fastapi_pagination.ext.beanie import paginate
from beanie import Document
from beanie.odm.queries.find import FindMany


class CustomParams(Params):
    """Custom Pagination params"""

    page: int = 1
    size: int = 10


async def paginate_model(
    query: FindMany[Document],
    params: CustomParams,
    fetch_links: bool = False,
    full_load: bool = False,
):
    """Paginate items"""

    if full_load:
        params.size = await query.count()

    return await paginate(
        query=query,
        params=params,
        fetch_links=fetch_links,
        sort=[("created_at", -1)],
    )
