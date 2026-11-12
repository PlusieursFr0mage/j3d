import pygame
import chunk

pygame.init()


zoom = 4

screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()

running = True

display = pygame.Surface((1920 // zoom, 1080 // zoom))

characterImage = pygame.image.load("./Ressources/Outline/MiniCavalierMan.png").convert()
characterImage.set_colorkey((255, 255, 255))

tileImage = pygame.image.load("tile.png").convert_alpha()
#tileImage.set_colorkey((0, 0, 0))

x,y = 0, 0

velocity = 20

while running:   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEWHEEL:
            zoom = max(1, min(6, zoom + event.y))
            display = pygame.Surface((1920 // zoom, 1080 // zoom))
    
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

    display.fill((0, 0, 0))

    for j, row in enumerate(chunk.chunk):
        for i, tile in enumerate(row):
            if tile :
                display.blit(tileImage, (1920 // 8 + i * 16 - j * 16 - x, 1080 // 8 + i * 8 + j * 8 - y))

    display.blit(characterImage, (1920 // 8, 1080 // 8))
    pygame.transform.scale(display, screen.get_size(), screen)
    pygame.display.flip()
    pygame.display.update()

    clock.tick(120)

pygame.quit()
