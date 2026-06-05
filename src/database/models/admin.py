"""
Admin model for storing admin credentials
"""

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column

from .base import AbstractBaseModel


class Admin(AbstractBaseModel):
	"""
	Admin model for storing admin credentials
	"""

	super_admin: Mapped[bool] = mapped_column(
		server_default=text("false"),
		comment="Is this admin a super admin",
	)
	is_active: Mapped[bool] = mapped_column(
		server_default=text("true"),
		comment="Whether the admin account is active",
	)

	def __repr__(self) -> str:
		"""String representation of the admin"""
		return f"<Admin(id={self.id}, super_admin={self.super_admin}, created_at={self.created_at})>"
