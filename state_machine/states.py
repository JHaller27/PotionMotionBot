from models import DataContext
from typing import Self
from pygame.event import Event

import keyboard
from threading import Event as ThEvent

from .state import State
from .set_split_guides import SelectTopLeftState, WaitState
from .play_game import ShowImageSplitState

import config


class SetSplitGuides(State):
	def __init__(self, ctx: DataContext) -> None:
		super().__init__(ctx)
		self._sub_state = SelectTopLeftState(ctx) if ctx.guide_params is None else WaitState(ctx)


	def handle(self, events: list[Event]) -> Self | None:
		next_state = self._sub_state.handle(events)

		if next_state is None:
			return PlayGame(self._ctx)

		if next_state != self._sub_state:
			self._sub_state = next_state
		return self


class PlayGame(State):
	def __init__(self, ctx: DataContext) -> None:
		super().__init__(ctx)
		self._sub_state = ShowImageSplitState(ctx)

		if config.ESCAPE_FROM_PLAY_KEY:
			keyboard.add_hotkey(config.ESCAPE_FROM_PLAY_KEY, self._break_loop, suppress=True)
			self._t_event = ThEvent()

	def _break_loop(self):
		print('Break loop')
		self._t_event.set()

	def handle(self, events: list[Event]) -> Self | None:
		if config.ESCAPE_FROM_PLAY_KEY and self._t_event.is_set():
			return None

		next_state = self._sub_state.handle(events)

		if next_state is None:
			if config.ESCAPE_FROM_PLAY_KEY:
				keyboard.remove_hotkey('ESCAPE')
			return None

		if next_state != self._sub_state:
			self._sub_state = next_state
		return self
