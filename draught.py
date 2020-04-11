WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def get_dirs(start: tuple, finish: tuple) -> tuple:
    dir_x = finish[0] - start[0]
    dir_x //= abs(dir_x)
    dir_y = finish[1] - start[1]
    dir_y //= abs(dir_y)
    return dir_x, dir_y


class Draught:
    def __init__(self, color_type: str, is_king=False):
        self.color_type = color_type
        self.is_king = is_king
        self.color = WHITE if color_type == 'white' else BLACK

    def __eq__(self, other):
        if isinstance(other, Draught):
            return (self.color_type == other.color_type and
                    self.is_king == other.is_king)

    def enemies_on_the_way(self, start: tuple, finish: tuple, field: list) -> int:
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

    def eats_one_enemy(self, start: tuple, finish: tuple, field: list) -> bool:
        if abs(finish[0] - start[0]) != abs(finish[1] - start[1]):
            return False
        if field[finish[0]][finish[1]] is not None:
            return False
        return self.enemies_on_the_way(start, finish, field) == 1

    def is_valid_step(self, start: tuple, finish: tuple, field: list):
        if field[finish[0]][finish[1]] is not None:
            return False
        if abs(start[0] - finish[0]) != abs(start[1] - finish[1]):
            return False
        if not self.is_king:
            if abs(start[0] - finish[0]) == 2:
                return self.eats_one_enemy(start, finish, field)
            if self.color_type == 'white':
                if start[0] <= finish[0]:
                    return False
            if self.color_type == 'black':
                if start[0] >= finish[0]:
                    return False
            if abs(start[0] - finish[0]) == 1:
                return True
            return False
        else:
            return self.eats_one_enemy(start, finish, field) or \
                   self.enemies_on_the_way(start, finish, field) == 0

    def is_valid_eating_step(self, start: tuple, finish: tuple, field: list):
        return self.is_valid_step(start, finish, field) & self.eats_one_enemy(start, finish, field)

    def get_valid_steps(self, start: tuple, field: list) -> tuple:
        result = []
        for i in range(len(field)):
            j = start[1] + (start[0] - i)
            if 0 <= j < len(field) and self.is_valid_step(start, (i, j), field):
                result.append((i, j))
            j = start[1] - (start[0] - i)
            if 0 <= j < len(field) and self.is_valid_step(start, (i, j), field):
                result.append((i, j))
        return tuple(result)

    def get_valid_eating_steps(self, start: tuple, field: list) -> tuple:
        result = []
        for finish in self.get_valid_steps(start, field):
            if self.eats_one_enemy(start, finish, field):
                result.append(finish)
        return tuple(result)

    def can_eat(self, start: tuple, field: list) -> bool:
        return self.get_valid_eating_steps(start, field) != ()

    def get_score(self):
        return 3 if self.is_king else 1


def draught_pos_to_eat(start: tuple, finish: tuple, field: list) -> tuple:
    dir_x, dir_y = get_dirs(start, finish)
    pos = list(start)
    while pos != list(finish):
        pos[0] += dir_x
        pos[1] += dir_y
        if field[pos[0]][pos[1]] is not None:
            return pos[0], pos[1]
    return ()


def eat_draught(start: tuple, finish: tuple, field: list):
    dr_pos = draught_pos_to_eat(start, finish, field)
    if dr_pos != ():
        field[dr_pos[0]][dr_pos[1]] = None


def move_draught(start: tuple, finish: tuple, field: list):
    eat_draught(start, finish, field)
    start_draught = field[start[0]][start[1]]
    if start_draught.color_type == 'white' and finish[0] == 0:
        start_draught.is_king = True
    if start_draught.color_type == 'black' and finish[0] == len(field) - 1:
        start_draught.is_king = True
    field[start[0]][start[1]] = None
    field[finish[0]][finish[1]] = start_draught
