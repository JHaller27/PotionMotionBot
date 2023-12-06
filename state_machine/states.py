from models import DataContext
from typing import Self
from pygame.event import Event

import keyboard
from threading import Event as ThEvent

from .state import State
from .set_split_guides import SelectTopLeftState, WaitState
from .play_game import ShowImageSplitState

from config import get_config


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

		if get_config('DebugPrompts', 'EscapeFromPlay', 'enabled'):
			keyboard.add_hotkey(get_config('DebugPrompts', 'EscapeFromPlay', 'keyname'), self._break_loop, suppress=True)
			self._t_event = ThEvent()

	def _break_loop(self):
		print('Break loop')
		self._t_event.set()

	def handle(self, events: list[Event]) -> Self | None:
		if self._t_event is not None and self._t_event.is_set():
			return None

		next_state = self._sub_state.handle(events)

		if next_state is None:
			if get_config('DebugPrompts', 'EscapeFromPlay', 'enabled'):
				keyboard.remove_hotkey(get_config('DebugPrompts', 'EscapeFromPlay', 'keyname'))
			return None

		if next_state != self._sub_state:
			self._sub_state = next_state
		return self
