"""
Scheduler service combining alert and promo schedulers.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from redis import asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.crud.user import user_crud
from src.database.setup import db_manager
from src.logger_config import get_logger
from src.templates import render_template

logger = get_logger("scheduler")


@asynccontextmanager
async def get_bot() -> AsyncGenerator[Bot, None]:
	"""
	Async context manager that creates and yields a bot instance.
	Ensures any future bot cleanup can be handled here.
	"""

	bot = Bot(
		settings.bot_token,
		default=DefaultBotProperties(parse_mode=ParseMode.HTML),
	)
	try:
		yield bot
	finally:
		await bot.session.close()


async def send_msg(db: AsyncSession, num: int, user_id: int):
	"""Send scheduled reminder message to user."""
	text = render_template(num)
	keyboard = InlineKeyboardBuilder()
	keyboard.add(
		InlineKeyboardButton(text="Оплатити 💳", callback_data="pay_reminder")
	)
	keyboard.adjust(1)

	try:
		if num in (1, 2, 3, 4):
			async with get_bot() as bot:
				await bot.send_message(
					user_id,
					text,
					reply_markup=keyboard.as_markup(),
				)
	except TelegramForbiddenError:
		await user_crud.mark_user_blocked(db, user_id)
		logger.info(f"User {user_id} blocked the bot, marked as blocked")


async def check_reminders() -> None:
	"""Check and send scheduled reminders."""
	try:
		async with db_manager.session() as db:
			users = await user_crud.get_users_for_reminder(db)
			for user in users:
				try:
					now_local = datetime.now(ZoneInfo("Europe/Kyiv"))
					elapsed = now_local - user.created_at

					if user.reminders_sent >= settings.reminders_count:
						continue

					next_reminder_index = user.reminders_sent
					required_time = settings.reminders[next_reminder_index]

					if elapsed >= required_time:
						await send_msg(db, next_reminder_index + 1, user.id)
						await user_crud.update_reminders(db, user.id)

				except IndexError:
					continue
				except Exception as e:
					logger.error(
						f"Error processing reminders for user {user.id}: {e}"
					)
					continue
	except Exception as e:
		logger.error(f"Error in check_reminders: {e}")


class Scheduler:
	"""
	Scheduler manager that coordinates alert and promo jobs.
	"""

	def __init__(self):
		self.redis_client = None
		self.scheduler = None
		self._running = False

	async def start(self) -> None:
		"""Start the scheduler."""
		if self._running:
			logger.warning("Scheduler is already running")
			return

		# Create Redis client
		self.redis_client = await redis.from_url(
			settings.redis_url, decode_responses=True
		)

		# Create job stores
		jobstores = {
			"default": RedisJobStore(
				host=settings.redis_host,
				port=settings.redis_port,
				db=settings.redis_db,
			)
		}

		# Create scheduler with Redis job store
		self.scheduler = AsyncIOScheduler(jobstores=jobstores)

		self.scheduler.add_job(
			check_reminders,
			trigger=IntervalTrigger(minutes=1),
			id="check_reminders",
			name="Check and send scheduled reminders",
			replace_existing=True,
		)

		self.scheduler.start()
		self._running = True
		logger.info("Scheduler started")

	async def stop(self) -> None:
		"""Stop the scheduler."""
		if not self._running:
			logger.warning("Scheduler is not running")
			return

		if self.scheduler:
			self.scheduler.shutdown()
		if self.redis_client:
			await self.redis_client.aclose()
		self._running = False
		logger.info("Scheduler stopped")
