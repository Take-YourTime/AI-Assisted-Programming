import pygame
from initialization import WIDTH, HEIGHT, screen, cell_size

# pacman ghost
class Ghost(pygame.sprite.Sprite):
    raw_image = [   pygame.image.load(("ghost.png")).convert_alpha(),
                    pygame.image.load(("ghost1.png")).convert_alpha(),
                    pygame.image.load(("ghost2.png")).convert_alpha(),
                    pygame.image.load(("ghost3.png")).convert_alpha()]

    def __init__(self, width, height, location, index) -> None:
        super().__init__()
        self.image = pygame.transform.scale(Ghost.raw_image[index], (width, height))
        self.rect = self.image.get_rect()
        self.rect.topleft = location
        self.mask = pygame.mask.from_surface(self.image)
        self.width = width
        self.height = height
        self.direction = 'N'

    
    def update(self, player, maze):
        self.move(maze, player)

    def move(self, maze, player):
        if maze[self.rect.topleft[1]][self.rect.topleft[0]] == 2:
            self.turnSide(player)
        
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

    # turn side
    def turnSide(self, player):
        x = player[0] - self.rect.topleft[0]
        y = player[1] - self.rect.topleft[1]

        # if the absolute value of x is greater than the absolute value of y
        if(abs(x) > abs(y)):
            if(x > 0):
                self.direction = 'E'
            else:
                self.direction = 'W'
        else:
            if(y > 0):
                self.direction = 'S'
            else:
                self.direction = 'N'
    
    def draw(self, screen):
        x, y = self.rect.topleft[0] * cell_size, self.rect.topleft[1] * cell_size
        screen.blit(self.image, (x, y))