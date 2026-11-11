#!/usr/bin/env python3
"""
Prototype de rendu isométrique (style ISO-CORE) en Python.

Installation :   pip install pygame-ce
Lancement   :    python iso_proto.py

Contrôles :
    ZQSD / WASD / flèches : se déplacer
    R                     : générer un nouveau monde
    Échap                 : quitter

Ce que montre ce prototype :
    - projection isométrique 2:1 avec relief (blocs en hauteur)
    - monde infini généré à la volée par chunks (bruit fractal)
    - biomes : eau, plage, prairie, forêt, désert, montagne, neige
    - décors (arbres, cactus, pins, rochers, fleurs), eau animée
    - rendu basse résolution agrandi x2 pour l'effet pixel art
"""
import math
import random
import sys

import pygame

# --------------------------------------------------------------------------
# Réglages
# --------------------------------------------------------------------------
SCREEN_W, SCREEN_H = 3600, 1440
SCALE = 2                                   # rendu interne puis zoom x2
VIEW_W, VIEW_H = SCREEN_W // SCALE, SCREEN_H // SCALE
TILE_W, TILE_H = 32, 16                     # losange 2:1
HALF_W, HALF_H = TILE_W // 2, TILE_H // 2
BLOCK_H = 8                                 # hauteur (px) d'un niveau de relief
CHUNK = 16                                  # taille d'un chunk (puissance de 2)
CHUNK_SHIFT = 4                             # log2(CHUNK)
VIEW_RADIUS = 24                            # rayon (en tuiles) autour du joueur
PLAYER_SPEED = 5.0                          # tuiles / seconde
BACKGROUND = (16, 22, 36)

# Biomes
DEEP, WATER, SAND, GRASS, FOREST, DESERT, ROCK, SNOW = range(8)
BASE_COLORS = [
    (28, 62, 135),     # eau profonde
    (46, 104, 184),    # eau peu profonde
    (226, 208, 146),   # plage
    (104, 172, 82),    # prairie
    (64, 140, 68),     # forêt
    (216, 184, 112),   # désert
    (128, 128, 138),   # montagne
    (238, 243, 250),   # neige
]
BIOME_NAMES = ["Eau profonde", "Eau", "Plage", "Prairie",
               "Forêt", "Désert", "Montagne", "Neige"]

# Décors
NONE, TREE, PINE, CACTUS, BOULDER, FLOWER = range(6)
BLOCKING = {TREE, PINE, CACTUS, BOULDER}


# --------------------------------------------------------------------------
# Bruit (value noise + fractal), sans dépendance externe
# --------------------------------------------------------------------------
def _hash(ix, iy, seed):
    n = (ix * 374761393 + iy * 668265263 + seed * 144665) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def _smooth(t):
    return t * t * (3 - 2 * t)


def value_noise(x, y, seed):
    x0, y0 = math.floor(x), math.floor(y)
    fx, fy = _smooth(x - x0), _smooth(y - y0)
    a = _hash(x0, y0, seed)
    b = _hash(x0 + 1, y0, seed)
    c = _hash(x0, y0 + 1, seed)
    d = _hash(x0 + 1, y0 + 1, seed)
    top = a + (b - a) * fx
    bottom = c + (d - c) * fx
    return top + (bottom - top) * fy


def fbm(x, y, seed, octaves=4):
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for i in range(octaves):
        total += value_noise(x * freq, y * freq, seed + i * 101) * amp
        norm += amp
        amp *= 0.5
        freq *= 2.0
    return total / norm


