from PIL import Image
import pygame

from pathlib import Path
import json
import logging
import sys

from models import GuideParams
from config import get_config


PERSIST_PATH = (Path('~') / 'PotionMotion' / 'persist.json').expanduser()


def _setup_logger():
	formatter = logging.Formatter(get_config('Logging', 'format'))

	log_path = Path(get_config('Logging', 'logPath')).expanduser()
	log_level = getattr(logging, get_config('Logging', 'logLevel').upper())

	log_path.parent.mkdir(exist_ok=True, parents=True)
	
	logger = logging.Logger(None)

	file_handler = logging.FileHandler(log_path, 'w')
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)

	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setLevel(log_level)
	console_handler.setFormatter(formatter)
	logger.addHandler(console_handler)

	print(f'Logging to {log_path.absolute()}')

	return logger


LOGGER = _setup_logger()


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

	for label, (x,y) in get_config('Solver', 'ClassificationTable').items():
		if x <= hue <= y:
			return f'{label}'
	return None
