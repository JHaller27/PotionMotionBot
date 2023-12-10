import pygame
from PIL import Image
from dataclasses import dataclass
from typing import Iterator

from config import get_config


@dataclass
class GuideParams:
	top_left: tuple[int, int]
	size: tuple[int, int]
	color: str

	def get_cell_rects(self) -> Iterator[pygame.Rect]:
		grid_size = get_config('Solver', 'gridSize')
		cell_size = (self.size[0] // grid_size[0], self.size[1] // grid_size[1])
		for x in range(grid_size[0]):
			for y in range(grid_size[1]):
				yield pygame.Rect(cell_size[0] * x + self.top_left[0], cell_size[1] * y + self.top_left[1], cell_size[0], cell_size[1])


@dataclass
class DataContext:
	window: pygame.Surface
	bbox: tuple[int, int, int, int]
	background_surface: pygame.Surface
	guide_params: GuideParams
	pil_image: Image.Image
	font: pygame.font.Font
	classified_grid: list[list] | None
	cell_rects: list[list[pygame.Rect]]
