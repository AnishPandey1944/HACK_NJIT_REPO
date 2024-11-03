import pygame
import serial
import time

ser = serial.Serial('COM11', 9600)
time.sleep(2)

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)      
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(100, SCREEN_HEIGHT - 75))
        self.velocity_y = 0
        self.on_ground = False

    def update(self):
        self.velocity_y += GRAVITY          
        self.rect.y += self.velocity_y
        if self.rect.bottom >= SCREEN_HEIGHT - 25:
            self.rect.bottom = SCREEN_HEIGHT - 25
            self.velocity_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def jump(self):
        if self.on_ground:
            self.velocity_y = -JUMP_STRENGTH

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH + 25, SCREEN_HEIGHT - 75))

    def update(self):
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Obstacle Jumping Game")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    score = 0
    spawn_obstacle_timer = 0
    spawn_obstacle_interval = 1500

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                    ser.write(b'11')

        all_sprites.update()

        spawn_obstacle_timer += clock.get_time()
        if spawn_obstacle_timer >= spawn_obstacle_interval:
            obstacle = Obstacle()
            obstacles.add(obstacle)
            all_sprites.add(obstacle)
            spawn_obstacle_timer = 0

        if pygame.sprite.spritecollide(player, obstacles, False):
            running = False

        screen.fill(WHITE)
        all_sprites.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)

    ser.close()
    pygame.quit()

if __name__ == "__main__":
    main()