# --------------------------------------------------------------------------
# Monde généré par chunks
# --------------------------------------------------------------------------
class World:
    """Une tuile = (biome, niveau_de_relief, décor, variante_de_teinte)."""

    def __init__(self, seed):
        self.seed = seed
        self.chunks = {}

    def get(self, x, y):
        key = (x >> CHUNK_SHIFT, y >> CHUNK_SHIFT)
        chunk = self.chunks.get(key)
        if chunk is None:
            chunk = self.chunks[key] = self._generate_chunk(*key)
        return chunk[y & (CHUNK - 1)][x & (CHUNK - 1)]

    def _generate_chunk(self, cx, cy):
        rows = []
        for ly in range(CHUNK):
            row = []
            for lx in range(CHUNK):
                x, y = cx * CHUNK + lx, cy * CHUNK + ly
                altitude = fbm(x * 0.035, y * 0.035, self.seed, 5)
                moisture = fbm(x * 0.05 + 500, y * 0.05 + 500, self.seed + 7, 3)
                row.append(self._make_tile(x, y, altitude, moisture))
            rows.append(row)
        return rows

    def _make_tile(self, x, y, h, m):
        r = _hash(x, y, self.seed + 99)
        k = min(2, int(_hash(x, y, self.seed + 5) * 3))
        if h < 0.38:
            return (DEEP, 0, NONE, k)
        if h < 0.45:
            return (WATER, 0, NONE, k)
        if h < 0.48:
            return (SAND, 1, NONE, k)

        z = 1 + int((h - 0.48) * 16)
        if h > 0.68:
            return (SNOW, z, PINE if r < 0.10 else NONE, k)
        if h > 0.60:
            return (ROCK, z, BOULDER if r < 0.08 else NONE, k)
        if m < 0.40:
            return (DESERT, z, CACTUS if r < 0.05 else NONE, k)
        if m > 0.55:
            return (FOREST, z, TREE if r < 0.40 else NONE, k)
        deco = TREE if r < 0.04 else FLOWER if r < 0.12 else NONE
        return (GRASS, z, deco, k)

    def find_spawn(self):
        for r in range(100):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    biome, _, deco, _ = self.get(dx, dy)
                    if biome in (GRASS, FOREST) and deco == NONE:
                        return dx + 0.5, dy + 0.5
        return 0.5, 0.5


