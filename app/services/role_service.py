from typing import List
from typing import Optional
from datetime import datetime
from sqlalchemy.future import select
from app.models.role_master import RoleMaster
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.role_master import RoleMasterAddEdit


def get_role_unique_id(role_name: str) -> str:
    """Generates a unique role ID based on the role name."""
    return f"CUSTOM_{role_name.upper().replace(' ', '_')}"



async def get_role_by_name(session: AsyncSession, name: str) -> Optional[RoleMaster]:
    """Fetches a role by its name."""
    result = await session.execute(select(RoleMaster).where(RoleMaster.name == name, RoleMaster.is_deleted == 0))
    return result.scalars().first()



async def get_role_by_id(session: AsyncSession, id: int) -> Optional[RoleMaster]:
    """Fetches a role by its ID."""
    result = await session.execute(select(RoleMaster).where(RoleMaster.id == id, RoleMaster.is_deleted == 0))
    return result.scalars().first()



async def get_all_roles(session: AsyncSession) -> List[RoleMaster]:
    """Fetches all non-deleted roles."""
    result = await session.execute(select(RoleMaster).where(RoleMaster.is_deleted == 0))
    return result.scalars().all()


async def add_edit_role(db: AsyncSession, role_data: RoleMasterAddEdit, created_by: Optional[int] = None, updated_by: Optional[int] = None) -> RoleMaster:
    """Adds a new role or edits an existing one."""
    if role_data.id == 0:
        # Check if role with same name already exists
        existing_role = await get_role_by_name(db, role_data.name)
        if existing_role:
            raise ValueError("Role with this name already exists.")

        role_unique_id = get_role_unique_id(role_data.name)
        new_role = RoleMaster(
            role_unique_id=role_unique_id,
            name=role_data.name,
            description=role_data.description,
            is_restricted=role_data.is_restricted,
            created_on=datetime.now(),
            created_by=created_by,
            updated_on=datetime.now(),
            updated_by=updated_by,
        )
        try:
            db.add(new_role)
            await db.commit()
            await db.refresh(new_role)
            return new_role
        except Exception as e:
            await db.rollback()
            raise e
    else:
        role_to_edit = await get_role_by_id(db, role_data.id)
        if not role_to_edit:
            raise ValueError(f"Role with ID {role_data.id} not found.")

        # Check for duplicate name if name is being changed
        if role_to_edit.name != role_data.name:
            existing_role_with_new_name = await get_role_by_name(db, role_data.name)
            if existing_role_with_new_name and existing_role_with_new_name.id != role_data.id:
                raise ValueError("Another role with this name already exists.")

        role_to_edit.name = role_data.name
        role_to_edit.description = role_data.description
        role_to_edit.is_restricted = role_data.is_restricted
        role_to_edit.updated_on = datetime.now()
        role_to_edit.updated_by = updated_by
        try:
            await db.commit()
            await db.refresh(role_to_edit)
            return role_to_edit
        except Exception as e:
            await db.rollback()
            raise e



async def delete_role(db: AsyncSession, role_id: int, deleted_by: Optional[int] = None) -> RoleMaster:
    """Deletes a role by marking it as deleted."""
    role_to_delete = await get_role_by_id(db, role_id)
    if not role_to_delete:
        raise ValueError(f"Role with ID {role_id} not found.")

    role_to_delete.is_deleted = 1
    role_to_delete.deleted_on = datetime.now()
    role_to_delete.deleted_by = deleted_by

    try:
        await db.commit()
        await db.refresh(role_to_delete)
        return role_to_delete
    except Exception as e:
        await db.rollback()
        raise e

