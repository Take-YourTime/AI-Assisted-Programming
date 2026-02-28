import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys


class SmallCube:
    def __init__(self, position, colors):
        """
        Initialize a single small cube.
        :param position: Tuple of (x, y, z) position
        :param colors: Dictionary of face colors {'U': (R, G, B), 'D': (R, G, B), ...}
        """
        self.position = position
        self.colors = colors

    def draw(self, size=0.45):
        """
        Draw this cubelet with the given size.
        """
        # Each face's normal direction and vertex coordinates
        faces = {
            (0, 0, 1): [(-size, -size, size), (size, -size, size), (size, size, size), (-size, size, size)],  # Front
            (0, 0, -1): [(-size, -size, -size), (-size, size, -size), (size, size, -size), (size, -size, -size)],  # Back
            (0, 1, 0): [(-size, size, -size), (-size, size, size), (size, size, size), (size, size, -size)],  # Top
            (0, -1, 0): [(-size, -size, -size), (size, -size, -size), (size, -size, size), (-size, -size, size)],  # Bottom
            (-1, 0, 0): [(-size, -size, -size), (-size, -size, size), (-size, size, size), (-size, size, -size)],  # Left
            (1, 0, 0): [(size, -size, -size), (size, size, -size), (size, size, size), (size, -size, size)],  # Right
        }

        # Translate to the cubelet's position
        glPushMatrix()
        glTranslatef(*self.position)

        # Draw each face
        for normal, vertices in faces.items():
            if normal in self.colors:  # Only draw faces with defined colors
                glBegin(GL_QUADS)
                glColor3fv(self.colors[normal])
                for vertex in vertices:
                    glVertex3fv(vertex)
                glEnd()

        glPopMatrix()

    def is_clicked(self, ray_origin, ray_direction, size=0.45):
        """
        Check if the ray intersects this cube.
        :param ray_origin: The origin of the ray
        :param ray_direction: The direction of the ray
        :param size: Half-size of the cube (default: 0.45)
        :return: True if clicked, False otherwise
        """
        min_bound = [self.position[i] - size for i in range(3)]
        max_bound = [self.position[i] + size for i in range(3)]

        t_min = -float("inf")
        t_max = float("inf")

        for i in range(3):
            if ray_direction[i] != 0:
                t1 = (min_bound[i] - ray_origin[i]) / ray_direction[i]
                t2 = (max_bound[i] - ray_origin[i]) / ray_direction[i]
                t_min = max(t_min, min(t1, t2))
                t_max = min(t_max, max(t1, t2))
            elif ray_origin[i] < min_bound[i] or ray_origin[i] > max_bound[i]:
                return False

        return t_max >= t_min >= 0


class RubiksCube:
    def __init__(self):
        """
        Initialize a 3x3 Rubik's Cube composed of 27 SmallCubes.
        """
        self.cubelets = []
        self.create_cube()

    def create_cube(self):
        """
        Create the 3x3 Rubik's Cube by instantiating SmallCube objects.
        """
        # Standard Rubik's Cube face colors
        color_map = {
            "U": (1, 1, 1),  # White
            "D": (1, 1, 0),  # Yellow
            "F": (0, 1, 0),  # Green
            "B": (0, 0, 1),  # Blue
            "L": (1, 0.5, 0),  # Orange
            "R": (1, 0, 0),  # Red
        }

        # Define positions for a 3x3 cube
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    # Assign colors to the visible faces of the cubelet
                    colors = {}
                    if x == -1:
                        colors[(-1, 0, 0)] = color_map["L"]
                    if x == 1:
                        colors[(1, 0, 0)] = color_map["R"]
                    if y == -1:
                        colors[(0, -1, 0)] = color_map["D"]
                    if y == 1:
                        colors[(0, 1, 0)] = color_map["U"]
                    if z == -1:
                        colors[(0, 0, -1)] = color_map["B"]
                    if z == 1:
                        colors[(0, 0, 1)] = color_map["F"]

                    # Add a new SmallCube to the list
                    self.cubelets.append(SmallCube((x, y, z), colors))

    def draw(self):
        """
        Draw the entire Rubik's Cube.
        """
        for cubelet in self.cubelets:
            cubelet.draw()


class RubiksCube3DApp:
    def __init__(self):
        pygame.init()
        display = (800, 600)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -8)

        self.rot_x, self.rot_y = 30, -30
        self.mouse_down = False

        # Enable depth testing to hide faces behind the visible ones
        glEnable(GL_DEPTH_TEST)

        # Initialize Rubik's Cube
        self.rubiks_cube = RubiksCube()

    def handle_mouse_click(self, x, y):
        """
        Handle a mouse click and detect the clicked cube.
        """
        # Get the ray direction in world space
        viewport = glGetIntegerv(GL_VIEWPORT)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)

        win_x = x
        win_y = viewport[3] - y
        win_z = glReadPixels(win_x, win_y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)

        ray_origin = gluUnProject(win_x, win_y, win_z, modelview, projection, viewport)
        ray_far = gluUnProject(win_x, win_y, 1, modelview, projection, viewport)
        ray_direction = [ray_far[i] - ray_origin[i] for i in range(3)]

        # Check each cubelet for intersection
        for cubelet in self.rubiks_cube.cubelets:
            if cubelet.is_clicked(ray_origin, ray_direction):
                print(f"Clicked cube at position {cubelet.position}, colors: {cubelet.colors}")
                break

    def handle_events(self):
        """
        Handle user inputs for interaction.
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.handle_mouse_click(*event.pos)
            elif event.type == MOUSEMOTION:
                if self.mouse_down:
                    dx, dy = event.rel
                    self.rot_x += dy
                    self.rot_y += dx

    def main_loop(self):
        """
        Main rendering loop.
        """
        while True:
            self.handle_events()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear the color and depth buffers
            glPushMatrix()
            glRotatef(self.rot_x, 1, 0, 0)
            glRotatef(self.rot_y, 0, 1, 0)
            self.rubiks_cube.draw()
            glPopMatrix()
            pygame.display.flip()
            pygame.time.wait(10)


if __name__ == "__main__":
    app = RubiksCube3DApp()
    app.main_loop()
