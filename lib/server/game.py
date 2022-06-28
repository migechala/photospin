import random


class Round:
    def __init__(self, player_images) -> None:
        self.player_images = player_images
        

    def getRandomImage(self) -> str:
        key = random.choice(list(self.player_images.items()))
        self.player_images.pop(key)
        return key