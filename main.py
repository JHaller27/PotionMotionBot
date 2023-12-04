from PIL import ImageGrab, Image
import pygame
from pygame.event import Event

from dataclasses import dataclass
from typing import Self, Iterator
from pathlib import Path
import json


PERSIST_PATH = (Path('~') / 'PotionMotion' / 'persist.json').expanduser()


GRID_SIZE = (7, 6)


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


@dataclass
class DataContext:
	window: pygame.Surface
	background_surface: pygame.Surface
	guide_params: GuideParams
	pil_image: Image.Image


def pil_image_to_surface(pil_image: Image.Image) -> pygame.Surface:
	return pygame.image.fromstring(
		pil_image.tobytes(), pil_image.size, pil_image.mode).convert()


def load_guide_params() -> GuideParams | None:
	if not PERSIST_PATH.is_file():
		return None
	with PERSIST_PATH.open() as fp:
		obj: dict = json.load(fp)
	return GuideParams(tuple(obj.get('top_left')), tuple(obj.get('size')), obj.get('color'))


def save_guide_params(guide_params: GuideParams):
	PERSIST_PATH.parent.mkdir(parents=True, exist_ok=True)
	with PERSIST_PATH.open('w') as fp:
		json.dump({
			'top_left': list(guide_params.top_left),
			'size': list(guide_params.size),
			'color': guide_params.color,
		}, fp)


def get_grid_guide(size: tuple[int, int], guide_params: GuideParams) -> pygame.Surface:
	surface = pygame.Surface(size, pygame.SRCALPHA, 32)

	for rect in guide_params.get_cell_rects():
		pygame.draw.rect(surface, guide_params.color, rect, width=2)

	return surface


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
		save_guide_params(self._ctx.guide_params)

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
	def __init__(self, ctx: DataContext) -> None:
		super().__init__(ctx)
		self._h_start = 241
		self._h_end = 250

	def handle(self, events: list[Event]) -> Self | None:
		for event in events:
			if event.type == pygame.KEYUP and event.key == pygame.K_UP:
				self._h_start += 1
			elif event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
				self._h_start -= 1
			if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
				self._h_end += 1
			elif event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
				self._h_end -= 1

		print(self._h_start, self._h_end)

		H,S,V = 0,1,2
		for cell_rect in self._ctx.guide_params.get_cell_rects():
			subimg = self._ctx.pil_image.crop((cell_rect.left, cell_rect.top, cell_rect.right, cell_rect.bottom))
			subimg = subimg.convert('HSV')

			source = subimg.split()

			mask = source[H].point(lambda i: i in range(self._h_start, self._h_end) and 255)

			out = source[S].point(lambda i: 0)
			source[S].paste(out, None, mask)

			out = source[V].point(lambda i: 0)
			source[V].paste(out, None, mask)

			subimg = Image.merge(subimg.mode, source).convert('RGB')

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
	init_ctx = DataContext(window, screencap_surface, load_guide_params(), pil_image)
	current_state = SelectTopLeftState(init_ctx) if init_ctx.guide_params is None else WaitState(init_ctx)

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
