from PIL import Image
import pygame

from pathlib import Path
import json

from models import GuideParams


GRID_SIZE = (7, 6)

PERSIST_PATH = (Path('~') / 'PotionMotion' / 'persist.json').expanduser()

CLASSIFICATION = {
	(0, 0.015): 'RED',
	(0.085, 0.087): 'ORANGE',
	(0.140, 0.143): 'YELLOW',
	(0.247, 0.250): 'CLOVER',
	(0.316, 0.322): 'GREEN',
}


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


def classify_hue(hue: float) -> str:
	# hue = [0, 1]

	for (x,y), label in CLASSIFICATION.items():
		if x <= hue <= y:
			return label
	return f'{hue:.3f}'