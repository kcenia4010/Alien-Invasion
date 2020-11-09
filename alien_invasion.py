import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    """Класс для урпаления ресурсами и поведением игры"""

    def __init__(self):
        """Инициальизирует игру и создает игровыне ресурсы"""
        pygame.init()
        self.settings = Settings()


        #Вывод игры в окно
        #self.screen = pygame.display.set_mode(
        #              (self.settings.sreen_width, self.settings.sreen_height))

        #вывод на полный экран
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height

        pygame.display.set_caption("Alien Invasion")


        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        #Создание кнопки Play
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Запуск основного цикла игры"""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

            

    def _check_events(self):
        """Обрабатывает нажатия клавишь и события мыши"""
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)
                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_play_button(self, mouse_pos):
        """Запускает игру при нажатии на PLay"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            #Сброс игровой статистики 
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_ships()

            #Отчистка списков пришельцев и снарядов
            self.aliens.empty()
            self.bullets.empty()

            #Создание нового флота и размещение коробля в центре
            self._create_fleet()
            self.ship._center_ship()

            #Сокрытие указателя мыши
            pygame.mouse.set_visible(False)

    def _fire_bullet(self):
        """Создание нового снаряда и включение его в группу bullets"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        #Обновление позиции снаряда
        self.bullets.update()
        
        #Удаление снарядов, вышедших за экран
        for bullet in self.bullets.copy():
                if bullet.rect.bottom <= 0:
                    self.bullets.remove(bullet)
        
        self._check_bullet_alien_collisions()
        
    def _check_bullet_alien_collisions(self):
        #при обнаружении попадания удалить снаяряд и пришельца
        collisions = pygame.sprite.groupcollide(
                    self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            #Уничтожение существующих снарядов и создание нового флота + повышение скорости
            self.bullets.empty()
            self.settings.increase_speed()
            self._create_fleet()

            self.stats.level +=1
            self.sb.prep_level()
 
    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()

        #Проверка коллизий "пришелец-корабль"
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        #Проверка: добрались ли пришельцы до нижнего края экрана
        self._check_aliens_bottom()


    def _create_fleet(self):
        """Создание флота пришельцев"""
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        number_aliens_x = (self.settings.screen_width - 
                (2 * alien_width)) // (2 * alien_width)

        #количесво рядов на экране
        number_rows = ((self.settings.screen_height - 
                3 * alien_height - self.ship.rect.height) // 
                        (2 * alien_height))


        #Создание флота вторжения
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Создание пришельца и размещение его в ряду"""
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.y = alien_height + 2 * alien_height * row_number
        alien.rect.y = alien.y
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self.change_fleet_direction()
                break

    def change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit (self):
        """Обработка столкновения коробря с пришельцами"""
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship._center_ship()

            sleep(1.0)
        
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Проверяет добрались ли пришельцы до нижней части экрана"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >=screen_rect.bottom:
                self._ship_hit()
                break

    def _update_screen(self):
        """Обновляет изображение экрана и отображает новый экран"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        if self.stats.game_active:
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()

        self.aliens.draw(self.screen)
        self.sb.show_score()

        if not self.stats.game_active:
            self.play_button.draw_button()

        #Отображение последнего прорисованного экрана
        pygame.display.flip()

if __name__=='__main__':
    #создание экземпляра и запуск игры
    ai = AlienInvasion()
    ai.run_game()
