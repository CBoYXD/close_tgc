"""
PromoUser model for tracking bot interactions
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, SmallInteger, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from .base import AbstractBaseModel


class User(AbstractBaseModel):
	"""
	User model for tracking bot interactions
	"""

	username: Mapped[Optional[str]] = mapped_column(
		String(20),
		comment="Telegram username",
	)
	full_name: Mapped[str] = mapped_column(
		String(100),
		comment="User's full name",
	)

	# UTM tracking
	utm_source: Mapped[Optional[str]] = mapped_column(
		String(20),
		comment="UTM source parameter",
	)
	utm_campaign: Mapped[Optional[str]] = mapped_column(
		String(20),
		comment="UTM campaign parameter",
	)
	utm_content: Mapped[Optional[str]] = mapped_column(
		String(20),
		comment="UTM content parameter",
	)

	is_connected: Mapped[bool] = mapped_column(
		server_default=text("false"),
		comment="Whether user is connected to the closed channel",
	)
	connected_at: Mapped[Optional[datetime]] = mapped_column(
		DateTime(timezone=True),
		comment="When user connected to the closed channel",
	)

	# Reminder tracking
	reminders_sent: Mapped[int] = mapped_column(
		SmallInteger,
		server_default=text("0"),
		comment="Number of reminder messages already sent",
	)
	blocked_the_bot: Mapped[bool] = mapped_column(
		server_default=text("false"),
		comment="Whether user has blocked the bot",
	)

	# Additional data
	notes: Mapped[Optional[str]] = mapped_column(
		Text,
		comment="Additional notes about the user",
	)

	def __repr__(self) -> str:
		"""String representation of the promo user"""
		return (
			f"<PromoUser(id={self.id}, "
			f"username='{self.username}', is_connected={self.is_connected})>"
		)
