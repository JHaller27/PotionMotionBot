from models import DataContext
from pygame.event import Event
from typing import Self


class State:
	def __init__(self, ctx: DataContext) -> None:
		self._ctx: DataContext = ctx

	def handle(self, events: list[Event]) -> Self | None:
		raise NotImplementedError
