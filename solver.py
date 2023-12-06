from dataclasses import dataclass


T_COORD = tuple[int, int]
T_XFORM = tuple[int, ...]


@dataclass
class BoardEdges:
	col_xforms: T_XFORM
	row_xforms: T_XFORM
	edges: list[tuple[T_COORD, T_COORD]]


def generate_edges(w: int, h: int, col_xforms: T_XFORM, row_xforms: T_XFORM) -> BoardEdges:
	edges = []

	for y in range(h):
		for x in range(w):
			# Right edge
			# If this row is xformed
			if row_xforms[y] != 0:
				if x == w-1:
					edges.append(((y,x), (y, 0)))
				elif x == w-row_xforms[y]-1:
					pass
				else:
					edges.append(((y,x), (y, x+1)))
			elif x != w-1:
				# If next col is xformed
				if col_xforms[x+1] != 0:
					y_off = col_xforms[x+1]
					edges.append(((y,x), ((y-y_off)%h, x+1)))
				# If this col is xformed
				elif col_xforms[x] != 0:
					y_off = col_xforms[x]
					edges.append(((y,x), ((y+y_off)%h, x+1)))
				else:
					edges.append(((y,x), (y, x+1)))

			# Down edge
			# If this col is xformed
			if col_xforms[x] != 0:
				if y == h-1:
					edges.append(((y,x), (0, x)))
				elif y == h-col_xforms[x]-1:
					pass
				else:
					edges.append(((y,x), (y+1, x)))
			elif y != h-1:
				# If next row is xformed
				if row_xforms[y+1] != 0:
					x_off = row_xforms[y+1]
					edges.append(((y,x), (y+1, (x-x_off)%w)))
				# If this row is xformed
				elif row_xforms[y] != 0:
					x_off = row_xforms[y]
					edges.append(((y,x), (y+1, (x+x_off)%w)))
				else:
					edges.append(((y,x), (y+1, x)))

	return BoardEdges(col_xforms, row_xforms, edges)


def _score(board: list[list], board_edges: BoardEdges, min_valid_score: int) -> int:
	neighborhoods: dict[T_COORD, set[T_COORD]] = {}
	representatives: dict[T_COORD, T_COORD] = {}

	for edges in board_edges.edges:
		src, dst = edges
		src_y, src_x = src
		dst_y, dst_x = dst

		if board[src_y][src_x] != board[dst_y][dst_x]:
			continue

		rep = None

		if src in representatives:
			rep = representatives[src]
			if dst in representatives:
				representatives.pop(dst)
		elif dst in representatives:
			rep = representatives[dst]
		else:
			rep = representatives[dst] = representatives[src] = src

		if rep not in neighborhoods:
			neighborhoods[rep] = set()

		neighborhoods[rep].add(src)
		neighborhoods[rep].add(dst)

	if len(neighborhoods) == 0:
		return 0

	return sum(len(n) for n in neighborhoods.values() if len(n) >= min_valid_score)


class Solver:
	def __init__(self, w: int, h: int) -> None:
		self._all_edges: list[BoardEdges] = []

		no_col_xform = (0,) * w
		no_row_xform = (0,) * h

		for col in range(w):
			for r in range(1, h):
				xforms = [0] * w
				xforms[col] = r
				xforms = tuple(xforms)
				edges = generate_edges(w, h, xforms, no_row_xform)
				self._all_edges.append(edges)

		for row in range(h):
			for r in range(1, w):
				xforms = [0] * h
				xforms[row] = r
				xforms = tuple(xforms)
				edges = generate_edges(w, h, no_col_xform, xforms)
				self._all_edges.append(edges)

	def find_first_move(self, board: list[list], min_score: int) -> tuple[T_XFORM, T_XFORM] | None:
		for move in self._all_edges:
			score = _score(board, move, min_score)
			if score >= min_score:
				return (move.col_xforms, move.row_xforms)

	def find_best_move(self, board: list[list], min_score: int) -> tuple[T_XFORM, T_XFORM] | None:
		move_map: dict[tuple[T_XFORM, T_XFORM], int] = {}
		for board_edges in self._all_edges:
			score = _score(board, board_edges, min_score)
			if score >= min_score:
				move = (board_edges.col_xforms, board_edges.row_xforms)
				move_map[move] = score

		if len(move_map) == 0:
			return None

		return max(move_map.items(), key=lambda kvp: kvp[1])[0]


if __name__ == '__main__':
	board = [
		list('RRab'),
		list('fgRR'),
	]
	size = (len(board[0]), len(board))
	solver = Solver(size[0], size[1])
	move = solver.find_best_move(board, 3)
	print(move)
