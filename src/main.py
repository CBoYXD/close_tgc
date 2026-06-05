import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from redis import asyncio as redis

from src.config import settings
from src.dialogs.promo import promo_dialog
from src.dialogs.super_admin import super_admin_link_dialog
from src.handlers.promo import promo_router
from src.handlers.super_admin import super_admin_router
from src.services.scheduler import Scheduler


async def create_redis_storage() -> RedisStorage:
	"""Create and return Redis storage for FSM."""
	redis_client = await redis.from_url(
		settings.redis_url,
		encoding="utf-8",
		decode_responses=True,
	)
	key_builder = DefaultKeyBuilder(with_destiny=True)
	return RedisStorage(redis_client, key_builder=key_builder)


async def main():
	try:
		logging.basicConfig(level=logging.INFO, stream=sys.stdout)
		redis_storage = await create_redis_storage()
		bot = Bot(
			settings.bot_token,
			default=DefaultBotProperties(parse_mode=ParseMode.HTML),
		)
		dp = Dispatcher(storage=redis_storage)

		super_admin_router.include_router(super_admin_link_dialog)
		dp.include_router(super_admin_router)

		promo_router.include_router(promo_dialog)
		dp.include_router(promo_router)

		dp.workflow_data["bot"] = bot

		async def on_startup() -> None:
			# Start the scheduler
			scheduler = Scheduler()
			dp.workflow_data["scheduler"] = scheduler
			await scheduler.start()

		async def on_shutdown() -> None:
			"""Actions performed at bot shutdown."""
			# Stop the scheduler
			if "scheduler" in dp.workflow_data:
				await dp.workflow_data["scheduler"].stop()

		dp.startup.register(on_startup)
		dp.shutdown.register(on_shutdown)

		# Setup dialogs (must be called after registering all dialogs)
		setup_dialogs(dp)

		await bot.delete_webhook(drop_pending_updates=True)
		await dp.start_polling(bot)
	except (KeyboardInterrupt, SystemExit):
		logging.warning("Bot stopped!")
		await dp.fsm.storage.close()


if __name__ == "__main__":
	asyncio.run(main())
