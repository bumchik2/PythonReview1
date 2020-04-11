import chessboard
import game
import test
import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 64)


class InterfaceGame:
    def __init__(self):
        self.screen_size = game.Game().chessboard_picture_size
        self.button_horizontal_size = 120
        self.button_vertical_size = 60
        self.offset_y = 100

    def draw_buttons(self, screen, button_names: tuple):
        for button_number in range(3):
            left_up_corner_x = (self.screen_size - self.button_horizontal_size) // 2
            left_up_corner_y = self.offset_y * (button_number + 1)
            pygame.draw.rect(screen, GREEN,
                             (left_up_corner_x, left_up_corner_y, self.button_horizontal_size,
                              self.button_vertical_size))

            font_obj = pygame.font.SysFont('Arial', 16)
            text_surface_obj = font_obj.render(button_names[button_number], True, BLACK, GREEN)
            text_rect_obj = text_surface_obj.get_rect()
            text_rect_obj.center = (self.screen_size // 2, left_up_corner_y + self.button_vertical_size // 2)
            screen.blit(text_surface_obj, text_rect_obj)

    def button_is_pressed(self, button_number: int, mouse_position: tuple) -> bool:
        left_up_corner_x = (self.screen_size - self.button_horizontal_size) // 2
        left_up_corner_y = self.offset_y * (button_number + 1)
        return left_up_corner_x <= mouse_position[0] <= left_up_corner_x + self.button_horizontal_size and \
            left_up_corner_y <= mouse_position[1] <= left_up_corner_y + self.button_vertical_size

    def choose_parameters(self, parameters_types: tuple):
        pygame.init()
        screen: pygame.Surface = pygame.display.set_mode((self.screen_size,
                                                          self.screen_size))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_pos = pygame.mouse.get_pos()
                    for parameter_number in range(len(parameters_types)):
                        if self.button_is_pressed(parameter_number, mouse_pos):
                            return parameter_number
            pygame.draw.rect(screen, WHITE, (0, 0, self.screen_size, self.screen_size))
            self.draw_buttons(screen, parameters_types)
            pygame.display.flip()

    def choose_game_mode(self):
        game_mode_names = ('AI vs AI', 'player vs AI', 'player vs player')
        result = self.choose_parameters(game_mode_names)
        return result + 1 if result != -1 else -1

    def choose_difficulty(self):
        difficulty_types = ('easy', 'medium', 'difficult')
        result = self.choose_parameters(difficulty_types)
        return result + 3 if result != -1 else -1

    def play(self):
        running = True
        while running:
            game_mode = self.choose_game_mode()
            difficulty = 4
            if game_mode != 3 and game_mode != -1:
                difficulty = self.choose_difficulty()
            if game_mode == -1 or difficulty == -1:
                return
            new_chessboard = chessboard.ChessBoard()
            this_game = game.Game(new_chessboard, game_mode, difficulty)
            this_game.play()


def main():
    test.run_tests()
    interface_game = InterfaceGame()
    interface_game.play()


main()
