import random


class Round:
    def __init__(self, player_images) -> None:
        self.player_images = player_images
        

    def getRandomImage(self) -> str:
        key = next(iter(self.player_images))
        return key