from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.menu_hierarchy import MenuHierarchy
from app.models.privileges_master import PrivilegesMaster


async def get_all_active_menu_hierarchy(db: AsyncSession):
    """
    Get all active menu hierarchy entries from the database.
    """
    result = await db.execute(select(MenuHierarchy).filter(MenuHierarchy.is_deleted == 0))
    return result.scalars().all()



async def get_all_privileges(db: AsyncSession):
    """
    Get all privileges from the database for mapping with roles.
    """
    result = await db.execute(select(PrivilegesMaster).filter(PrivilegesMaster.is_deleted == 0))
    return result.scalars().all()


