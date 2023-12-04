from PIL import ImageGrab, Image
import pygame

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
				rect = (cell_size[0] * x + self.top_left[0], cell_size[1] * y + self.top_left[1])
				rect = (rect[0], rect[1], cell_size[0], cell_size[1])
				yield rect


class State:
	def get_guide_params(self) -> GuideParams:
		raise NotImplementedError

	def get_next_state(self, event: pygame.event.Event) -> Self | None:
		raise NotImplementedError


class SelectTopLeftState(State):
	def __init__(self) -> None:
		self._current_guide_params = None

	def get_guide_params(self) -> GuideParams:
		self._current_guide_params = GuideParams(pygame.mouse.get_pos(), (100, 100), 'red')
		return self._current_guide_params

	def get_next_state(self, event: pygame.event.Event) -> Self | None:
		if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
			return SetSizeState(self._current_guide_params)
		return self


class SetSizeState(State):
	def __init__(self, guide_params: GuideParams) -> None:
		self._prev_params = guide_params
		self._current_guide_params = None

	def get_guide_params(self) -> GuideParams:
		mouse_pos = pygame.mouse.get_pos()
		size = (mouse_pos[0] - self._prev_params.top_left[0], mouse_pos[1] - self._prev_params.top_left[1])

		self._current_guide_params = GuideParams(self._prev_params.top_left, size, 'blue')
		return self._current_guide_params

	def get_next_state(self, event: pygame.event.Event) -> Self | None:
		if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
			return WaitState(self._current_guide_params)
		elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
			return SelectTopLeftState()
		return self


class WaitState(State):
	def __init__(self, guide_params: GuideParams) -> None:
		self._prev_params = guide_params

	def get_guide_params(self) -> GuideParams:
		return self._prev_params

	def get_next_state(self, event: pygame.event.Event) -> Self | None:
		if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
			return SetSizeState(self._prev_params)
		return self


def get_grid_guide(size: tuple[int, int], guide_params: GuideParams) -> pygame.Surface:
	surface = pygame.Surface(size, pygame.SRCALPHA, 32)

	for rect in guide_params.get_cell_rects():
		pygame.draw.rect(surface, guide_params.color, rect, width=2)

	return surface


def main():
	pygame.init()
	info_object = pygame.display.Info()
	window = pygame.display.set_mode((info_object.current_w, info_object.current_h), pygame.FULLSCREEN)

	bbox = (0, 0, info_object.current_w, info_object.current_h)
	pil_image = ImageGrab.grab(bbox)
	screencap_surface = pil_image_to_surface(pil_image)

	clock = pygame.time.Clock()
	current_state = SelectTopLeftState()

	while current_state is not None:
		clock.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
				next_state = None
				break
			else:
				next_state = current_state.get_next_state(event)
				if next_state is None:
					break

		if next_state is None:
			break

		guide_params = current_state.get_guide_params()
		grid_surface = get_grid_guide((info_object.current_w, info_object.current_h), guide_params)

		window.fill(0)
		window.blit(screencap_surface, screencap_surface.get_rect())
		window.blit(grid_surface, grid_surface.get_rect())

		pygame.display.flip()

		if next_state != current_state:
			print(f'Moving to {next_state.__class__.__name__}')
			current_state = next_state


main()
