"""
Admin dialog states for link creation.
"""

from aiogram.fsm.state import State, StatesGroup


class LinkDialogStates(StatesGroup):
	"""Admin link creation dialog states."""

	SELECT_SOURCE = State()
	SELECT_CAMPAIGN = State()
	SELECT_CONTENT = State()
