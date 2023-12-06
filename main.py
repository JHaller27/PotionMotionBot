from PIL import ImageGrab
import pygame

import utils

from models import DataContext
import state_machine as fsm


def main():
	pygame.init()
	pygame.font.init()
	my_font = pygame.font.SysFont('Comic Sans MS', 12)

	info_object = pygame.display.Info()
	window = pygame.display.set_mode((info_object.current_w, info_object.current_h), pygame.FULLSCREEN)

	bbox = (0, 0, info_object.current_w, info_object.current_h)
	pil_image = ImageGrab.grab(bbox)
	screencap_surface = utils.pil_image_to_surface(pil_image)

	clock = pygame.time.Clock()
	init_ctx = DataContext(window, bbox, screencap_surface, utils.load_guide_params(), pil_image, my_font, None, [])
	current_state: fsm.State = fsm.INIT_STATE(init_ctx)

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
