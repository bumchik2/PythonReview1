from enum import Enum


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
        return hash((self.is_white, self.is_king))

    def get_score(self):
        return 3 if self.is_king else 1
