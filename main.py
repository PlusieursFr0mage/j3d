import pygame
import chunk
import math
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

velocity = 1

c1 = Chunk(1, border)
c2 = Chunk(1, border)
c3 = Chunk(1, border)
c4 = Chunk(1, border)

"""
    Généré avec CLAUDE, passage par la matrice inverse pour éffectuer un chagement de base 
    sans passer par la projection. (Ce que je me suis embêter à faire)
"""

THETA = math.atan(0.5)      # 26,565° : le 2:1 du pixel art (ton cas)
L = 16 / math.cos(THETA)    # pour que L·cos θ = 16 px, soit TW / 2

def uv_to_xy(u, v) -> int:
    c, s = L * math.cos(THETA), L * math.sin(THETA)
    return int(c * (u - v)), int(s * (u + v))

def xy_to_uv(x, y) -> int:
    c, s = L * math.cos(THETA), L * math.sin(THETA)
    return int((x / c + y / s) / 2), int((y / s - x / c) / 2)


while running:   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            print(xy_to_uv(x,y))
           
            
    keys = pygame.key.get_pressed()

    if keys[pygame.K_d]:
        x -= 16 / velocity
        y -= 8 / velocity
    if keys[pygame.K_q]:
        x += 16 /velocity
        y += 8 / velocity
    if keys[pygame.K_s]:
        y -= 8 / velocity
        x += 16 / velocity
    if keys[pygame.K_z]:
        y += 8 / velocity
        x -= 16 / velocity

    border.fill((255, 255, 255))
    

    c4.chunk_draw(c4.chunk_render(), x + int((512*zoom) / 2), y - (272*5)/2+40, scale = zoom)
    c1.chunk_draw(c1.chunk_render(), x, y, scale = zoom)
    c2.chunk_draw(c2.chunk_render(), x + (512*zoom), y, scale = zoom)
    c3.chunk_draw(c3.chunk_render(), x + int((512*zoom) / 2), y + (272*5)/2-40, scale = zoom)
   
    border.blit(pygame.transform.scale(characterImage, (64, 64)), (width // 2, height // 2))
    pygame.display.flip()
    clock.tick(120)
pygame.quit()
