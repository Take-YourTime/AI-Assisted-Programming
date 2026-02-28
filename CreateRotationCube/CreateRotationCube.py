import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import imageio
import os

# Step 1: Import colors from 'sidecolor.txt' file
def import_colors(filename='sidecolor.txt'):
    with open(filename, 'r') as f:
        colors = [line.strip() for line in f]
    return colors

# Step 2: Define the cube's vertices and faces
def get_cube_vertices():
    vertices = np.array([[-1, -1, -1],
                         [1, -1, -1],
                         [1,  1, -1],
                         [-1,  1, -1],
                         [-1, -1,  1],
                         [1, -1,  1],
                         [1,  1,  1],
                         [-1,  1,  1]])
    
    faces = [[0, 1, 2, 3],  # Bottom
             [4, 5, 6, 7],  # Top
             [0, 1, 5, 4],  # Front
             [2, 3, 7, 6],  # Back
             [0, 3, 7, 4],  # Left
             [1, 2, 6, 5]]  # Right
    
    return vertices, faces

# Function to rotate the cube around X, Y, and Z axes
def rotate_vertices(vertices, angle_x, angle_y):
    # Rotation matrix around X axis
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(angle_x), -np.sin(angle_x)],
                   [0, np.sin(angle_x), np.cos(angle_x)]])
    
    # Rotation matrix around Y axis
    Ry = np.array([[np.cos(angle_y), 0, np.sin(angle_y)],
                   [0, 1, 0],
                   [-np.sin(angle_y), 0, np.cos(angle_y)]])
    
    # Combine the rotations
    return vertices @ (Ry @ Rx).T

# Step 3: Create images of the cube rotating and save them
def create_rotating_cube_images(colors, num_frames=36, image_dir='cube_frames'):
    vertices, faces = get_cube_vertices()
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    for i in range(num_frames):
        ax.cla()  # Clear previous plot
        ax.set_xlim([-2, 2])
        ax.set_ylim([-2, 2])
        ax.set_zlim([-2, 2])
        
        # Rotate the cube over time (changing the angle per frame)
        angle_x = np.radians(i * 10)  # X-axis rotation
        angle_y = np.radians(i * 10)  # Y-axis rotation
        rotated_vertices = rotate_vertices(vertices, angle_x, angle_y)
        
        # Plot each face of the cube with the corresponding color
        for j, face in enumerate(faces):
            square = Poly3DCollection([rotated_vertices[face]], facecolors=colors[j], linewidths=1, edgecolors='black', alpha=0.9)
            ax.add_collection3d(square)
        
        # Save each frame as an image
        frame_filename = os.path.join(image_dir, f'frame_{i:02d}.png')
        plt.savefig(frame_filename)
        print(f'Saved: {frame_filename}')
    
    print(f"All frames saved to {image_dir}")

# Step 4: Create GIF from saved images
def create_gif_from_images(image_dir='cube_frames', gif_name='rotating_cube.gif'):
    frames = []
    
    for i in range(36):  # Same number as num_frames
        frame_filename = os.path.join(image_dir, f'frame_{i:02d}.png')
        image = imageio.imread(frame_filename)
        frames.append(image)
    
    # Save frames as a GIF, set loop=0 to make it repeat indefinitely
    imageio.mimsave(gif_name, frames, fps=10, loop=0)
    print(f"GIF saved as {gif_name} (will loop indefinitely)")

# Main function to execute the program
if __name__ == '__main__':
    colors = import_colors()  # Read colors from 'sidecolor.txt'
    
    # Step 5: Generate the images for the rotating cube
    create_rotating_cube_images(colors)
    
    # Step 6: Create the GIF from the images (with looping)
    create_gif_from_images()
