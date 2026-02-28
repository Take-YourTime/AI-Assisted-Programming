from typing import Any
import pygame
from initialization import WIDTH, HEIGHT, screen, cell_size

class Player(pygame.sprite.Sprite):
    raw_image = [pygame.image.load(("pacman.png")).convert_alpha(),
                 pygame.image.load(("pacman2.png")).convert_alpha()]
    
    def __init__(self, width, height) -> None:
        super().__init__()
        self.runimage = [   pygame.transform.scale(Player.raw_image[0], (width, height)),
                            pygame.transform.scale(Player.raw_image[1], (width, height))]
        self.image = self.runimage[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (19, 16)
        self.mask = pygame.mask.from_surface(self.image)
        self.width = width
        self.height = height
        self.direction = 'N'
        self.index = 0
    
    def update(self, maze, ghostGroup) -> bool:
        self.index += 1
        if self.index >= 20:
            self.index = 0
        self.image = self.runimage[self.index // 10]

        self.eatDot(maze)

        for ghost in ghostGroup:
            if ghost.rect.colliderect(self.rect):
                if ghost.mask.overlap(self.mask, (self.rect.left  * cell_size - ghost.rect.left  * cell_size, self.rect.top  * cell_size - ghost.rect.top  * cell_size)):
                    self.kill()
                    return False
        return True

                    

    def draw(self):
        x, y = self.rect.topleft[0] * cell_size, self.rect.topleft[1] * cell_size
        screen.blit(self.image, (x, y))
    
    def eatDot(self, maze):
        # Eat dot
        if maze[self.rect.topleft[1]][self.rect.topleft[0]] == 0:
            maze[self.rect.topleft[1]][self.rect.topleft[0]] = 3
    
    def move(self, maze):
        match self.direction:
            case 'N':
                self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1] - 1)
            case 'S':
                self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1] + 1)
            case 'W':
                self.rect.topleft = (self.rect.topleft[0] - 1, self.rect.topleft[1])
            case 'E':
                self.rect.topleft = (self.rect.topleft[0] + 1, self.rect.topleft[1])
        
        if maze[self.rect.topleft[1]][self.rect.topleft[0]] == 1:
            # Revert move if hitting wall
            match self.direction:
                case 'N':
                    self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1] + 1)
                case 'S':
                    self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1] - 1)
                case 'W':
                    self.rect.topleft = (self.rect.topleft[0] + 1, self.rect.topleft[1])
                case 'E':
                    self.rect.topleft = (self.rect.topleft[0] - 1, self.rect.topleft[1])

    def turnSide(self):
        match self.direction:
            case 'N':
                self.runimage[0] = pygame.transform.rotate(Player.raw_image[0], 90)
                self.runimage[1] = pygame.transform.rotate(Player.raw_image[1], 90)
                self.runimage[0] = pygame.transform.scale(self.runimage[0], (self.width, self.height))
                self.runimage[1] = pygame.transform.scale(self.runimage[1], (self.width, self.height))
                #self.image = pygame.transform.scale(self.image, (self.width, self.height))
            case 'S':
                self.runimage[0] = pygame.transform.rotate(Player.raw_image[0], 270)
                self.runimage[1] = pygame.transform.rotate(Player.raw_image[1], 270)
                self.runimage[0] = pygame.transform.scale(self.runimage[0], (self.width, self.height))
                self.runimage[1] = pygame.transform.scale(self.runimage[1], (self.width, self.height))
                #self.image = pygame.transform.scale(self.image, (self.width, self.height))
            case 'W':
                self.runimage[0] = pygame.transform.rotate(Player.raw_image[0], 180)
                self.runimage[1] = pygame.transform.rotate(Player.raw_image[1], 180)
                self.runimage[0] = pygame.transform.scale(self.runimage[0], (self.width, self.height))
                self.runimage[1] = pygame.transform.scale(self.runimage[1], (self.width, self.height))
                #self.image = pygame.transform.scale(self.image, (self.width, self.height))
            case 'E':
                self.runimage[0] = pygame.transform.rotate(Player.raw_image[0], 0)
                self.runimage[1] = pygame.transform.rotate(Player.raw_image[1], 0)
                self.runimage[0] = pygame.transform.scale(self.runimage[0], (self.width, self.height))
                self.runimage[1] = pygame.transform.scale(self.runimage[1], (self.width, self.height))  
                #self.image = pygame.transform.scale(self.image, (self.width, self.height))
