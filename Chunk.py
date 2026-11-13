import pygame
import chunk 

class Chunk:

    SIZE = 16
    CHUNK_WIDTH = 512
    CHUNK_HEIGHT = 272

    def __init__(self, biome_id :float, screen :pygame.Surface):
        self.biome_id = biome_id
        self.screen  = screen
    
    def chunk_render(self) -> pygame.Surface:
        
        #Toile temporaire en attendant la méthode de génération des chunk
        tileImage = pygame.image.load("tile.png").convert_alpha() 
        
        render = pygame.Surface((self.CHUNK_WIDTH, self.CHUNK_HEIGHT), pygame.SRCALPHA)
        
        for j, row in enumerate(chunk.chunk):
            for i, tile in enumerate(row):
                if tile:
                    render.blit(tileImage, ((240) + ((i - j) * 16), (0) + ((i + j) * 8))) 
        return render
    
    def chunk_draw(self, chunk :pygame.Surface, cx :int, cy :int, scale :int) -> None:
        self.screen.blit(pygame.transform.scale(chunk, (self.CHUNK_WIDTH * scale, self.CHUNK_HEIGHT * scale)), (cx, cy)) 
