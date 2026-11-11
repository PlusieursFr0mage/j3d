import pygame
import chunk

pygame.init()

screen = pygame.display.set_mode((3000, 2000))
clock = pygame.time.Clock()
running = True


chunkSize = 16
display = pygame.Surface((chunkSize*100, chunkSize*100))
mapSize = len(chunk.chunk)

while running:
    display.fill((0, 0, 0))
   

    for j, row in enumerate(chunk.chunk):
        for i, tile in enumerate(row):
            if tile :
                pygame.draw.rect(display, (255, 255, 255), pygame.Rect(j*100, i*100, 100, 100), 1)

        

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(display, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
