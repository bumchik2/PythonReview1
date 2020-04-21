import pygame
import random


class MusicManager:
    music = {
        'Green Day': ('Wake me up, when September ends',),
        'Blink-182': ('Adam\'s song',)
    }

    @staticmethod
    def get_random_song(group_name):
        return f'Music/{random.choice(MusicManager.music[group_name])}.mp3'

    def play(self, group_name):
        pygame.mixer.init()
        pygame.mixer.music.load(self.get_random_song(group_name))
        pygame.mixer.music.play()

    def __del__(self):
        pygame.mixer.music.fadeout(1000)
