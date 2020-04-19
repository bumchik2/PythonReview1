import draught


class ChessBoard:
    def __init__(self, size=8, rows_filled=3):
        self.field = []
        for row in range(size):
            self.field.append([])
            for column in range(size):
                if row < rows_filled and (row + column) % 2 == 1:
                    self.field[len(self.field) - 1].append(draught.Draught(is_white=False))
                elif row >= size - rows_filled and (row + column) % 2 == 1:
                    self.field[len(self.field) - 1].append(draught.Draught(is_white=True))
                else:
                    self.field[len(self.field) - 1].append(None)
