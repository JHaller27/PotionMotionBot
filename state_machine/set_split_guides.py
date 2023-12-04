from models import GuideParams
import pygame
from pygame.event import Event
from typing import Self

from .state import State
import utils


class SelectTopLeftState(State):
	def handle(self, events: list[Event]) -> Self | None:
		self._ctx.guide_params = GuideParams(pygame.mouse.get_pos(), (100, 100), 'red')
		grid_surface = utils.get_grid_guide(self._ctx.window.get_size(), self._ctx.guide_params)

		self._ctx.window.blit(self._ctx.background_surface, self._ctx.background_surface.get_rect())
		self._ctx.window.blit(grid_surface, grid_surface.get_rect())

		for event in events:
			if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				return SetSizeState(self._ctx)

		return self


class SetSizeState(State):
	def handle(self, events: list[Event]) -> Self | None:
		mouse_pos = pygame.mouse.get_pos()
		size = (mouse_pos[0] - self._ctx.guide_params.top_left[0], mouse_pos[1] - self._ctx.guide_params.top_left[1])

		self._ctx.guide_params = GuideParams(self._ctx.guide_params.top_left, size, 'blue')

		grid_surface = utils.get_grid_guide(self._ctx.window.get_size(), self._ctx.guide_params)

		self._ctx.window.blit(self._ctx.background_surface, self._ctx.background_surface.get_rect())
		self._ctx.window.blit(grid_surface, grid_surface.get_rect())

		for event in events:
			if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				return WaitState(self._ctx)
			elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
				return SelectTopLeftState(self._ctx)

		return self


class WaitState(State):
	def handle(self, events: list[Event]) -> Self | None:
		utils.save_guide_params(self._ctx.guide_params)

		grid_surface = utils.get_grid_guide(self._ctx.window.get_size(), self._ctx.guide_params)

		self._ctx.window.blit(self._ctx.background_surface, self._ctx.background_surface.get_rect())
		self._ctx.window.blit(grid_surface, grid_surface.get_rect())

		for event in events:
			if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
				return None
			elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
				return SetSizeState(self._ctx)
		return self
