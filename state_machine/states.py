from models import DataContext
from typing import Self
import colorsys
from pygame.event import Event
from PIL import Image, ImageStat

from .state import State
from .set_split_guides import SelectTopLeftState, WaitState
import utils


class SetSplitGuides(State):
	def __init__(self, ctx: DataContext) -> None:
		super().__init__(ctx)
		self._sub_state = SelectTopLeftState(ctx) if ctx.guide_params is None else WaitState(ctx)


	def handle(self, events: list[Event]) -> Self | None:
		next_state = self._sub_state.handle(events)

		if next_state is None:
			return ShowImageSplitState(self._ctx)
		elif next_state == self._sub_state:
			return self

		self._sub_state = next_state
		return self


class ShowImageSplitState(State):
	def __init__(self, ctx: DataContext) -> None:
		super().__init__(ctx)
		self._h_start = 241
		self._h_end = 250

	def handle(self, events: list[Event]) -> Self | None:
		H,S,V = 0,1,2
		for cell_rect in self._ctx.guide_params.get_cell_rects():
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
			label = self._ctx.font.render(utils.classify_hue(mean_hsv[H]), True, 'black', 'white')
			self._ctx.window.blit(label, cell_rect.topleft)

		return self
