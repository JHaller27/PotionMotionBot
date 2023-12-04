from PIL import ImageGrab, Image
import pygame
from pygame.event import Event

from dataclasses import dataclass
from typing import Self, Iterator


GRID_SIZE = (7, 6)


def pil_image_to_surface(pil_image: Image.Image) -> pygame.Surface:
	return pygame.image.fromstring(
		pil_image.tobytes(), pil_image.size, pil_image.mode).convert()


@dataclass
class GuideParams:
	top_left: tuple[int, int]
	size: tuple[int, int]
	color: str

	def get_cell_rects(self) -> Iterator[pygame.Rect]:
		cell_size = (self.size[0] // GRID_SIZE[0], self.size[1] // GRID_SIZE[1])
		for x in range(GRID_SIZE[0]):
			for y in range(GRID_SIZE[1]):
				yield pygame.Rect(cell_size[0] * x + self.top_left[0], cell_size[1] * y + self.top_left[1], cell_size[0], cell_size[1])


def get_grid_guide(size: tuple[int, int], guide_params: GuideParams) -> pygame.Surface:
	surface = pygame.Surface(size, pygame.SRCALPHA, 32)

	for rect in guide_params.get_cell_rects():
		pygame.draw.rect(surface, guide_params.color, rect, width=2)

	return surface


@dataclass
class DataContext:
	window: pygame.Surface
	background_surface: pygame.Surface
	guide_params: GuideParams
	pil_image: Image.Image


class State:
	def __init__(self, ctx: DataContext) -> None:
		self._ctx: DataContext = ctx

	def handle(self, events: list[Event]) -> Self | None:
		raise NotImplementedError


class SelectTopLeftState(State):
	def handle(self, events: list[Event]) -> Self | None:
		self._ctx.guide_params = GuideParams(pygame.mouse.get_pos(), (100, 100), 'red')
		grid_surface = get_grid_guide(self._ctx.window.get_size(), self._ctx.guide_params)

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

		grid_surface = get_grid_guide(self._ctx.window.get_size(), self._ctx.guide_params)

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
		grid_surface = get_grid_guide(self._ctx.window.get_size(), self._ctx.guide_params)

		self._ctx.window.blit(self._ctx.background_surface, self._ctx.background_surface.get_rect())
		self._ctx.window.blit(grid_surface, grid_surface.get_rect())

		for event in events:
			if event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
				return ShowImageSplitState(self._ctx)
			elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
				return SetSizeState(self._ctx)
		return self


class ShowImageSplitState(State):
	def handle(self, events: list[Event]) -> Self | None:
		for cell_rect in self._ctx.guide_params.get_cell_rects():
			subimg = self._ctx.pil_image.crop((cell_rect.left, cell_rect.top, cell_rect.right, cell_rect.bottom))
			sub_surface = pil_image_to_surface(subimg)

			self._ctx.window.blit(sub_surface, cell_rect)

		return self


def main():
	pygame.init()
	info_object = pygame.display.Info()
	window = pygame.display.set_mode((info_object.current_w, info_object.current_h), pygame.FULLSCREEN)

	bbox = (0, 0, info_object.current_w, info_object.current_h)
	pil_image = ImageGrab.grab(bbox)
	screencap_surface = pil_image_to_surface(pil_image)

	clock = pygame.time.Clock()
	current_state = SelectTopLeftState(DataContext(window, screencap_surface, None, pil_image))

	while current_state is not None:
		clock.tick(60)

		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
				current_state = None
				break

		if current_state is None:
			break

		window.fill(0)
		next_state = current_state.handle(events)
		pygame.display.flip()

		if next_state != current_state:
			print(f'Moving to {next_state.__class__.__name__}')
			current_state = next_state


main()