# --------------------------------------------------------------------------
# Sprites générés par code (aucun fichier image nécessaire)
# --------------------------------------------------------------------------
def make_sprites():
    sprites = {}

    s = pygame.Surface((16, 22), pygame.SRCALPHA)
    pygame.draw.rect(s, (92, 62, 38), (7, 13, 3, 9))
    pygame.draw.circle(s, (40, 110, 52), (8, 8), 7)
    pygame.draw.circle(s, (62, 150, 70), (6, 6), 4)
    sprites[TREE] = s

    s = pygame.Surface((14, 24), pygame.SRCALPHA)
    pygame.draw.rect(s, (92, 62, 38), (6, 18, 3, 6))
    pygame.draw.polygon(s, (38, 100, 60), [(7, 6), (14, 19), (0, 19)])
    pygame.draw.polygon(s, (48, 120, 72), [(7, 0), (13, 11), (1, 11)])
    pygame.draw.polygon(s, (240, 245, 250), [(7, 0), (10, 5), (4, 5)])
    sprites[PINE] = s

    s = pygame.Surface((12, 16), pygame.SRCALPHA)
    green = (60, 140, 80)
    pygame.draw.rect(s, green, (4, 2, 4, 14))
    pygame.draw.rect(s, green, (0, 7, 4, 3))
    pygame.draw.rect(s, green, (0, 4, 3, 5))
    pygame.draw.rect(s, green, (8, 9, 4, 3))
    pygame.draw.rect(s, green, (9, 6, 3, 5))
    sprites[CACTUS] = s

    s = pygame.Surface((12, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (104, 104, 114), (0, 2, 12, 6))
    pygame.draw.ellipse(s, (150, 150, 160), (2, 0, 7, 5))
    sprites[BOULDER] = s

    s = pygame.Surface((5, 5), pygame.SRCALPHA)
    for p in [(2, 0), (0, 2), (4, 2), (2, 4)]:
        s.set_at(p, (240, 120, 160))
    s.set_at((2, 2), (255, 220, 80))
    sprites[FLOWER] = s

    return sprites


def make_player_sprites():
    body = pygame.Surface((10, 16), pygame.SRCALPHA)
    pygame.draw.rect(body, (60, 50, 90), (2, 11, 2, 5))       # jambes
    pygame.draw.rect(body, (60, 50, 90), (6, 11, 2, 5))
    pygame.draw.rect(body, (200, 70, 60), (1, 5, 8, 7))       # corps
    pygame.draw.rect(body, (240, 205, 170), (2, 0, 6, 6))     # tête
    pygame.draw.rect(body, (70, 45, 30), (2, 0, 6, 2))        # cheveux
    shadow = pygame.Surface((12, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 0, 12, 6))
    return body, shadow


# --------------------------------------------------------------------------
# Tuiles : surfaces mises en cache (clé = biome, teinte, faces latérales)
# --------------------------------------------------------------------------
_tile_cache = {}


def _shade(color, k):
    d = (k - 1) * 7
    return tuple(max(0, min(255, c + d)) for c in color)


def _darker(color, factor):
    return tuple(int(c * factor) for c in color)


def tile_surface(biome, k, left_h, right_h):
    key = (biome, k, left_h, right_h)
    surf = _tile_cache.get(key)
    if surf is not None:
        return surf

    top = _shade(BASE_COLORS[biome], k)
    surf = pygame.Surface((TILE_W, TILE_H + max(left_h, right_h)), pygame.SRCALPHA)

    def face(color, pts):
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.polygon(surf, color, pts, 1)   # évite les micro-fentes

    if left_h:
        face(_darker(top, 0.78), [(0, HALF_H), (HALF_W, TILE_H),
                                  (HALF_W, TILE_H + left_h), (0, HALF_H + left_h)])
    if right_h:
        face(_darker(top, 0.60), [(HALF_W, TILE_H), (TILE_W, HALF_H),
                                  (TILE_W, HALF_H + right_h), (HALF_W, TILE_H + right_h)])
    face(top, [(HALF_W, 0), (TILE_W, HALF_H), (HALF_W, TILE_H), (0, HALF_H)])

    _tile_cache[key] = surf
    return surf


# --------------------------------------------------------------------------
# Rendu
# --------------------------------------------------------------------------
def draw_world(canvas, world, sprites, player, t):
    px, py, pz, cam_x, cam_y, moving = player
    body, shadow = player_sprites
    ox = VIEW_W // 2 - cam_x
    oy = VIEW_H // 2 - cam_y
    ix, iy = math.floor(px), math.floor(py)
    R = VIEW_RADIUS

    for y in range(iy - R, iy + R + 1):
        for x in range(ix - R, ix + R + 1):
            sx = int((x - y) * HALF_W - HALF_W + ox)
            base_sy = int((x + y) * HALF_H + oy)

            # Élimination rapide des tuiles hors écran
            if sx < -TILE_W or sx > VIEW_W:
                continue
            if base_sy + TILE_H < 0 or base_sy - 64 > VIEW_H:
                continue

            biome, z, deco, k = world.get(x, y)
            if biome <= WATER:      # eau animée : la teinte oscille
                k = int((math.sin(t * 1.4 + (x + y) * 0.6) + 1) * 1.49)

            left_h = max(0, z - world.get(x, y + 1)[1]) * BLOCK_H
            right_h = max(0, z - world.get(x + 1, y)[1]) * BLOCK_H
            sy = base_sy - z * BLOCK_H

            canvas.blit(tile_surface(biome, k, left_h, right_h), (sx, sy))

            if deco:
                spr = sprites[deco]
                canvas.blit(spr, (sx + HALF_W - spr.get_width() // 2,
                                  sy + HALF_H - spr.get_height() + 2))

            # Le joueur est dessiné juste après sa propre tuile :
            # les tuiles "devant" lui le recouvrent correctement.
            if x == ix and y == iy:
                fx = int((px - py) * HALF_W + ox)
                fy = int((px + py) * HALF_H - pz * BLOCK_H + oy)
                bob = -1 if (moving and math.sin(t * 14) > 0) else 0
                canvas.blit(shadow, (fx - 6, fy - 3))
                canvas.blit(body, (fx - 5, fy - 15 + bob))


def can_stand(world, x, y, z_from):
    biome, z, deco, _ = world.get(math.floor(x), math.floor(y))
    if biome == DEEP or deco in BLOCKING:
        return False
    return abs(z - z_from) <= 1


# --------------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------------
def main():
    global player_sprites
    shot = None
    if "--shot" in sys.argv:                    # option de test : capture d'écran
        shot = sys.argv[sys.argv.index("--shot") + 1]

    pygame.init()
    pygame.display.set_caption("Prototype isométrique - style ISO-CORE")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    canvas = pygame.Surface((VIEW_W, VIEW_H))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    sprites = make_sprites()
    player_sprites = make_player_sprites()

    seed = random.randint(0, 99999)
    world = World(seed)
    px, py = world.find_spawn()
    pz = float(world.get(math.floor(px), math.floor(py))[1])
    cam_x = (px - py) * HALF_W
    cam_y = (px + py) * HALF_H - pz * BLOCK_H
    t, frame = 0.0, 0

    running = True
    while running:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        t += dt
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    seed = random.randint(0, 99999)
                    world = World(seed)
                    px, py = world.find_spawn()
                    pz = float(world.get(math.floor(px), math.floor(py))[1])

        # --- Déplacement (directions "écran" converties en directions grille)
        keys = pygame.key.get_pressed()
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        left = keys[pygame.K_q] or keys[pygame.K_a] or keys[pygame.K_LEFT]
        down = keys[pygame.K_s] or keys[pygame.K_DOWN]
        up = keys[pygame.K_z] or keys[pygame.K_w] or keys[pygame.K_UP]
        dx_in = int(bool(right)) - int(bool(left))
        dy_in = int(bool(down)) - int(bool(up))
        gx, gy = dx_in + dy_in, -dx_in + dy_in
        length = math.hypot(gx, gy)
        moving = length > 0
        if moving:
            gx, gy = gx / length * PLAYER_SPEED * dt, gy / length * PLAYER_SPEED * dt
            cur_z = world.get(math.floor(px), math.floor(py))[1]
            if can_stand(world, px + gx, py, cur_z):
                px += gx
            if can_stand(world, px, py + gy, cur_z):
                py += gy

        # --- Hauteur et caméra lissées
        tile_z = world.get(math.floor(px), math.floor(py))[1]
        pz += (tile_z - pz) * min(1.0, 12 * dt)
        target_x = (px - py) * HALF_W
        target_y = (px + py) * HALF_H - pz * BLOCK_H
        cam_x += (target_x - cam_x) * min(1.0, 8 * dt)
        cam_y += (target_y - cam_y) * min(1.0, 8 * dt)

        # --- Rendu
        canvas.fill(BACKGROUND)
        draw_world(canvas, world, sprites,
                   (px, py, pz, int(cam_x), int(cam_y), moving), t)
        pygame.transform.scale(canvas, (SCREEN_W, SCREEN_H), screen)

        biome = world.get(math.floor(px), math.floor(py))[0]
        lines = [
            "ZQSD / flèches : se déplacer   R : nouveau monde   Échap : quitter",
            f"Biome : {BIOME_NAMES[biome]}   Seed : {seed}   "
            f"Chunks : {len(world.chunks)}   FPS : {clock.get_fps():.0f}",
        ]
        for i, text in enumerate(lines):
            screen.blit(font.render(text, True, (0, 0, 0)), (11, 11 + i * 22))
            screen.blit(font.render(text, True, (255, 255, 255)), (10, 10 + i * 22))

        pygame.display.flip()

        if shot and frame == 5:
            pygame.image.save(screen, shot)
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
