from PIL import Image
import pygame

from pathlib import Path
import json

from models import GuideParams
from config import get_config


PERSIST_PATH = (Path('~') / 'PotionMotion' / 'persist.json').expanduser()


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


def classify_hue(hue: float) -> str | None:
	# hue = [0, 1]

	for label, (x,y) in get_config('Solver', 'Classification').items():
		if x <= hue <= y:
			return f'{label}'
	return None


def log(msg, *config_parts):
	if len(config_parts) == 0 or get_config('Logging', *config_parts):
		print(msg)
