"""
This module contains the Pydantic schemas for the Admin model.
"""

from typing import Optional

from pydantic import BaseModel


class AdminCreate(BaseModel):
	"""
	Schema for creating an Admin.
	"""

	id: int
	super_admin: bool = False
	is_active: bool = True


class AdminUpdate(BaseModel):
	"""
	Schema for updating an Admin.
	"""

	super_admin: Optional[bool]
	is_active: Optional[bool]
