import chessboard
import game
import test
import pygame
import musicmanager

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 64)
RED = (255, 0, 0)


class InterfaceGame:
    def __init__(self):
        self.screen_size = game.Game().chessboard_picture_size
        self.button_horizontal_size = 120
        self.button_vertical_size = 60
        self.offset_y = 100

    @staticmethod
    def draw_text(screen, text, text_size, text_color, background_color, center_pos):
        font_obj = pygame.font.SysFont('Arial', text_size)
        text_surface_obj = font_obj.render(text, True, text_color, background_color)
        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.center = center_pos
        screen.blit(text_surface_obj, text_rect_obj)

    def draw_buttons(self, screen, button_names: tuple, hint=None):
        if hint is not None:
            center_pos = (self.screen_size // 2, int(self.button_vertical_size * 3 / 4))
            InterfaceGame.draw_text(screen, hint, 26, RED, WHITE, center_pos)

        for button_number in range(3):
            left_up_corner_x = (self.screen_size - self.button_horizontal_size) // 2
            left_up_corner_y = self.offset_y * (button_number + 1)
            pygame.draw.rect(screen, GREEN,
                             (left_up_corner_x, left_up_corner_y, self.button_horizontal_size,
                              self.button_vertical_size))

            center_pos = (self.screen_size // 2, left_up_corner_y + self.button_vertical_size // 2)
            InterfaceGame.draw_text(screen, button_names[button_number], 16, BLACK, GREEN, center_pos)

    def button_is_pressed(self, button_number: int, mouse_position: tuple) -> bool:
        left_up_corner_x = (self.screen_size - self.button_horizontal_size) // 2
        left_up_corner_y = self.offset_y * (button_number + 1)
        return left_up_corner_x <= mouse_position[0] <= left_up_corner_x + self.button_horizontal_size and \
            left_up_corner_y <= mouse_position[1] <= left_up_corner_y + self.button_vertical_size

    def choose_parameters(self, parameters_types: tuple, hint=None):
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
            self.draw_buttons(screen, parameters_types, hint=hint)
            pygame.display.flip()

    def choose_game_mode(self):
        game_mode_names = ('AI vs AI', 'player vs AI', 'player vs player')
        result = self.choose_parameters(game_mode_names, hint='Choose game mode!')
        return result + 1 if result != -1 else -1

    def choose_difficulty(self):
        difficulty_types = ('easy', 'medium', 'hard')
        result = self.choose_parameters(difficulty_types, hint='Choose difficulty!')
        return result + 3 if result != -1 else -1

    def choose_music(self):
        music_types = ('Green Day', 'Blink-182', 'I don\'t like music!')
        result = self.choose_parameters(music_types, hint='Choose music!')
        if result == len(music_types) - 1:
            return None
        return -1 if result == -1 else music_types[result]

    def play(self):
        running = True
        while running:  # if some of the chosen parameters is -1, player quited the game
            game_mode = self.choose_game_mode()
            if game_mode == -1:
                return

            difficulty = 4
            if game_mode != 3:
                difficulty = self.choose_difficulty()
            if difficulty == -1:
                return

            group_name = self.choose_music()
            if group_name == -1:
                return
            music_manager = musicmanager.MusicManager()
            if group_name is not None:
                music_manager.play(group_name)

            new_chessboard = chessboard.ChessBoard()
            this_game = game.Game(new_chessboard, game_mode, difficulty)
            this_game.play()

            # stopping the music
            music_manager.__del__()


def main():
    # you can set test_mode=False to see
    # the game between AIs while testing
    # test.run_tests(test_mode=True)
    interface_game = InterfaceGame()
    interface_game.play()


if __name__ == '__main__':
    main()
