import pygame
import sys
from random import randint
import time


class Piece:
    COOL = 30

    def __init__(self, x, y, health):
        self.x = x
        self.y = y
        self.health = health
        self.shape_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down = 0

    def create(self, screen):
        screen.blit(self.shape_img, (self.x, self.y))
        for laser in self.lasers:
            laser.create(screen)

    def get_width(self):
        return self.shape_img.get_width()

    def get_height(self):
        return self.shape_img.get_height()

    def fire(self):
        if self.cool_down == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down = 1

    def laser_cool_down(self):
        if self.cool_down >= self.COOL:
            self.cool_down = 0
        elif self.cool_down > 0:
            self.cool_down += 1

    def lasers_move(self, speed, item):
        self.laser_cool_down()
        for laser in self.lasers:
            laser.fire(speed)
            if laser.is_off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.hit(item):
                if laser in self.lasers:
                    self.lasers.remove(laser)
                    return True


class Alien(Piece):
    def __init__(self, x, y, health):
        super().__init__(x, y, health)
        self.shape_img = alien_img
        self.laser_img = alien_laser_image
        self.max_health = health
        self.mask = pygame.mask.from_surface(self.shape_img)

    def lasers_move(self, speed, items):
        self.laser_cool_down()
        for laser in self.lasers:
            laser.fire(speed)
            if laser.is_off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for item in items:
                    if laser.hit(item):
                        items.remove(item)
                        self.lasers.remove(laser)

    def fire(self):
        if self.cool_down == 0:
            laser = Laser(self.x + 15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down = 1


class Ufo(Piece):
    def __init__(self, x, y, health):
        super().__init__(x, y, health)
        self.shape_img = ufo_image
        self.laser_img = ufo_laser_image
        self.mask = pygame.mask.from_surface(self.shape_img)

    def move(self, y_dist, x_dist):
        self.y += y_dist
        self.x += x_dist


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def create(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def fire(self, speed):
        self.y += speed

    def is_off_screen(self, height):
        if self.y >= height or self.y <= 0:
            return True
        else:
            return False

    def hit(self, item):
        return contact(item, self)


# Initializing pygame
pygame.init()

# Variables and Constants
WIDTH, HEIGHT = 900, 900

# Load Images
BG = pygame.image.load('images/space_bg900x900.jpg')
alien_img = pygame.image.load('images/alien.gif')
ufo_image = pygame.image.load('images/ufo50.gif')
alien_laser_image = pygame.image.load('images/dots.gif')
ufo_laser_image = pygame.image.load('images/dots_enemy.gif')

# Create Screen
space = pygame.display.set_mode(size=(WIDTH, HEIGHT))
pygame.display.set_caption("Clone Invaders")


def contact(item_1, item_2):
    x_offset = item_2.x - item_1.x
    y_offset = item_2.y - item_1.y
    return item_1.mask.overlap(item_2.mask, (x_offset, y_offset)) != None


def menu():
    menu_font = pygame.font.Font('Atari.ttf', 57)
    sub_font = pygame.font.Font('Atari.ttf', 25)
    game_is_on = True
    while game_is_on:
        space.blit(BG, (0, 0))
        menu_text = menu_font.render("Clone Invaders!", True, '#40DFEF')
        space.blit(menu_text, ((WIDTH - menu_text.get_width()) / 2, 150))
        sub_text = sub_font.render("Hit ENTER to battle the ufos...", True, '#40DFEF')
        space.blit(sub_text, ((WIDTH - sub_text.get_width()) / 2, 225))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_is_on = False
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            game_is_on = False
            sys.exit()
        elif keys[pygame.K_RETURN]:
            play()

    pygame.quit()


def play():
    game_is_on = True
    game_over = False
    FPS = 60
    end_game_count = 0
    score = 0
    lives = 7
    level = 0
    alien_move_speed = 7
    laser_speed = 5
    small_font = pygame.font.Font('Atari.ttf', 14)
    large_font = pygame.font.Font('Atari.ttf', 52)

    ufos = []
    ufo_wave_size = 4
    ufo_fire_freq = 20
    y_dist = 0.1
    x_dist = 0.5

    alien = Alien(400, 775, health=100)

    clock = pygame.time.Clock()

    def draw_screen():
        space.blit(BG, (0, 0))
        display_level()
        display_title()
        display_score()
        display_lives()

        if game_over:
            display_game_over()

        for ufo in ufos:
            ufo.create(space)

        alien.create(space)



        pygame.display.update()

    def display_score():
        score_text = small_font.render(f"Score: {score}", True, '#40DFEF')
        space.blit(score_text, (10, 30))

    def display_lives():
        lives_text = small_font.render(f"Lives: {lives}", True, '#40DFEF')
        space.blit(lives_text, (10, 50))

    def display_level():
        level_text = small_font.render(f"Level: {level}", True, '#40DFEF')
        space.blit(level_text, (10, 10))

    def display_title():
        title_text = large_font.render('CLONE INVADERS!', True, '#40DFEF')
        space.blit(title_text, (150, 13))

    def display_game_over():
        game_over_label = large_font.render("GAME OVER", True, '#E78EA9')
        space.blit(game_over_label,
                   ((game_over_label.get_width() - WIDTH) / 2, (game_over_label.get_height() - HEIGHT) / 2))
        menu()

    while game_is_on:
        clock.tick(FPS)
        draw_screen()

        # Check for Game Over
        if lives == 0:
            game_over = True
            menu()

        # Check Level-Up
        if len(ufos) == 0:
            level += 1
            lives += 1
            ufo_wave_size += 3
            x_dist += 0.025
            y_dist += 0.02
            ufo_fire_freq -= 1
            for n in range(ufo_wave_size):
                ufo = Ufo(x=randint(50, WIDTH - 75), y=randint(0, 300), health=100)
                ufos.append(ufo)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_is_on = False
                sys.exit()

        # Check Keys Pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]: #Quit
            game_is_on = False
            sys.exit()
        elif keys[pygame.K_a] and alien.x - alien_move_speed > -25: #Move Left
            alien.x -= alien_move_speed
        elif keys[pygame.K_s] and alien.x + alien_move_speed < WIDTH - alien.get_width() + 22: #Move Right
            alien.x += alien_move_speed
        elif keys[pygame.K_SPACE]:
            alien.fire()

        # move ufos
        for ufo in ufos[:]:
            if ufo.x > 840 or ufo.x < 20:
                x_dist *= -1
            # ufo fire
            if randint(0, ufo_fire_freq * 50) == 0:
                ufo.fire()
            elif ufo.y + ufo.get_height() > HEIGHT:
                lives -= 1
                ufos.remove(ufo)
            elif contact(ufo, alien):
                lives -= 1
                ufos.remove(ufo)

            ufo.move(y_dist, x_dist)
            if ufo.lasers_move(laser_speed, alien):
                lives -= 1

        alien.lasers_move(-laser_speed, ufos)

menu()
