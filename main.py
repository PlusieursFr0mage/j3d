import pygame
import chunk
from Chunk import Chunk 

pygame.init()

width, height = 2460, 1440

zoom = 5

border = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

running = True
characterImage = pygame.image.load("./Ressources/Outline/MiniCavalierMan.png").convert()
characterImage.set_colorkey((0, 0, 0))

x,y = 0, 0

velocity = 20

c = Chunk(1, border)
while running:   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            print(x,y)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_q]:
        x -= 16 / velocity
        y -= 8 / velocity
    if keys[pygame.K_d]:
        x += 16 /velocity
        y += 8 / velocity
    if keys[pygame.K_z]:
        y -= 8 / velocity
        x += 16 / velocity
    if keys[pygame.K_s]:
        y += 8 / velocity
        x -= 16 / velocity

    border.fill((255, 255, 255))
    
    chunk = c.chunk_render()
    c.chunk_draw(chunk, width / 2 + x, height / 2 + y, scale = 5)

    border.blit(pygame.transform.scale(characterImage, (64, 64)), (width // 2, height // 2))
    pygame.display.flip()
    clock.tick(120)

pygame.quit()
