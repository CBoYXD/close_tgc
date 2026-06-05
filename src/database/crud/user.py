"""
This module contains the CRUD operations for the User model.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.crud.base import CRUDBase
from src.database.models.user import User
from src.database.schemas.user import UserCreate, UserUpdate


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
	"""
	CRUD class for the User model.
	"""

	async def mark_connected(self, db: AsyncSession, id: int) -> Optional[User]:
		"""
		Mark user as connected to the closed channel.
		:param db: Database session.
		:param id: user ID.
		:return: Updated User object or None.
		"""
		user = await self.get_by_id(db, id)
		if not user:
			return None

		return await self.update(
			db,
			user,
			UserUpdate(
				is_connected=True,
				connected_at=datetime.now(),
			),
		)

	async def update_reminders(
		self, db: AsyncSession, id: int
	) -> Optional[User]:
		"""
		Mark scheduled reminder message as sent.
		:param db: Database session.
		:param id: user ID.

		:return: Updated User object or None.
		"""
		user = await self.get_by_id(db, id)
		if not user:
			return None

		return await self.update(
			db,
			user,
			UserUpdate(
				reminders_sent=user.reminders_sent + 1,
			),
		)

	async def mark_user_blocked(
		self, db: AsyncSession, id: int, blocked: bool = True
	) -> Optional[User]:
		"""
		Mark user as having blocked or unblocked the bot.
		:param db: Database session.
		:param id: user ID.
		:param blocked: Whether user blocked the bot (True) or unblocked (False).
		:return: Updated User object or None.
		"""
		user = await self.get_by_id(db, id)
		if not user:
			return None

		return await self.update(
			db,
			user,
			UserUpdate(
				blocked_the_bot=blocked,
			),
		)

	async def get_users_for_reminder(self, db: AsyncSession) -> list[User]:
		"""
		Get users who need scheduled reminder messages.
		:param db: Database session.
		:return: list of User objects.
		"""
		query = select(User).where(
			User.is_connected.is_(False),
			User.blocked_the_bot.is_(False),
		)
		result = await db.execute(query)
		return list(result.scalars().all())

	async def get_connected_users(self, db: AsyncSession) -> list[User]:
		"""
		Get all connected users.
		:param db: Database session.
		:return: list of connected User objects.
		"""
		query = select(User).where(User.is_connected.is_(True))
		result = await db.execute(query)
		return list(result.scalars().all())

	async def get_blocked_users_count(self, db: AsyncSession) -> int:
		"""
		Get count of users who blocked the bot.
		:param db: Database session.
		:return: Count of blocked users.
		"""
		query = select(func.count(User.id)).where(
			User.blocked_the_bot.is_(True)
		)
		result = await db.execute(query)
		return result.scalar() or 0

	async def get_users_by_utm_source(
		self, db: AsyncSession, utm_source: str
	) -> list[User]:
		"""
		Get users by UTM source.
		:param db: Database session.
		:param utm_source: UTM source to filter by.
		:return: list of User objects.
		"""
		query = select(User).where(User.utm_source == utm_source)
		result = await db.execute(query)
		return list(result.scalars().all())

	async def get_users_by_utm_campaign(
		self, db: AsyncSession, utm_campaign: str
	) -> list[User]:
		"""
		Get users by UTM campaign.
		:param db: Database session.
		:param utm_campaign: UTM campaign to filter by.
		:return: list of User objects.
		"""
		query = select(User).where(User.utm_campaign == utm_campaign)
		result = await db.execute(query)
		return list(result.scalars().all())

	# Analytics methods (replacing UTM analytics table functionality)
	async def get_utm_analytics(
		self, db: AsyncSession, utm_source: Optional[str] = None
	) -> list[dict]:
		"""
		Get UTM analytics calculated from promo table.
		:param db: Database session.
		:param utm_source: Optional UTM source to filter by.
		:return: list of UTM analytics dictionaries.
		"""
		if utm_source:
			query = select(User).where(User.utm_source == utm_source)
		else:
			query = select(User).where(User.utm_source.isnot(None))

		result = await db.execute(query)
		users = list(result.scalars().all())

		# Group by UTM parameters
		utm_groups = {}
		for user in users:
			key = (user.utm_source, user.utm_campaign, user.utm_content)
			if key not in utm_groups:
				utm_groups[key] = {
					"utm_source": user.utm_source,
					"utm_campaign": user.utm_campaign,
					"utm_content": user.utm_content,
					"total_clicks": 0,
					"registrations": 0,
					"connections": 0,
					"first_click": None,
					"last_click": None,
				}

			utm_groups[key]["total_clicks"] += 1
			utm_groups[key]["registrations"] += (
				1  # Every user is a registration
			)

			if user.is_connected:
				utm_groups[key]["connections"] += 1

			# Track timestamps
			if (
				utm_groups[key]["first_click"] is None
				or user.created_at < utm_groups[key]["first_click"]
			):
				utm_groups[key]["first_click"] = user.created_at
			if (
				utm_groups[key]["last_click"] is None
				or user.created_at > utm_groups[key]["last_click"]
			):
				utm_groups[key]["last_click"] = user.created_at

		# Calculate conversion rates
		analytics = []
		for group in utm_groups.values():
			total_clicks = group["total_clicks"]
			group["registration_rate"] = round(
				(group["registrations"] / total_clicks * 100)
				if total_clicks > 0
				else 0,
				1,
			)
			group["connection_rate"] = round(
				(group["connections"] / total_clicks * 100)
				if total_clicks > 0
				else 0,
				1,
			)
			analytics.append(group)

		return analytics

	async def get_top_sources(
		self, db: AsyncSession, limit: int = 10
	) -> list[dict]:
		"""
		Get top performing UTM sources by connections.
		:param db: Database session.
		:param limit: Maximum number of results to return.
		:return: list of top performing UTM analytics dictionaries.
		"""
		analytics = await self.get_utm_analytics(db)
		# Sort by connections descending and limit results
		sorted_analytics = sorted(
			analytics, key=lambda x: x["connections"], reverse=True
		)
		return sorted_analytics[:limit]

	async def get_conversion_stats(self, db: AsyncSession) -> dict:
		"""
		Get overall conversion statistics.
		:param db: Database session.
		:return: dictionary with conversion statistics.
		"""
		# Get total counts
		total_users_query = select(func.count(User.id))
		total_users_result = await db.execute(total_users_query)
		total_users = total_users_result.scalar() or 0

		connected_users_query = select(func.count(User.id)).where(
			User.is_connected.is_(True)
		)
		connected_users_result = await db.execute(connected_users_query)
		connected_users = connected_users_result.scalar() or 0

		# Calculate rates
		registration_rate = round(
			100.0 if total_users > 0 else 0.0, 1
		)  # Every user is a registration
		connection_rate = round(
			(connected_users / total_users * 100) if total_users > 0 else 0.0,
			1,
		)

		return {
			"total_clicks": total_users,
			"total_registrations": total_users,
			"total_connections": connected_users,
			"registration_rate": registration_rate,
			"connection_rate": connection_rate,
		}

	async def get_by_utm_source(
		self, db: AsyncSession, utm_source: str
	) -> list[dict]:
		"""
		Get UTM analytics by source.
		:param db: Database session.
		:param utm_source: UTM source to filter by.
		:return: list of UTM analytics dictionaries.
		"""
		return await self.get_utm_analytics(db, utm_source)

	async def get_by_utm_campaign(
		self, db: AsyncSession, utm_campaign: str
	) -> list[dict]:
		"""
		Get UTM analytics by campaign.
		:param db: Database session.
		:param utm_campaign: UTM campaign to filter by.
		:return: list of UTM analytics dictionaries.
		"""
		query = select(User).where(User.utm_campaign == utm_campaign)
		result = await db.execute(query)
		users = list(result.scalars().all())

		# Group by UTM parameters
		utm_groups = {}
		for user in users:
			key = (user.utm_source, user.utm_campaign, user.utm_content)
			if key not in utm_groups:
				utm_groups[key] = {
					"utm_source": user.utm_source,
					"utm_campaign": user.utm_campaign,
					"utm_content": user.utm_content,
					"total_clicks": 0,
					"registrations": 0,
					"connections": 0,
					"first_click": None,
					"last_click": None,
				}

			utm_groups[key]["total_clicks"] += 1
			utm_groups[key]["registrations"] += 1

			if user.is_connected:
				utm_groups[key]["connections"] += 1

			# Track timestamps
			if (
				utm_groups[key]["first_click"] is None
				or user.created_at < utm_groups[key]["first_click"]
			):
				utm_groups[key]["first_click"] = user.created_at
			if (
				utm_groups[key]["last_click"] is None
				or user.created_at > utm_groups[key]["last_click"]
			):
				utm_groups[key]["last_click"] = user.created_at

		# Calculate conversion rates
		analytics = []
		for group in utm_groups.values():
			total_clicks = group["total_clicks"]
			group["registration_rate"] = round(
				(group["registrations"] / total_clicks * 100)
				if total_clicks > 0
				else 0,
				1,
			)
			group["connection_rate"] = round(
				(group["connections"] / total_clicks * 100)
				if total_clicks > 0
				else 0,
				1,
			)
			analytics.append(group)

		return analytics


user_crud = UserCRUD(User)
