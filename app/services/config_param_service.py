from datetime import datetime
from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.config_param import ConfigParam
from app.models.config_group import ConfigGroup
from app.schemas.config import ConfigParamAddEdit


async def get_config_param_unique_id(session: AsyncSession, config_group_id: int, param_name: str) -> str:
    """Generates a unique config param ID based on the param name."""
    result = await session.execute(select(ConfigGroup).where(ConfigGroup.id == config_group_id, ConfigGroup.is_deleted == 0))
    config_group = result.scalars().first()
    if not config_group:
        raise ValueError(f"Config group with ID {config_group_id} not found.")
    group_name = config_group.name.upper().replace(' ', '_')
    return f"{group_name}_{param_name.upper().replace(' ', '_')}"



async def get_config_param_by_name(session: AsyncSession, name: str) -> Optional[ConfigParam]:
    """Fetches a config param by its name."""
    result = await session.execute(select(ConfigParam).where(ConfigParam.name == name, ConfigParam.is_deleted == 0))
    return result.scalars().first()



async def get_config_param_by_id(session: AsyncSession, id: int) -> Optional[ConfigParam]:
    """Fetches a config param by its ID."""
    result = await session.execute(select(ConfigParam).where(ConfigParam.id == id, ConfigParam.is_deleted == 0))
    return result.scalars().first()



async def add_edit_config_param(db: AsyncSession, config_param_data: ConfigParamAddEdit, created_by: Optional[int] = None, updated_by: Optional[int] = None) -> ConfigParam:
    """Adds a new config param or edits an existing one."""
    if config_param_data.id == 0:
        # Check if config param with same name already exists
        existing_config_param = await get_config_param_by_name(db, config_param_data.name)
        if existing_config_param:
            raise ValueError("already exist")

        param_unique_id = await get_config_param_unique_id(db, config_param_data.config_group_id, config_param_data.name)
        new_config_param = ConfigParam(
            param_unique_id=param_unique_id,
            name=config_param_data.name,
            description=config_param_data.description,
            config_group_id=config_param_data.config_group_id,
            created_on=datetime.now(),
            created_by=created_by,
            updated_on=datetime.now(),
            updated_by=updated_by,
        )
        try:
            db.add(new_config_param)
            await db.commit()
            await db.refresh(new_config_param)
            return new_config_param
        except Exception as e:
            await db.rollback()
            raise e
    else:
        config_param_to_edit = await get_config_param_by_id(db, config_param_data.id)
        if not config_param_to_edit:
            raise ValueError(f"Config param with ID {config_param_data.id} not found.")

        # Check for duplicate name if name is being changed
        if config_param_to_edit.name != config_param_data.name:
            existing_config_param_with_new_name = await get_config_param_by_name(db, config_param_data.name)
            if existing_config_param_with_new_name and existing_config_param_with_new_name.id != config_param_data.id:
                raise ValueError("already exist")

        config_param_to_edit.name = config_param_data.name
        config_param_to_edit.description = config_param_data.description
        config_param_to_edit.config_group_id = config_param_data.config_group_id
        if config_param_data.param_unique_id is not None:
            config_param_to_edit.param_unique_id = config_param_data.param_unique_id
        config_param_to_edit.updated_on = datetime.now()
        config_param_to_edit.updated_by = updated_by
        try:
            await db.commit()
            await db.refresh(config_param_to_edit)
            return config_param_to_edit
        except Exception as e:
            await db.rollback()
            raise e



async def delete_config_param(db: AsyncSession, param_id: int, deleted_by: Optional[int] = None) -> ConfigParam:
    """Deletes a config param by marking it as deleted."""
    config_param_to_delete = await get_config_param_by_id(db, param_id)
    if not config_param_to_delete:
        raise ValueError(f"Config param with ID {param_id} not found.")

    config_param_to_delete.is_deleted = 1
    config_param_to_delete.deleted_on = datetime.now()
    config_param_to_delete.deleted_by = deleted_by

    try:
        await db.commit()
        await db.refresh(config_param_to_delete)
        return config_param_to_delete
    except Exception as e:
        await db.rollback()
        raise e



async def get_all_config_params(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[ConfigParam]:
    """Fetches all non-deleted config params."""
    result = await session.execute(select(ConfigParam).where(ConfigParam.is_deleted == 0).offset(skip).limit(limit))
    return result.scalars().all()
