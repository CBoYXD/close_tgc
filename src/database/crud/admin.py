"""
This module contains the CRUD operations for the Admin model.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud.base import CRUDBase
from src.database.models.admin import Admin
from src.database.schemas.admin import AdminCreate, AdminUpdate


class AdminCRUD(CRUDBase[Admin, AdminCreate, AdminUpdate]):
	"""
	CRUD class for the Admin model.
	"""

	async def get_super_admins(self, db: AsyncSession) -> list[Admin]:
		"""
		Retrieve all super admins.
		"""
		statement = select(self.model).where(self.model.super_admin.is_(True))
		result = await db.execute(statement)
		return result.scalars().all()

	async def get_admin_ids(
		self, db: AsyncSession, super_admin: Optional[bool] = None
	) -> list[int]:
		"""
		Retrieve all admin IDs.
		:param db: Database session.
		:return: List of telegram IDs.
		"""
		query = select(Admin.id)
		if super_admin is not None:
			query = query.where(Admin.super_admin.is_(super_admin))
		result = await db.execute(query)
		return result.scalars().all()


admin_crud = AdminCRUD(Admin)
