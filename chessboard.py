from draught import Draught, ColorType
from typing import NamedTuple, List

Pos = NamedTuple("Pos", (('x', int), ('y', int)))


def get_dirs(start: Pos, finish: Pos) -> Pos:
    dir_x = finish[0] - start[0]
    dir_x //= abs(dir_x)
    dir_y = finish[1] - start[1]
    dir_y //= abs(dir_y)
    return dir_x, dir_y


def is_valid_position(pos: Pos, board_size: int) -> bool:
    return 0 <= pos[0] < board_size and 0 <= pos[1] < board_size


class ChessBoard:
    def __init__(self, size=8, rows_filled=3):
        self.field = []
        for row in range(size):
            self.field.append([])
            for column in range(size):
                if row < rows_filled and (row + column) % 2 == 1:
                    self.field[-1].append(Draught(is_white=False))
                elif row >= size - rows_filled and (row + column) % 2 == 1:
                    self.field[-1].append(Draught(is_white=True))
                else:
                    self.field[-1].append(None)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.field[key]
        else:
            return self.field[key[0]][key[1]]

    def __setitem__(self, index, value):
        self.field[index[0]][index[1]] = value

    def __len__(self):
        return len(self.field)

    def enemies_on_the_way(self, start: Pos, finish: Pos) -> int:
        dr = self[start]

        dir_x, dir_y = get_dirs(start, finish)
        pos = list(start)
        enemies = 0
        while pos != list(finish):
            pos[0] += dir_x
            pos[1] += dir_y
            if self[pos] is not None:
                if self[pos].color_type == dr.color_type:
                    return -1
                else:
                    enemies += 1
        return enemies

    def eats_one_enemy(self, start: Pos, finish: Pos) -> bool:
        if abs(finish[0] - start[0]) != abs(finish[1] - start[1]):
            return False
        if self[finish] is not None:
            return False
        return self.enemies_on_the_way(start, finish) == 1

    def is_valid_step(self, start: Pos, finish: Pos) -> bool:
        dr = self[start]

        if self[finish] is not None:
            return False
        if abs(start[0] - finish[0]) != abs(start[1] - finish[1]):
            return False
        if not dr.is_king:
            if abs(start[0] - finish[0]) > 2:
                return False
            if abs(start[0] - finish[0]) == 2:
                return self.eats_one_enemy(start, finish)
            if dr.color_type == ColorType.WHITE:
                if start[0] <= finish[0]:
                    return False
            if dr.color_type == ColorType.BLACK:
                if start[0] >= finish[0]:
                    return False
            if abs(start[0] - finish[0]) == 1:
                return True
            return False
        else:
            return self.eats_one_enemy(start, finish) or \
                   self.enemies_on_the_way(start, finish) == 0

    def is_valid_eating_step(self, start: Pos, finish: Pos) -> bool:
        return self.is_valid_step(start, finish) & self.eats_one_enemy(start, finish)

    def get_valid_steps(self, start: Pos) -> List[Pos]:
        result = []
        for i in range(len(self.field)):
            for j in (start[1] + (start[0] - i), start[1] - (start[0] - i)):
                if 0 <= j < len(self.field) and self.is_valid_step(start, (i, j)):
                    result.append((i, j))
        return result

    def get_valid_eating_steps(self, start: Pos) -> List[Pos]:
        result = []
        for finish in self.get_valid_steps(start):
            if self.eats_one_enemy(start, finish):
                result.append(finish)
        return result

    def can_eat(self, start: Pos) -> bool:
        dr = self[start]

        if not dr.is_king:
            for delta_x in (-1, 1):
                for delta_y in (-1, 1):
                    if is_valid_position((start[0] + 2 * delta_x, start[1] + 2 * delta_y), len(self.field)):
                        if self.field[start[0] + 2 * delta_x][start[1] + 2 * delta_y] is None and \
                                self.field[start[0] + delta_x][start[1] + delta_y] is not None and \
                                self.field[start[0] + delta_x][start[1] + delta_y].color_type != dr.color_type:
                            return True
            return False
        else:
            return self.get_valid_eating_steps(start) != []

    def draught_pos_to_eat(self, start: Pos, finish: Pos):
        dir_x, dir_y = get_dirs(start, finish)
        pos = [start[0], start[1]]
        while pos != list(finish):
            pos[0] += dir_x
            pos[1] += dir_y
            if self[pos] is not None:
                return pos
        return None

    def eat_draught(self, start: Pos, finish: Pos):
        dr_pos = self.draught_pos_to_eat(start, finish)
        if dr_pos is not None:
            self[dr_pos] = None

    def move_draught(self, start: Pos, finish: Pos):
        self.eat_draught(start, finish)
        start_draught = self[start]
        if start_draught.color_type == ColorType.WHITE and finish[0] == 0:
            start_draught.is_king = True
        if start_draught.color_type == ColorType.BLACK and finish[0] == len(self.field) - 1:
            start_draught.is_king = True
        self[start] = None
        self[finish] = start_draught


chess = ChessBoard()
chess.can_eat((0, 1))
