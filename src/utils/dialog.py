from aiogram.fsm.state import State
from aiogram_dialog import DialogManager


async def next(event, widget, dialog_manager: DialogManager, *_):
	await dialog_manager.next()


async def switch_to(event, widget, dialog_manager: DialogManager, state: State):
	await dialog_manager.switch_to(state)
