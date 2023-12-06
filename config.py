import pygame


ENABLE_MOUSE: bool = True
PROMPT_AFTER_DRAG: int | None = None and pygame.K_RETURN
PROMPT_AFTER_SHOW_DRAG: int | None = None and pygame.K_RETURN
PROMPT_TO_SCREENCAP: str | None = None and 'x'
ESCAPE_FROM_PLAY_KEY: str | None = None or 'ESCAPE'

GRID_SIZE = (7, 6)
CLASSIFICATION = {
	(0.000, 0.015): 'RED',
	(0.074, 0.084): 'BROWN',
	(0.085, 0.087): 'ORANGE',
	(0.140, 0.143): 'YELLOW',
	(0.247, 0.250): 'CLOVER',
	(0.315, 0.322): 'GREEN',
	(0.467, 0.470): 'AQUA',
	(0.578, 0.580): 'BLUE',
	(0.748, 0.752): 'PURPLE',
	(0.869, 0.871): 'PINK',
}