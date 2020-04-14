import draught
import chessboard
import game
import numpy
from datetime import datetime


def print_field(field):
    for i in range(len(field)):
        for j in range(len(field[0])):
            if field[i][j] is None:
                print('-', end=' ')
            else:
                if field[i][j].color_type == 'white':
                    print('w', end=' ')
                else:
                    print('b', end=' ')
        print()


def general_test(field1, field2):
    chess_board = chessboard.ChessBoard()
    chess_board.field = field1
    test_game = game.Game(chess_board)
    test_game.make_step_ai(())
    numpy.testing.assert_equal(test_game.field, field2)


def test_simple_eating():
    # just simple eating step
    start_field = [
        [None, None, None, None],
        [None, None, None, None],
        [None, draught.Draught('black'), None, None],
        [None, None, draught.Draught('white'), None]
    ]
    expected_field = [
        [None, None, None, None],
        [draught.Draught('white'), None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]
    general_test(start_field, expected_field)
    print('test \'simple eating\' passed')


def test_try_not_to_die():
    # one step leads to immediate death,
    # another one does not
    start_field = [
        [None, None, None, None],
        [draught.Draught('black'), None, None, None],
        [None, None, None, None],
        [None, None, draught.Draught('white'), None]
    ]
    expected_field = [
        [None, None, None, None],
        [draught.Draught('black'), None, None, None],
        [None, None, None, draught.Draught('white')],
        [None, None, None, None]
    ]
    general_test(start_field, expected_field)
    print('test \'try not to die\' passed')


def test_eat_two_not_one():
    # eating one enemy is better than
    # eating one in this case
    start_field = [
        [None] * 6,
        [None] * 6,
        [None, None, draught.Draught('black'), None, None, None],
        [None] * 6,
        [None, None, draught.Draught('black'), None, draught.Draught('black'), None],
        [None, None, None, draught.Draught('white'), None, None]
    ]
    expected_field = [
        [None] * 6,
        [None, None, None, draught.Draught('white'), None, None],
        [None] * 6,
        [None] * 6,
        [None, None, None, None, draught.Draught('black'), None],
        [None] * 6
    ]
    general_test(start_field, expected_field)
    print('test \'eat two, not one\' passed')


def test_long_eating():
    # this test checks, if draughts can eat
    # through long distances, once they become kings
    start_field = [
        [None] * 6,
        [None, draught.Draught('black'), None, None, None, None],
        [draught.Draught('white'), None, None, None, draught.Draught('black'), None],
        [None, draught.Draught('black'), None, None, None, None],
        [None] * 6,
        [None] * 6
    ]
    expected_field = [
        [None] * 6,
        [None] * 6,
        [None] * 6,
        [None, draught.Draught('black'), None, None, None, draught.Draught('white', True)],
        [None] * 6,
        [None] * 6
    ]
    general_test(start_field, expected_field)
    print('test \'long eating\' passed')


def test_multiple_complex_eating():
    # there is only one way to eat
    # all of the black draughts
    # - - - 2 - 6 - -
    # - - b - - - b -
    # - 1 - b - b - 7
    # - - b - - - - -
    # - 5 - w - - - 3
    # - - b - b - b -
    # - - - 8 - - - -
    # - - r - 4 - - -
    start_field = [
        [None] * 8,
        [None, None, draught.Draught('black'), None, None, None, draught.Draught('black'), None],
        [None, None, None, draught.Draught('black'), None, draught.Draught('black'), None, None],
        [None, None, draught.Draught('black'), None, None, None, None, None],
        [None, None, None, draught.Draught('white'), None, None, None, None],
        [None, None, draught.Draught('black'), None,
         draught.Draught('black'), None, draught.Draught('black'), None],
        [None] * 8,
        [None, None, draught.Draught('gray'), None, None, None, None, None]
    ]
    # gray draught is a 'neutral' draught,
    # just a wall, blocking a cell
    expected_field = [
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None] * 8,
        [None, None, None, draught.Draught('white', True), None, None, None, None],
        [None, None, draught.Draught('gray'), None, None, None, None, None]
    ]
    general_test(start_field, expected_field)
    print('test \'multiple complex eating\' passed')


def test_time(func):
    def wrapper():
        start_time = datetime.now()
        func()
        print(func.__name__, ' is ', datetime.now() - start_time)

    return wrapper


@test_time
def first_step_time():
    difficulty = 5
    new_chessboard = chessboard.ChessBoard()
    new_game = game.Game(new_chessboard, difficulty=difficulty)
    new_game.make_step_ai(())


def hard_game_time():
    start_time = datetime.now()
    difficulty = 5
    new_chessboard = chessboard.ChessBoard()
    new_game = game.Game(new_chessboard, difficulty=difficulty, test_mode=True)
    new_game.play()
    print('average step time is: ', (datetime.now() - start_time) / new_game.ai_step_number)


def run_tests():
    test_simple_eating()
    test_try_not_to_die()
    test_eat_two_not_one()
    test_long_eating()
    test_multiple_complex_eating()
    first_step_time()
    hard_game_time()
    print('all tests passed!')


if __name__ == '__main__':
    run_tests()
