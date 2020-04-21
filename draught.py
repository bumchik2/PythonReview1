from typing import NamedTuple
from enum import Enum


Pos = NamedTuple("Pos", (('x', int), ('y', int)))


def get_dirs(start: Pos, finish: Pos) -> Pos:
    dir_x = finish[0] - start[0]
    dir_x //= abs(dir_x)
    dir_y = finish[1] - start[1]
    dir_y //= abs(dir_y)
    return dir_x, dir_y


def is_valid_position(pos: Pos, board_size: int) -> bool:
    return 0 <= pos[0] < board_size and 0 <= pos[1] < board_size


class ColorType(Enum):
    WHITE = 1
    BLACK = 2


class Draught:
    def __init__(self, is_white: bool, is_king=False):
        self.is_white = is_white
        self.is_king = is_king

    def get_color_type(self):
        return ColorType.WHITE if self.is_white else ColorType.BLACK

    def set_color_type(self, new_color_type: ColorType):
        self.is_white = True if new_color_type == ColorType.WHITE else False

    color_type = property(fget=get_color_type, fset=set_color_type)

    def __eq__(self, other):
        if isinstance(other, Draught):
            return (self.color_type == other.color_type and
                    self.is_king == other.is_king)
        return False

    def __hash__(self):
        return hash(self.is_white, self.is_king)

    def enemies_on_the_way(self, start: Pos, finish: Pos, field) -> int:
        dir_x, dir_y = get_dirs(start, finish)
        pos = list(start)
        enemies = 0
        while pos != list(finish):
            pos[0] += dir_x
            pos[1] += dir_y
            if field[pos[0]][pos[1]] is not None:
                if field[pos[0]][pos[1]].color_type == self.color_type:
                    return -1
                else:
                    enemies += 1
        return enemies

    def eats_one_enemy(self, start: Pos, finish: Pos, field: list) -> bool:
        if abs(finish[0] - start[0]) != abs(finish[1] - start[1]):
            return False
        if field[finish[0]][finish[1]] is not None:
            return False
        return self.enemies_on_the_way(start, finish, field) == 1

    def is_valid_step(self, start: Pos, finish: Pos, field):
        if field[finish[0]][finish[1]] is not None:
            return False
        if abs(start[0] - finish[0]) != abs(start[1] - finish[1]):
            return False
        if not self.is_king:
            if abs(start[0] - finish[0]) > 2:
                return False
            if abs(start[0] - finish[0]) == 2:
                return self.eats_one_enemy(start, finish, field)
            if self.color_type == ColorType.WHITE:
                if start[0] <= finish[0]:
                    return False
            if self.color_type == ColorType.BLACK:
                if start[0] >= finish[0]:
                    return False
            if abs(start[0] - finish[0]) == 1:
                return True
            return False
        else:
            return self.eats_one_enemy(start, finish, field) or \
                   self.enemies_on_the_way(start, finish, field) == 0

    def is_valid_eating_step(self, start: Pos, finish: Pos, field: list):
        return self.is_valid_step(start, finish, field) & self.eats_one_enemy(start, finish, field)

    def get_valid_steps(self, start: Pos, field) -> list:
        result = []
        for i in range(len(field)):
            j = start[1] + (start[0] - i)
            if 0 <= j < len(field) and self.is_valid_step(start, (i, j), field):
                result.append((i, j))
            j = start[1] - (start[0] - i)
            if 0 <= j < len(field) and self.is_valid_step(start, (i, j), field):
                result.append((i, j))
        return result

    def get_valid_eating_steps(self, start: Pos, field) -> list:
        result = []
        for finish in self.get_valid_steps(start, field):
            if self.eats_one_enemy(start, finish, field):
                result.append(finish)
        return result

    def can_eat(self, start: Pos, field) -> bool:
        if not self.is_king:
            for delta_x in (-1, 1):
                for delta_y in (-1, 1):
                    if is_valid_position((start[0] + 2 * delta_x, start[1] + 2 * delta_y), len(field)):
                        if field[start[0] + 2 * delta_x][start[1] + 2 * delta_y] is None and \
                                field[start[0] + delta_x][start[1] + delta_y] is not None and \
                                field[start[0] + delta_x][start[1] + delta_y].color_type != self.color_type:
                            return True
            return False
        else:
            return self.get_valid_eating_steps(start, field) != []

    def get_score(self):
        return 3 if self.is_king else 1


def draught_pos_to_eat(start: Pos, finish: Pos, field):
    dir_x, dir_y = get_dirs(start, finish)
    pos = list(start)
    while pos != list(finish):
        pos[0] += dir_x
        pos[1] += dir_y
        if field[pos[0]][pos[1]] is not None:
            return pos[0], pos[1]
    return None


def eat_draught(start: Pos, finish: Pos, field):
    dr_pos = draught_pos_to_eat(start, finish, field)
    if dr_pos is not None:
        field[dr_pos[0]][dr_pos[1]] = None


def move_draught(start: Pos, finish: Pos, field):
    eat_draught(start, finish, field)
    start_draught = field[start[0]][start[1]]
    if start_draught.color_type == ColorType.WHITE and finish[0] == 0:
        start_draught.is_king = True
    if start_draught.color_type == ColorType.BLACK and finish[0] == len(field) - 1:
        start_draught.is_king = True
    field[start[0]][start[1]] = None
    field[finish[0]][finish[1]] = start_draught
