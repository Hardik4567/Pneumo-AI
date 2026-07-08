from app.db.base_class import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, func, BigInteger

class MenuHierarchy(Base):
    __tablename__ = "menu_hierarchy"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    disp_name = Column(String(255), nullable=False)
    parent_id = Column(BigInteger, nullable=False)
    parent_unique_id = Column(String(255))
    entity_url = Column(String(255), nullable=False)
    menu_icon = Column(String(255))
    description = Column(String(1000))
    is_active = Column(Integer, default=1)
    enable_for_others = Column(Integer)
    icon_name = Column(String(100))
    display_order = Column(BigInteger)
    menu_unique_id = Column(String(255))
    request_date_time = Column(TIMESTAMP)
    request_source = Column(Integer)
    is_deleted = Column(Integer, default=0)
    created_on = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(Integer)

    updated_on = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )
    updated_by = Column(Integer)

    deleted_on = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_by = Column(Integer)

