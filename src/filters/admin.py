from typing import Optional

from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.database.crud.admin import admin_crud
from src.database.setup import db_manager


class AdminFilter(BaseFilter):
	def __init__(self, super_admin: Optional[bool] = False):
		self.super_admin = super_admin

	async def __call__(self, obj: Message) -> bool:
		# Get admin telegram IDs from database
		async with db_manager.session() as db:
			admin_telegram_ids = await admin_crud.get_admin_ids(
				db, self.super_admin
			)

		# Check if user is in admin list
		is_user_admin = obj.from_user.id in admin_telegram_ids

		return is_user_admin
