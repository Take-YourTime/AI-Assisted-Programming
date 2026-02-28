import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import random
import copy
import math

# initialize Pygame and OpenGL
pygame.init()

# Constants
LEFT = 1
RIGHT = 3

# Rubik's Cube Data Structure
class RubiksCube:
    def __init__(self):
        # Initialize a solved cube
        # U: White (W), D: Yellow (Y), F: Green (G), B: Blue (B), L: Orange (O), R: Red (R)
        self.faces = {
            'U': [['W'] * 3 for _ in range(3)],
            'D': [['Y'] * 3 for _ in range(3)],
            'F': [['G'] * 3 for _ in range(3)],
            'B': [['B'] * 3 for _ in range(3)],
            'L': [['O'] * 3 for _ in range(3)],
            'R': [['R'] * 3 for _ in range(3)]
        }

    def rotate_face_clockwise(self, face):
        # Rotate a face 90 degrees clockwise
        self.faces[face] = [list(row) for row in zip(*self.faces[face][::-1])]

    def rotate_face_counterclockwise(self, face):
        # Rotate a face 90 degrees counter-clockwise
        self.faces[face] = [list(row) for row in zip(*self.faces[face])]
        self.faces[face].reverse()

    def rotate_face_180(self, face):
        # Rotate a face 180 degrees
        self.rotate_face_clockwise(face)
        self.rotate_face_clockwise(face)

    def move(self, move):
        """
        Perform a move on the cube.
        Moves are denoted by:
        - 'U', 'D', 'F', 'B', 'L', 'R' for clockwise rotations
        - 'U\'', 'D\'', 'F\'', 'B\'', 'L\'', 'R\'' for counter-clockwise
        - 'U2', 'D2', 'F2', 'B2', 'L2', 'R2' for 180-degree rotations
        """
        if move.endswith("2"):
            base_move = move[0]
            times = 2
        elif move.endswith("'"):
            base_move = move[0]
            times = -1
        else:
            base_move = move
            times = 1

        for _ in range(abs(times)):
            if times == -1:
                self._perform_move(base_move, clockwise=False)
            else:
                self._perform_move(base_move, clockwise=True)

    def _perform_move(self, face, clockwise=True):
        # Rotate the face itself
        if clockwise:
            self.rotate_face_clockwise(face)
        else:
            self.rotate_face_counterclockwise(face)

        # Define the adjacent faces and the rows/columns that are affected
        adjacent = {
            'U': [('B', 0, 'row'), ('R', 0, 'row'), ('F', 0, 'row'), ('L', 0, 'row')],
            'D': [('F', 2, 'row'), ('R', 2, 'row'), ('B', 2, 'row'), ('L', 2, 'row')],
            'F': [('U', 2, 'row'), ('R', 0, 'col'), ('D', 0, 'row'), ('L', 2, 'col')],
            'B': [('U', 0, 'row'), ('L', 0, 'col'), ('D', 2, 'row'), ('R', 2, 'col')],
            'L': [('U', 0, 'col'), ('F', 0, 'col'), ('D', 0, 'col'), ('B', 2, 'col')],
            'R': [('U', 2, 'col'), ('B', 0, 'col'), ('D', 2, 'col'), ('F', 2, 'col')]
        }

        adj = adjacent[face]

        if clockwise:
            # Save the last adjacent face's slice
            temp = self._get_slice(adj[3])
            for i in range(4):
                self._set_slice(adj[i], self._get_slice(adj[i-1]))
        else:
            # Save the first adjacent face's slice
            temp = self._get_slice(adj[0])
            for i in range(4):
                # Use modulo to prevent index out of range
                self._set_slice(adj[i], self._get_slice(adj[(i+1) % 4]))

    def _get_slice(self, face_info):
        face, idx, typ = face_info
        if typ == 'row':
            return copy.deepcopy(self.faces[face][idx])
        elif typ == 'col':
            return [self.faces[face][i][idx] for i in range(3)]
        else:
            raise ValueError("Invalid slice type")

    def _set_slice(self, face_info, values):
        face, idx, typ = face_info
        if typ == 'row':
            self.faces[face][idx] = values
        elif typ == 'col':
            for i in range(3):
                self.faces[face][i][idx] = values[i]
        else:
            raise ValueError("Invalid slice type")

    def initialize_random(self, moves=100):
        # Define all possible basic moves
        basic_moves = ['U', 'D', 'F', 'B', 'L', 'R']
        modifiers = ['', '\'', '2']

        all_moves = [m + mod for m in basic_moves for mod in modifiers]

        last_move = None
        for _ in range(moves):
            move = random.choice(all_moves)
            # Prevent repeating the same face move to avoid unnecessary complexity
            if last_move and move[0] == last_move[0]:
                continue
            self.move(move)
            last_move = move

    def is_solved(self):
        # Check if the cube is in a solved state
        for face in self.faces:
            color = self.faces[face][0][0]
            for row in self.faces[face]:
                for sticker in row:
                    if sticker != color:
                        return False
        return True

