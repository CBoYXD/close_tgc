from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from src.database.crud.user import user_crud
from src.database.setup import db_manager
from src.filters.admin import AdminFilter
from src.logger_config import get_logger
from src.states.super_admin import LinkDialogStates
from src.templates import render_template

logger = get_logger("super_admin_handler")

super_admin_router = Router()
super_admin_router.message.filter(AdminFilter(super_admin=True))


@super_admin_router.message(CommandStart())
async def super_admin_start_handler(message: Message):
	"""
	Handler for the /start command, available only to admins.
	"""
	user_name = message.from_user.full_name
	text = render_template("admin_start", user_name=user_name)
	await message.answer(text, parse_mode="HTML")


@super_admin_router.message(Command("panel"))
async def super_admin_panel_command(message: Message):
	"""Handler for the /panel admin command."""
	text = render_template("admin_panel")
	await message.answer(text, parse_mode="HTML")


@super_admin_router.message(Command("stats"))
async def super_admin_stats_command(message: Message):
	"""Show overall statistics."""
	try:
		async with db_manager.session() as db:
			# Get user statistics
			all_users = await user_crud.get_all(db)
			connected_users = await user_crud.get_connected_users(db)
			blocked_count = await user_crud.get_blocked_users_count(db)

			# Calculate conversion rates
			total_users = len(all_users)
			connected_count = len(connected_users)
			conversion_rate = round(
				(connected_count / total_users * 100) if total_users > 0 else 0,
				1,
			)

			# Group by UTM source
			utm_sources = {}
			for user in all_users:
				if user.utm_source:
					if user.utm_source not in utm_sources:
						utm_sources[user.utm_source] = {
							"total": 0,
							"connected": 0,
						}
					utm_sources[user.utm_source]["total"] += 1
					if user.is_connected:
						utm_sources[user.utm_source]["connected"] += 1

			# Format UTM sources text
			utm_sources_text = ""
			for source, stats in utm_sources.items():
				source_rate = round(
					(stats["connected"] / stats["total"] * 100)
					if stats["total"] > 0
					else 0,
					1,
				)
				utm_sources_text += (
					f"• {source}: {stats['connected']}/{stats['total']} "
					f"({source_rate:.1f}%)\n"
				)

			text = render_template(
				"admin_stats",
				total_users=total_users,
				connected_count=connected_count,
				conversion_rate=conversion_rate,
				utm_sources_text=utm_sources_text,
				last_update=message.date.strftime("%d.%m.%Y %H:%M"),
				blocked_count=blocked_count,
			)

			await message.answer(text, parse_mode="HTML")

	except Exception as e:
		logger.error(f"Error getting stats: {e}")
		text = render_template("error_stats")
		await message.answer(text)


@super_admin_router.message(Command("utm"))
async def super_admin_utm_command(message: Message):
	"""Show UTM analytics."""
	try:
		async with db_manager.session() as db:
			utm_stats = await user_crud.get_conversion_stats(db)

			if not utm_stats:
				text = render_template("no_utm_data")
				await message.answer(text)
				return

			# Get detailed analytics by source
			analytics = await user_crud.get_utm_analytics(db)
			text = render_template(
       			"admin_utm", 
          		utm_stats=utm_stats, 
            	analytics=analytics
            )
			await message.answer(text, parse_mode="HTML")

	except Exception as e:
		logger.error(f"Error getting UTM stats: {e}")
		text = render_template("error_utm")
		await message.answer(text)


@super_admin_router.message(Command("user"))
async def super_admin_user_command(message: Message):
	"""Show user management options."""
	try:
		async with db_manager.session() as db:
			all_users = await user_crud.get_all(db)
			connected_users = await user_crud.get_connected_users(db)
			blocked_count = await user_crud.get_blocked_users_count(db)

			text = render_template(
				"admin_users",
				total_users=len(all_users),
				connected_users=len(connected_users),
				not_connected_users=len(all_users) - len(connected_users),
				blocked_count=blocked_count,
			)
			await message.answer(text, parse_mode="HTML")

	except Exception as e:
		logger.error(f"Error getting user info: {e}")
		text = render_template("error_users")
		await message.answer(text)


@super_admin_router.message(Command("create_link"))
async def super_admin_create_link_command(
	message: Message, dialog_manager: DialogManager
):
	"""Start link creation dialog."""
	await dialog_manager.start(
		LinkDialogStates.SELECT_SOURCE, mode=StartMode.RESET_STACK
	)
