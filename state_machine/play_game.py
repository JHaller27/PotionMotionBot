import colorsys
import pygame
from PIL import Image, ImageStat, ImageGrab
import mouse
from solver import Solver
import utils
from utils import LOGGER
from time import sleep
import logging

from .state import State
import keyboard
from pygame.event import Event
from models import DataContext
from typing import Self

from config import get_config


class TakeScreenShot(State):
	def handle(self, events: list[Event]) -> Self | None:
		if get_config('DebugPrompts', 'PromptToScreencap', 'enabled'):
			keyboard.wait(get_config('DebugPrompts', 'PromptToScreencap', 'keyname'))

		pil_image = ImageGrab.grab(self._ctx.bbox)
		screencap_surface = utils.pil_image_to_surface(pil_image)

		self._ctx.pil_image = pil_image
		self._ctx.background_surface = screencap_surface

		return ShowImageSplitState(self._ctx)


class ShowImageSplitState(State):
	def __init__(self, ctx: DataContext) -> None:
		super().__init__(ctx)
		self._h_start = 241
		self._h_end = 250

	def handle(self, events: list[Event]) -> Self | None:
		H,S,V = 0,1,2

		pixels2rect_map: dict[tuple[int, int], pygame.Rect] = {}

		# Maps pixel coordinates to classification label - e.g. (125,672) -> 'RED'
		pixels2label_map: dict[tuple[int, int], str] = {}

		# List of top & left pixel values to sort, and use indices as cell index
		top_pixel_values: set[int] = set()
		left_pixel_values: set[int] = set()

		bad_classifications = []
		for cell_rect in self._ctx.guide_params.get_cell_rects():
			pixels2rect_map[cell_rect.topleft] = cell_rect

			top_pixel_values.add(cell_rect.top)
			left_pixel_values.add(cell_rect.left)

			subimg = self._ctx.pil_image.crop((cell_rect.left, cell_rect.top, cell_rect.right, cell_rect.bottom))
			subimg = subimg.convert('HSV')

			source = subimg.split()

			mask = source[H].point(lambda i: i in range(self._h_start, self._h_end) and 255)
			inv_mask = source[H].point(lambda i: 255 - i)

			out = source[S].point(lambda i: 0)
			source[S].paste(out, None, mask)

			out = source[V].point(lambda i: 0)
			source[V].paste(out, None, mask)

			subimg = Image.merge(subimg.mode, source).convert('RGB')

			img_stat = ImageStat.Stat(subimg, mask=inv_mask)
			mean = tuple(map(int, img_stat.mean))
			avg_img = Image.new('RGB', subimg.size, mean)

			sub_surface = utils.pil_image_to_surface(avg_img)
			self._ctx.window.blit(sub_surface, cell_rect)

			mean_hsv = colorsys.rgb_to_hsv(*(x/255 for x in img_stat.mean))
			label_text = utils.classify_hue(mean_hsv[H])
			label_surface = self._ctx.font.render(f'{label_text} ({mean_hsv[H]:.3f})', True, 'black', 'white')
			self._ctx.window.blit(label_surface, cell_rect.topleft)

			pixels2label_map[cell_rect.topleft] = label_text

			if label_text is None:
				bad_classifications.append('%.5f hsv(%.1f, %.1f%%, %.1f%%)' % (mean_hsv[H], mean_hsv[H]*360, mean_hsv[S]*100, mean_hsv[V]*100))

		if len(bad_classifications) in range(*get_config('Logging', 'misclassificationsCountRange')):
			LOGGER.warning('Failed to classify hues:')
			for hue in bad_classifications:
				LOGGER.warning(f'\t{hue}')

		if len(bad_classifications) > get_config('Solver', 'maxAcceptableClassificationFailures'):
			self._ctx.classified_grid = None
		else:
			# Set classifications in context
			self._ctx.classified_grid = []
			self._ctx.cell_rects = []

			top_pixel_values = sorted(top_pixel_values)
			left_pixel_values = sorted(left_pixel_values)
			for px_y in top_pixel_values:
				self._ctx.classified_grid.append([])
				self._ctx.cell_rects.append([])

				for px_x in left_pixel_values:
					px_xy = (px_x, px_y)
					self._ctx.classified_grid[-1].append(pixels2label_map[px_xy])
					self._ctx.cell_rects[-1].append(pixels2rect_map[px_xy])

		return ShowSuggestedMove(self._ctx)


class ShowSuggestedMove(State):
	def __init__(self, ctx: DataContext) -> None:
		super().__init__(ctx)

		self._solver = None
		if self._ctx.classified_grid:
			self._solver = Solver(len(ctx.classified_grid[0]), len(ctx.classified_grid))

	def handle(self, events: list[Event]) -> Self | None:
		if get_config('DebugPrompts', 'PromptToShowDrag', 'enabled'):
			keyboard.wait(get_config('DebugPrompts', 'PromptToShowDrag', 'keyname'))

		xforms = None

		if self._solver:
			xforms = self._solver.find_best_move(self._ctx.classified_grid, 3)

		if xforms is None:
			if get_config('Logging', 'enableMoves'):
				LOGGER.debug('No valid move found')
			return TakeScreenShot(self._ctx)

		if get_config('Logging', 'enableMoves'):
			LOGGER.debug(xforms)
		col_xform, row_xform = xforms

		src_cell = [0, 0]
		dst_cell = [0, 0]

		for x_idx, r_x in enumerate(col_xform):
			for y_idx, r_y in enumerate(row_xform):
				if r_x > 0:
					src_cell[1] = x_idx
					dst_cell[1] = x_idx
					dst_cell[0] = r_x
				if r_y > 0:
					src_cell[0] = y_idx
					dst_cell[0] = y_idx
					dst_cell[1] = r_y

		src_rect = self._ctx.cell_rects[src_cell[0]][src_cell[1]]
		dst_rect = self._ctx.cell_rects[dst_cell[0]][dst_cell[1]]

		pygame.draw.line(self._ctx.background_surface, 'red', src_rect.center, dst_rect.center, 4)
		self._ctx.window.blit(self._ctx.background_surface, self._ctx.background_surface.get_rect())

		if get_config('Mouse', 'enabled'):
			mouse.drag(src_rect.centerx, src_rect.centery, dst_rect.centerx, dst_rect.centery, duration=get_config('Mouse', 'dragDuration'))
			sleep(get_config('Mouse', 'pauseDuration'))

		if not get_config('DebugPrompts', 'PromptAfterDrag', 'enabled'):
			return TakeScreenShot(self._ctx)

		for event in events:
			if event.type == pygame.KEYUP and event.key == get_config('DebugPrompts', 'PromptAfterDrag', 'keycode'):
				return TakeScreenShot(self._ctx)

		return self