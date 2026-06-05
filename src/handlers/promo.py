from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode

from src.database.crud.payment import payment_crud
from src.database.crud.user import user_crud
from src.database.enums.payment import PaymentStatus
from src.database.schemas.user import UserCreate
from src.database.setup import db_manager
from src.states.promo import PromoStates

promo_router = Router()

def parse_utm_args(args: str) -> dict:
    """Parse UTM parameters from start command."""
    start_param = args.split("&")
    if start_param:
        # Parse query string format: utm_source=telegram&utm_campaign=ads
        return {
            "utm_source": start_param[0],
            "utm_campaign": start_param[1],
            "utm_content": start_param[2],
        }
    return {}


@promo_router.message(CommandStart(deep_link=True, deep_link_encoded=True))
async def cmd_start(message: Message, dialog_manager: DialogManager, command: CommandObject):
	utm_params = parse_utm_args(command.args)
	async with db_manager.session() as db:
		user = await user_crud.get_by_id(db, message.from_user.id)
		if not user:
			user = await user_crud.create(
				db,
				UserCreate(
					id=message.from_user.id,
					username=message.from_user.username,
					full_name=message.from_user.full_name,
                	**utm_params,
				),
			)
		if user.blocked_the_bot:
			await user_crud.mark_user_blocked(db, user.id, blocked=False)
			await message.answer("Раді бачити вас знову! 🤝")

		payment = await payment_crud.get_by_user_id(db, message.from_user.id)
		if payment and payment.status != PaymentStatus.COMPLETED:
			await dialog_manager.start(
				PromoStates.PAYMENT_WAIT, mode=StartMode.RESET_STACK
			)
			return
	await dialog_manager.start(PromoStates.START, mode=StartMode.RESET_STACK)


@promo_router.message(CommandStart())
async def cmd_start_without_params(message: Message, dialog_manager: DialogManager):
	async with db_manager.session() as db:
		user = await user_crud.get_by_id(db, message.from_user.id)
		if not user:
			user = await user_crud.create(
				db,
				UserCreate(
					id=message.from_user.id,
					username=message.from_user.username,
					full_name=message.from_user.full_name,
				),
			)
		if user.blocked_the_bot:
			await user_crud.mark_user_blocked(db, user.id, blocked=False)
			await message.answer("Раді бачити вас знову! 🤝")

		payment = await payment_crud.get_by_user_id(db, message.from_user.id)
		if payment and payment.status != PaymentStatus.COMPLETED:
			await dialog_manager.start(
				PromoStates.PAYMENT_WAIT, mode=StartMode.RESET_STACK
			)
			return
	await dialog_manager.start(PromoStates.START, mode=StartMode.RESET_STACK)


@promo_router.callback_query(F.data == "pay_reminder")
async def reminder_payment_handler(
	callback: CallbackQuery, dialog_manager: DialogManager
):
	await dialog_manager.start(
		PromoStates.PAYMENT_WAIT, mode=StartMode.RESET_STACK
	)
