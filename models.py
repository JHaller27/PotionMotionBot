import pygame
from PIL import Image
from dataclasses import dataclass
from typing import Iterator

import utils


@dataclass
class GuideParams:
	top_left: tuple[int, int]
	size: tuple[int, int]
	color: str

	def get_cell_rects(self) -> Iterator[pygame.Rect]:
		cell_size = (self.size[0] // utils.GRID_SIZE[0], self.size[1] // utils.GRID_SIZE[1])
		for x in range(utils.GRID_SIZE[0]):
			for y in range(utils.GRID_SIZE[1]):
				yield pygame.Rect(cell_size[0] * x + self.top_left[0], cell_size[1] * y + self.top_left[1], cell_size[0], cell_size[1])


@dataclass
class DataContext:
	window: pygame.Surface
	background_surface: pygame.Surface
	guide_params: GuideParams
	pil_image: Image.Image
	font: pygame.font.Font
	classified_grid: list[list]
	cell_rects: list[list[pygame.Rect]]
