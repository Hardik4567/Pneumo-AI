from datetime import datetime
from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.config_group import ConfigGroup 
from app.schemas.config import ConfigGroupAddEdit


def get_config_group_unique_id(group_name: str) -> str:
    """Generates a unique config group ID based on the group name."""
    return f"GROUP_{group_name.upper().replace(' ', '_')}"


async def get_config_group_by_name(session: AsyncSession, name: str) -> Optional[ConfigGroup]:
    """Fetches a config group by its name."""
    result = await session.execute(select(ConfigGroup).where(ConfigGroup.name == name, ConfigGroup.is_deleted == 0))
    return result.scalars().first()


async def get_config_group_by_id(session: AsyncSession, id: int) -> Optional[ConfigGroup]:
    """Fetches a config group by its ID."""
    result = await session.execute(select(ConfigGroup).where(ConfigGroup.id == id, ConfigGroup.is_deleted == 0))
    return result.scalars().first()


async def add_edit_config_group(db: AsyncSession, config_group_data: ConfigGroupAddEdit, created_by: Optional[int] = None, updated_by: Optional[int] = None) -> ConfigGroup:
    """Adds a new config group or edits an existing one."""
    if config_group_data.id == 0:
        # Check if config group with same name already exists
        existing_config_group = await get_config_group_by_name(db, config_group_data.name)
        if existing_config_group:
            raise ValueError("Config group with this name already exists.")

        group_unique_id = get_config_group_unique_id(config_group_data.name)
        new_config_group = ConfigGroup(
            group_unique_id=group_unique_id,
            name=config_group_data.name,
            description=config_group_data.description,
            created_on=datetime.now(),
            created_by=created_by,
            updated_on=datetime.now(),
            updated_by=updated_by,
        )
        try:
            db.add(new_config_group)
            await db.commit()
            await db.refresh(new_config_group)
            return new_config_group
        except Exception as e:
            await db.rollback()
            raise e
    else:
        config_group_to_edit = await get_config_group_by_id(db, config_group_data.id)
        if not config_group_to_edit:
            raise ValueError(f"Config group with ID {config_group_data.id} not found.")

        # Check for duplicate name if name is being changed
        if config_group_to_edit.name != config_group_data.name:
            existing_config_group_with_new_name = await get_config_group_by_name(db, config_group_data.name)
            if existing_config_group_with_new_name and existing_config_group_with_new_name.id != config_group_data.id:
                raise ValueError("Another config group with this name already exists.")

        config_group_to_edit.name = config_group_data.name
        config_group_to_edit.description = config_group_data.description
        config_group_to_edit.updated_on = datetime.now()
        config_group_to_edit.updated_by = updated_by
        try:
            await db.commit()
            await db.refresh(config_group_to_edit)
            return config_group_to_edit
        except Exception as e:
            await db.rollback()
            raise e


async def delete_config_group(db: AsyncSession, group_id: int, deleted_by: Optional[int] = None) -> ConfigGroup:
    """Deletes a config group by marking it as deleted."""
    config_group_to_delete = await get_config_group_by_id(db, group_id)
    if not config_group_to_delete:
        raise ValueError(f"Config group with ID {group_id} not found.")

    config_group_to_delete.is_deleted = 1
    config_group_to_delete.deleted_on = datetime.now()
    config_group_to_delete.deleted_by = deleted_by

    try:
        await db.commit()
        await db.refresh(config_group_to_delete)
        return config_group_to_delete
    except Exception as e:
        await db.rollback()
        raise e


async def get_all_config_groups(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[ConfigGroup]:
    """Fetches all non-deleted config groups."""
    result = await session.execute(select(ConfigGroup).where(ConfigGroup.is_deleted == 0).offset(skip).limit(limit))
    return result.scalars().all()