# 3D Rendering and Interaction
class RubiksCube3D:
    def __init__(self):
        try:
            # window setup
            display = (800, 600)
            pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
            
            # OpenGL setup
            gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
            glTranslatef(0.0, 0.0, -20)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_COLOR_MATERIAL)
            glEnable(GL_NORMALIZE)
            glShadeModel(GL_SMOOTH)
            print("Pygame 和 OpenGL 初始化成功。")

            self.cube = RubiksCube()
            self.cube.initialize_random(moves=100)
            print("魔術方塊初始化並已打亂。")

            # Rotation angles
            self.rot_x = 30
            self.rot_y = -30

            # Mouse control
            self.mouse_down = False
            self.last_mouse_pos = (0, 0)

            # Animation
            self.animating = False
            self.animation_axis = None
            self.animation_layer = None
            self.animation_direction = 1  # 1 for clockwise, -1 for counter-clockwise
            self.animation_angle = 0
            self.animation_speed = 5  # degrees per frame

            # Mode: 'cube_rotation' or 'side_rotation'
            self.mode = 'cube_rotation'
            self.selected_face = None  # To store which face is selected in side_rotation mode

            # Color mapping for selection (unique colors for each face)
            self.selection_colors = {
                'U': (1, 0, 0),    # Red
                'D': (0, 1, 0),    # Green
                'F': (0, 0, 1),    # Blue
                'B': (1, 1, 0),    # Yellow
                'L': (1, 0, 1),    # Magenta
                'R': (0, 1, 1)     # Cyan
            }

        except Exception as e:
            print(f"初始化錯誤: {e}")
            pygame.quit()
            sys.exit()

    def draw_cubelet(self, position, size=1, selection=False, selection_color=(0,0,0)):
        try:
            x, y, z = position
            hs = size / 2  # half size

            # Define vertices
            vertices = [
                (x - hs, y - hs, z - hs),
                (x + hs, y - hs, z - hs),
                (x + hs, y + hs, z - hs),
                (x - hs, y + hs, z - hs),
                (x - hs, y - hs, z + hs),
                (x + hs, y - hs, z + hs),
                (x + hs, y + hs, z + hs),
                (x - hs, y + hs, z + hs)
            ]

            # Define edges
            edges = (
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 0),
                (4, 5),
                (5, 6),
                (6, 7),
                (7, 4),
                (0, 4),
                (1, 5),
                (2, 6),
                (3, 7)
            )

            # Define surfaces with colors based on the cube's state
            surfaces = []
            colors = []

            # Each cubelet can have up to 6 colored faces
            # We'll check the position to determine which faces to color

            # U face (+y)
            if y == 2:
                surfaces.append((4, 5, 6, 7))
                colors.append(self.color_map(self.cube.faces['U'][1][1]))
            # D face (-y)
            if y == -2:
                surfaces.append((0, 1, 2, 3))
                colors.append(self.color_map(self.cube.faces['D'][1][1]))
            # F face (+z)
            if z == 2:
                surfaces.append((3, 2, 6, 7))
                colors.append(self.color_map(self.cube.faces['F'][1][1]))
            # B face (-z)
            if z == -2:
                surfaces.append((0, 1, 5, 4))
                colors.append(self.color_map(self.cube.faces['B'][1][1]))
            # R face (+x)
            if x == 2:
                surfaces.append((1, 2, 6, 5))
                colors.append(self.color_map(self.cube.faces['R'][1][1]))
            # L face (-x)
            if x == -2:
                surfaces.append((0, 3, 7, 4))
                colors.append(self.color_map(self.cube.faces['L'][1][1]))

            # If selection mode, override colors with unique selection colors
            if selection and self.selected_face:
                face = self.selected_face
                if face == 'U' and y == 2:
                    surfaces = [(4,5,6,7)]
                    colors = [self.selection_colors['U']]
                elif face == 'D' and y == -2:
                    surfaces = [(0,1,2,3)]
                    colors = [self.selection_colors['D']]
                elif face == 'F' and z == 2:
                    surfaces = [(3,2,6,7)]
                    colors = [self.selection_colors['F']]
                elif face == 'B' and z == -2:
                    surfaces = [(0,1,5,4)]
                    colors = [self.selection_colors['B']]
                elif face == 'R' and x == 2:
                    surfaces = [(1,2,6,5)]
                    colors = [self.selection_colors['R']]
                elif face == 'L' and x == -2:
                    surfaces = [(0,3,7,4)]
                    colors = [self.selection_colors['L']]

            # Draw surfaces
            for i, surface in enumerate(surfaces):
                glBegin(GL_QUADS)
                glColor3fv(colors[i])
                for vertex in surface:
                    glVertex3fv(vertices[vertex])
                glEnd()

            # Optionally draw edges for better visualization
            glColor3fv((0, 0, 0))
            glBegin(GL_LINES)
            for edge in edges:
                for vertex in edge:
                    glVertex3fv(vertices[vertex])
            glEnd()

        except Exception as e:
            print(f"draw_cubelet 錯誤: {e}")

    def color_map(self, color_char):
        # Map the color character to RGB values
        mapping = {
            'W': (1, 1, 1),       # White
            'Y': (1, 1, 0),       # Yellow
            'G': (0, 1, 0),       # Green
            'B': (0, 0, 1),       # Blue
            'O': (1, 0.5, 0),     # Orange
            'R': (1, 0, 0)        # Red
        }
        return mapping.get(color_char, (0, 0, 0))  # Default to black if unknown

    def draw_cube(self, selection=False):
        # Draw all visible cubies
        try:
            offset = 2  # spacing between cubies
            for x in [-2, 0, 2]:
                for y in [-2, 0, 2]:
                    for z in [-2, 0, 2]:
                        # Skip the invisible center cubie
                        if x == 0 and y == 0 and z == 0:
                            continue
                        self.draw_cubelet((x, y, z), selection=selection)
        except Exception as e:
            print(f"draw_cube 錯誤: {e}")

    def rotate_layer(self, axis, layer, direction):
        # Perform rotation on the data structure
        # axis: 'x', 'y', 'z'
        # layer: -1, 1 corresponding to left/middle/right or similar
        # direction: 1 for clockwise, -1 for counter-clockwise
        # This is a simplified example; actual implementation requires mapping layers to cube faces

        # For demonstration, let's map axis and layer to cube face moves
        # This mapping needs to be refined for accurate layer rotations
        move_map = {
            ('y', 1): 'U',
            ('y', -1): 'D',
            ('z', 1): 'F',
            ('z', -1): 'B',
            ('x', 1): 'R',
            ('x', -1): 'L'
        }

        move = move_map.get((axis, layer), None)
        if move:
            if direction == 1:
                self.cube.move(move)
            else:
                self.cube.move(move + "'")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("退出程式。")
                pygame.quit()
                sys.exit()

            elif event.type == MOUSEBUTTONDOWN:
                if self.mode == 'cube_rotation':
                    if event.button == LEFT:
                        # Start rotating the cube
                        self.mouse_down = True
                        self.last_mouse_pos = pygame.mouse.get_pos()

                        # In cube_rotation mode, detect face click
                        # Start selection process
                        face = self.detect_face_under_mouse()
                        if face:
                            print(f"選擇面：{face}")
                            self.mode = 'side_rotation'
                            self.selected_face = face

                elif self.mode == 'side_rotation':
                    if event.button == LEFT:
                        # Left-click: 90 degrees counter-clockwise
                        if not self.animating:
                            print("左鍵點擊：逆時針旋轉選定面。")
                            self.start_animation(self.selected_face, clockwise=False)
                    elif event.button == RIGHT:
                        # Right-click: 90 degrees clockwise
                        if not self.animating:
                            print("右鍵點擊：順時針旋轉選定面。")
                            self.start_animation(self.selected_face, clockwise=True)
            
            elif event.type == MOUSEBUTTONUP:
                if self.mode == 'cube_rotation':
                    if event.button == 1:
                        # Stop rotating the cube
                        self.mouse_down = False
            
            elif event.type == MOUSEMOTION:
                if self.mode == 'cube_rotation' and self.mouse_down:
                    # Rotate the entire cube based on mouse movement
                    x, y = pygame.mouse.get_pos()
                    dx, dy = pygame.mouse.get_rel()
                    self.rot_x += dy
                    self.rot_y += dx

            elif event.type == KEYDOWN:
                if self.mode == 'side_rotation' and event.key == K_ESCAPE:
                    # Return to cube_rotation mode
                    print("按下 Esc 鍵：返回立方體旋轉模式。")
                    self.mode = 'cube_rotation'
                    self.selected_face = None

    def detect_face_under_mouse(self):
        # Implement color picking to detect which face is under the mouse
        # Render the cube with unique colors for each face's center cubelet
        # Read the pixel color under the mouse and map it to the face

        # Hide the main view and render the selection view
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        self.draw_cube(selection=True)
        glPopMatrix()
        pygame.display.flip()

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Read the pixel color at the mouse position
        pixel = glReadPixels(mouse_x, 600 - mouse_y, 1, 1, GL_RGB, GL_FLOAT)
        clicked_color = tuple(pixel[0][0])

        # Map the color back to the face
        for face, color in self.selection_colors.items():
            # Allow a small margin for floating point inaccuracies
            if all(abs(clicked_color[i] - color[i]) < 0.01 for i in range(3)):
                return face

        return None  # No face detected

    def start_animation(self, face, clockwise=True):
        # Map face to axis and layer
        face_axis_map = {
            'U': ('y', 1),
            'D': ('y', -1),
            'F': ('z', 1),
            'B': ('z', -1),
            'L': ('x', -1),
            'R': ('x', 1)
        }

        axis, layer = face_axis_map.get(face, (None, None))
        if axis is None:
            print(f"無效的面：{face}")
            return

        self.animating = True
        self.animation_axis = axis
        self.animation_layer = layer
        self.animation_direction = 1 if clockwise else -1
        self.animation_angle = 0
        print(f"開始動畫：軸={axis}, 層={layer}, 方向={'順時針' if clockwise else '逆時針'}")

    def animate_rotation(self):
        if self.animating:
            angle_increment = self.animation_speed * self.animation_direction
            self.animation_angle += angle_increment
            if abs(self.animation_angle) >= 90:
                angle_increment -= (self.animation_angle - 90 * self.animation_direction)
                self.animating = False
                # Apply the rotation to the data structure
                self.rotate_layer(self.animation_axis, self.animation_layer, self.animation_direction)
                self.animation_angle = 0
                print("動畫結束，應用旋轉到數據結構。")
            return angle_increment
        return 0

    def run(self):
        clock = pygame.time.Clock()
        print("進入主迴圈。")
        while True:
            self.handle_events()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glPushMatrix()
            glRotatef(self.rot_x, 1, 0, 0)
            glRotatef(self.rot_y, 0, 1, 0)

            # Handle animation rotation
            if self.animating:
                angle = self.animate_rotation()
                if self.animation_axis == 'x':
                    glRotatef(angle, 1, 0, 0)
                elif self.animation_axis == 'y':
                    glRotatef(angle, 0, 1, 0)
                elif self.animation_axis == 'z':
                    glRotatef(angle, 0, 0, 1)

            self.draw_cube()
            glPopMatrix()

            pygame.display.flip()
            clock.tick(60)

# Main Execution
if __name__ == "__main__":
    try:
        rubiks_cube_3d = RubiksCube3D()
        rubiks_cube_3d.run()
    except Exception as e:
        print(f"程式運行時出錯: {e}")
        pygame.quit()
        sys.exit()