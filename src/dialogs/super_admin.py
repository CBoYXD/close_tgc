"""
Admin dialogs for link creation using aiogram dialog.
"""

from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Const

from src.logger_config import get_logger
from src.states.super_admin import LinkDialogStates
from src.templates import render_template
from src.utils.dialog import next

logger = get_logger("super_admin_dialog")


async def process_output(event, widget, dialog_manager: DialogManager, *_):
	bot: Bot = dialog_manager.middleware_data["bot"]
	try:
		source = dialog_manager.find("source_input").get_value()
		campaign = dialog_manager.find("campaign_input").get_value()
		content = dialog_manager.find("content_input").get_value()
		payload = "&".join([source, campaign, content])
		start_link = await create_start_link(bot, payload, encode=True)
		text = render_template(
			"admin_link",
			start_link=start_link,
			source=source,
			campaign=campaign,
			content=content,
		)
		await bot.send_message(dialog_manager.event.from_user.id, text)
	except Exception as e:
		logger.error(f"Error creating referral link: {e}")
		text = render_template("admin_link_error")
		await bot.send_message(dialog_manager.event.from_user.id, text)

	await dialog_manager.done()


# Create and register admin link dialog
super_admin_link_dialog = Dialog(
	Window(
		Const("Введіть джерело трафіку (source):"),
		TextInput(id="source_input", on_success=next),
		state=LinkDialogStates.SELECT_SOURCE,
	),
	Window(
		Const("Введіть назву кампанії (campaign):"),
		TextInput(id="campaign_input", on_success=next),
		state=LinkDialogStates.SELECT_CAMPAIGN,
	),
	Window(
		Const("Введіть тип контенту (content):"),
		TextInput(id="content_input", on_success=process_output),
		state=LinkDialogStates.SELECT_CONTENT,
	),
)
