import pygame

# Initialize Pygame and set up screen size
pygame.init()
WIDTH, HEIGHT = 800, 600  # Adjust the window size as needed
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Game")

cell_size = 20  # Cell size for maze grid