"""
Main promo dialogs using aiogram dialog.
"""

from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Url
from aiogram_dialog.widgets.text import Const, Format

from src.config import settings
from src.database.crud.payment import payment_crud
from src.database.crud.user import user_crud
from src.database.enums.payment import PaymentStatus
from src.database.setup import db_manager
from src.services.payment import payment_service
from src.states.promo import PromoStates
from src.templates import render_template


async def get_payment_link(dialog_manager: DialogManager, **kwargs):
	"""Get payment link."""

	user_id = dialog_manager.event.from_user.id
	async with db_manager.session() as db:
		payment = await payment_crud.get_by_user_id(db, user_id)

	link = (
		await payment_service.create_invoice(user_id)
		if not payment
		else payment.pay_url
	)
	return {"link": link}


async def check_if_paid(
	c: CallbackQuery,
	button: Button,
	dialog_manager: DialogManager,
):
	"""Check if user has already paid."""
	user_id = dialog_manager.event.from_user.id
	async with db_manager.session() as db:
		payment = await payment_crud.get_by_user_id(db, user_id)
	if payment and payment.status == PaymentStatus.COMPLETED:
		await dialog_manager.done()
		bot: Bot = dialog_manager.middleware_data["bot"]
		await bot.send_message(user_id, "Ви вже оплатили доступ.")


async def check_payment_handler(
	c: CallbackQuery,
	button: Button,
	dialog_manager: DialogManager,
):
	"""Handle payment check."""
	async with db_manager.session() as db:
		payment = await payment_crud.get_by_user_id(db, c.from_user.id)

	if await payment_service.check_payment(payment.id):
		await dialog_manager.done()
		bot: Bot = dialog_manager.middleware_data["bot"]
		invite_link = await bot.create_chat_invite_link(
			chat_id=settings.closed_channel_id, member_limit=1
		)
		await bot.send_message(
			c.from_user.id,
			render_template(
				"payment_success",
				link=invite_link.invite_link,
			),
		)
		async with db_manager.session() as db:
			await user_crud.mark_connected(db, c.from_user.id)
	else:
		await c.answer(render_template("payment_failed"))


promo_dialog = Dialog(
	Window(
		Const(render_template("start")),
		SwitchTo(
			Const("✅ Оплатити доступ"),
			id="start_flow",
			state=PromoStates.PAYMENT_WAIT,
			on_click=check_if_paid,
		),
		SwitchTo(
			Const("ℹ️ Інформація про канал"),
			id="info_flow",
			state=PromoStates.INFO,
		),
		SwitchTo(
			Const("❓ Як почати?"),
			id="how_to_start_flow",
			state=PromoStates.HOW_TO_START,
		),
		SwitchTo(
			Const("📚 FAQ"),
			id="faq_flow",
			state=PromoStates.FAQ,
		),
		Url(
			Const("Поставити питання"),
			url=Const("https://t.me/CBoYXD"),
		),
		state=PromoStates.START,
	),
	Window(
		Const(render_template("info")),
		SwitchTo(
			Const("Оплатити доступ ✅"),
			id="info_to_payment",
			state=PromoStates.PAYMENT_WAIT,
			on_click=check_if_paid,
		),
		SwitchTo(
			Const("⬅️ Назад"),
			id="info_to_start",
			state=PromoStates.START,
		),
		state=PromoStates.INFO,
	),
	Window(
		Const(render_template("how_to_start")),
		SwitchTo(
			Const("Оплатити доступ ✅"),
			id="info_to_payment",
			state=PromoStates.PAYMENT_WAIT,
			on_click=check_if_paid,
		),
		SwitchTo(
			Const("⬅️ Назад"),
			id="how_to_start_to_start",
			state=PromoStates.START,
		),
		state=PromoStates.HOW_TO_START,
	),
	Window(
		Const(render_template("faq")),
		SwitchTo(
			Const("Оплатити доступ ✅"),
			id="info_to_payment",
			state=PromoStates.PAYMENT_WAIT,
			on_click=check_if_paid,
		),
		SwitchTo(
			Const("⬅️ Назад"),
			id="how_to_start_to_start",
			state=PromoStates.START,
		),
		state=PromoStates.FAQ,
	),
	Window(
		Const(render_template("payment_wait", price=settings.pay_amount)),
		Url(
			Const("Оплатити 💳"),
			url=Format("{link}"),
		),
		Button(
			Const("Я оплатив"),
			id="check_payment",
			on_click=check_payment_handler,
		),
		SwitchTo(
			Const("⬅️ Назад"),
			id="payment_to_start",
			state=PromoStates.START,
		),
		state=PromoStates.PAYMENT_WAIT,
		getter=get_payment_link,
	),
)
