"""
This module contains the Pydantic schemas for the User model.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
	"""
	Base schema for the User model.
	"""

	id: int
	username: Optional[str] = None
	full_name: str
	utm_source: Optional[str] = None
	utm_campaign: Optional[str] = None
	utm_content: Optional[str] = None


class UserUpdate(BaseModel):
	"""
	Schema for updating a User.
	"""

	is_connected: Optional[bool] = None
	connected_at: Optional[datetime] = None
	reminders_sent: Optional[int] = None
	blocked_the_bot: Optional[bool] = None
	notes: Optional[str] = None
