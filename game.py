import draught
import pygame
import copy
import pickle
import os
from enum import Enum
from chessboard import ChessBoard, Pos
from draught import ColorType
from typing import Tuple


GRAY = (105, 105, 105)
GREEN = (0, 200, 64)
WHITE_GRAY = (215, 215, 215)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class PlayerType(Enum):
    Player = 1
    AI = 2


def get_indexes(pos: tuple, cell_size: int) -> Pos:
    return pos[1] // cell_size, pos[0] // cell_size


def get_coordinate(index: int, cell_size: int) -> int:
    return int(cell_size * (index + 1 / 2))


class State(Enum):
    CHOOSING_DRAUGHT = 1
    CHOOSING_TARGET = 2


class Game:
    def __init__(self, chess_board=ChessBoard(), game_mode=1, difficulty=4, test_mode=False):
        self.chess_board = chess_board

        if not test_mode:
            self.chessboard_picture_size = 512
            self.cell_size = int(self.chessboard_picture_size / len(self.chess_board))
            self.screen: pygame.Surface = pygame.display.set_mode((self.chessboard_picture_size,
                                                                   self.chessboard_picture_size))
            self.crown = pygame.image.load("Pictures/Crown.png").convert_alpha()
            self.scaled_crown = pygame.transform.scale(self.crown,
                                                       (40 * self.chessboard_picture_size // 512,
                                                        22 * self.chessboard_picture_size // 512))
        # initializing game variables
        self.last_mouse_pos = None
        self.chosen_draught = None
        self.chosen_draught_position = None
        self.chosen_target_position = None
        self.can_change_draught = True
        self.current_state = State.CHOOSING_DRAUGHT
        self.current_player_color_type = ColorType.WHITE

        self.game_mode = game_mode
        if game_mode == 1:
            self.players = [PlayerType.AI, PlayerType.AI]
        elif game_mode == 2:
            self.players = [PlayerType.Player, PlayerType.AI]
        elif game_mode == 3:
            self.players = [PlayerType.Player, PlayerType.Player]
        else:
            raise Exception('unknown game mode')
        self.difficulty = difficulty
        self.test_mode = test_mode

        # we store number of steps, made by ai
        # to calculate average step time
        self.ai_step_number = 0

    def draw_field(self):
        offset_x = - self.chessboard_picture_size * 20 // 512
        offset_y = - self.chessboard_picture_size * 10 // 512

        pygame.draw.rect(self.screen, GRAY, (0, 0, self.chessboard_picture_size, self.chessboard_picture_size))
        for i in range(len(self.chess_board)):
            for j in range(len(self.chess_board)):
                if (i + j) % 2 == 0:
                    pygame.draw.rect(self.screen, WHITE_GRAY,
                                     (j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size))

                if self.chosen_draught_position == (i, j):
                    pygame.draw.rect(self.screen, GREEN,
                                     (j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size))

                if self.chess_board[i][j] is not None:
                    pos_x = get_coordinate(j, self.cell_size)
                    pos_y = get_coordinate(i, self.cell_size)
                    color = WHITE if self.chess_board[i][j].is_white else BLACK
                    pygame.draw.circle(self.screen, color, (pos_x, pos_y), int(self.cell_size / 2))
                    if self.chess_board[i][j].is_king:
                        self.screen.blit(self.scaled_crown, (pos_x + offset_x, pos_y + offset_y))

    def set_choices_none(self):
        self.chosen_draught = None
        self.chosen_draught_position = None
        self.chosen_target_position = None
        self.can_change_draught = True

    def eating_draught_exists(self) -> bool:
        for i, row in enumerate(self.chess_board.field):
            for j, dr in enumerate(row):
                if dr is not None and dr.color_type == self.current_player_color_type:
                    if self.chess_board.can_eat((i, j)):
                        return True
        return False

    def change_current_player(self):
        self.current_player_color_type = ColorType.BLACK if \
            self.current_player_color_type == ColorType.WHITE else ColorType.WHITE
        self.set_choices_none()
        self.current_state = State.CHOOSING_DRAUGHT

    def correct_draught_is_chosen(self):
        if self.chosen_draught is None:
            return False

        if self.chosen_draught.color_type != self.current_player_color_type:
            return False

        return not self.eating_draught_exists() or \
            self.chess_board.can_eat(self.chosen_draught_position)

    def player_choose_draught(self):
        if self.last_mouse_pos is not None:
            self.chosen_draught_position = get_indexes(self.last_mouse_pos, self.cell_size)
            self.chosen_draught = self.chess_board[self.chosen_draught_position]
            self.last_mouse_pos = None

        if self.correct_draught_is_chosen():
            self.current_state = State.CHOOSING_TARGET
        else:
            self.set_choices_none()

    def player_choose_target(self):
        if self.last_mouse_pos is not None:
            self.chosen_target_position = get_indexes(self.last_mouse_pos, self.cell_size)
            self.last_mouse_pos = None

        if self.chosen_target_position is None:
            return

        just_ate_someone = False
        if self.chess_board.can_eat(self.chosen_draught_position):
            just_ate_someone = True
            chosen_target_valid = self.chess_board.is_valid_eating_step(self.chosen_draught_position,
                                                                        self.chosen_target_position)
        else:
            chosen_target_valid = self.chess_board.is_valid_step(self.chosen_draught_position,
                                                                 self.chosen_target_position)

        if not chosen_target_valid:
            if self.can_change_draught:
                self.chosen_draught = None
                self.chosen_draught_position = None
                self.current_state = State.CHOOSING_DRAUGHT
            return

        self.chess_board.move_draught(self.chosen_draught_position, self.chosen_target_position)
        if just_ate_someone and self.chess_board.can_eat(self.chosen_target_position):
            # in this case we have to make one more step
            self.chosen_draught_position = self.chosen_target_position
            self.can_change_draught = False
        else:
            self.change_current_player()

    def make_step_player(self):
        if self.current_state == State.CHOOSING_DRAUGHT:
            self.player_choose_draught()
        elif self.current_state == State.CHOOSING_TARGET:
            self.player_choose_target()
        else:
            raise Exception('unknown state')

    def score(self) -> int:
        result = 0
        for i, row in enumerate(self.chess_board.field):
            for j, dr in enumerate(row):
                if dr is not None:
                    if dr.color_type == self.current_player_color_type:
                        result += dr.get_score()
                    else:
                        result -= dr.get_score()
        return result

    def get_possible_steps(self) -> list:
        result = []
        need_to_find_eating_draught = self.eating_draught_exists()
        for i, row in enumerate(self.chess_board.field):
            for j, dr in enumerate(row):
                if dr is not None and dr.color_type == self.current_player_color_type:
                    if need_to_find_eating_draught:
                        possible_finishes = self.chess_board.get_valid_eating_steps((i, j))
                    else:
                        possible_finishes = self.chess_board.get_valid_steps((i, j))
                    for finish in possible_finishes:
                        result.append(((i, j), finish))
        return result

    def best_step(self, depth: int, starting_pos: Pos) -> Tuple[Pos, Pos, int]:
        if depth == 0:
            return None, None, self.score()
        if starting_pos != ():
            possible_steps = [(starting_pos, finish) for finish in
                              self.chess_board.get_valid_eating_steps(starting_pos)]
        else:
            possible_steps = self.get_possible_steps()
        if not possible_steps:
            return None, None, self.score()

        best_step_so_far = (None, None, -1000)

        for step in possible_steps:
            # saving current field condition
            dr_copy = copy.deepcopy(self.chess_board[step[0]])
            dr_to_eat_pos = self.chess_board.draught_pos_to_eat(step[0], step[1])
            eaten_dr_copy = None if dr_to_eat_pos is None else copy.deepcopy(
                self.chess_board[dr_to_eat_pos])

            one_more_step = self.chess_board.eats_one_enemy(step[0], step[1])
            self.chess_board.move_draught(step[0], step[1])
            one_more_step &= self.chess_board.can_eat(step[1])

            if one_more_step:
                next_step = self.best_step(max(depth - 1, 1), step[1])
                if next_step[2] > best_step_so_far[2]:
                    best_step_so_far = (step[0], step[1], next_step[2])
            else:
                self.change_current_player()
                worst_step = self.best_step(depth - 1, ())
                self.change_current_player()
                if -worst_step[2] > best_step_so_far[2]:
                    best_step_so_far = (step[0], step[1], -worst_step[2])

            # recovering field condition
            self.chess_board[step[0]] = dr_copy
            self.chess_board[step[1]] = None
            if dr_to_eat_pos is not None:
                self.chess_board[dr_to_eat_pos] = eaten_dr_copy

        return best_step_so_far

    def make_step_ai(self, starting_pos: Pos):
        if not self.get_possible_steps():
            print('Game Over!')
            return
        players_copy = self.players.copy()
        self.players = [PlayerType.AI, PlayerType.AI]

        start_finish_score = self.best_step(self.difficulty, starting_pos)

        one_eaten = self.chess_board.eats_one_enemy(start_finish_score[0], start_finish_score[1])
        self.chess_board.move_draught(start_finish_score[0], start_finish_score[1])
        if one_eaten and self.chess_board.can_eat(start_finish_score[1]):
            self.make_step_ai(start_finish_score[1])
        else:
            self.change_current_player()

        self.players = players_copy
        self.ai_step_number += 1

    def save_game(self):
        data_to_save = {
            'chessboard': self.chess_board,
            'chosen_draught': self.chosen_draught,
            'chosen_draught_position': self.chosen_draught_position,
            'chosen_target_position': self.chosen_target_position,
            'can_change_draught': self.can_change_draught,
            'current_state': self.current_state,
            'current_player_color_type': self.current_player_color_type,
            'difficulty': self.difficulty,
            'game_mode': self.game_mode,
            'players': self.players
        }
        with open('Game data/save.txt', 'wb') as save_file:
            pickle.dump(data_to_save, save_file)

    def copy_loaded_data(self, loaded_data):
        self.chess_board = loaded_data['chessboard']
        self.chosen_draught = loaded_data['chosen_draught']
        self.chosen_draught_position = loaded_data['chosen_draught_position']
        self.chosen_target_position = loaded_data['chosen_target_position']
        self.can_change_draught = loaded_data['can_change_draught']
        self.current_state = loaded_data['current_state']
        self.current_player_color_type = loaded_data['current_player_color_type']
        self.difficulty = loaded_data['difficulty']
        self.game_mode = loaded_data['game_mode']
        self.players = loaded_data['players']

    def load_game(self):
        with open('Game data/save.txt', 'rb') as load_file:
            if os.stat('Game data/save.txt').st_size != 0:
                loaded_data = pickle.load(load_file)
                self.copy_loaded_data(loaded_data)

    def get_game_over_message(self):
        white_draughts_exist = False
        black_draughts_exits = False
        for i, row in enumerate(self.chess_board.field):
            for j, dr in enumerate(row):
                if dr is not None:
                    if dr.color_type == draught.ColorType.WHITE:
                        white_draughts_exist = True
                    else:
                        black_draughts_exits = True

        if white_draughts_exist and black_draughts_exits:
            return 'Draw!'
        else:
            return 'White side wins!' if white_draughts_exist else 'Black side wins!'

    def draw_game_over_message(self):
        hint = ' Press LMB to continue.'
        game_over_message = self.get_game_over_message()
        game_over_message += hint
        font_obj = pygame.font.SysFont('Arial', 30)
        text_surface_obj = font_obj.render(game_over_message, True, GRAY, GREEN)
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.center = (self.chessboard_picture_size // 2, self.chessboard_picture_size // 2)
        self.screen.blit(text_surface_obj, text_rect_obj)

    def game_over(self):
        self.draw_field()
        self.draw_game_over_message()
        pygame.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONUP:
                    running = False

    def play(self):
        if not self.test_mode:
            pygame.init()

        running = True
        while running:
            if not self.test_mode:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.last_mouse_pos = pygame.mouse.get_pos()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_s:
                            self.save_game()
                        elif event.key == pygame.K_l:
                            self.load_game()

            player_number = 0 if self.current_player_color_type == ColorType.WHITE else 1
            if self.players[player_number] == PlayerType.Player:
                self.make_step_player()
            elif self.players[player_number] == PlayerType.AI:
                self.make_step_ai(())
            else:
                raise Exception('unknown player')

            if not self.get_possible_steps():
                running = False

            if not self.test_mode:
                self.draw_field()
                pygame.display.flip()

        if not self.test_mode:
            self.game_over()
