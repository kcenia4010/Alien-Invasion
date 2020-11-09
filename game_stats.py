class GameStats():
    """Отслеживание статистики"""

    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = False

        #Рекорд
        with open('C:\\Users\\Kceni\\Desktop\\personal_projects\\Alien-Invasion\\High score.txt') as f:
            self.high_score = f.read()
        self.high_score = int(self.high_score)
        

    def reset_stats(self):
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1