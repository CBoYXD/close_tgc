from aiogram.fsm.state import State, StatesGroup


class PromoStates(StatesGroup):
	START = State()
	INFO = State()
	HOW_TO_START = State()
	FAQ = State()
	ASK_QUESTION = State()
	PAYMENT_WAIT = State()
	PAYMENT_CONFIRM = State()
