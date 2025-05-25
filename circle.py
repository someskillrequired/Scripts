import math
import numpy as np
import matplotlib.pyplot as plt

radius = 11  # Radius of the arc
side_length = 1  # Length of the square's side
num_squares_touching = 100
spacing = math.sqrt(2) * side_length  # Minimum spacing to avoid corner overlap
delta_theta = math.asin(spacing / (2 * radius))  # Angular spacing in radians
num_squares = int((math.pi / 2) / delta_theta)  # Number of squares for a 90° ar 


def plot_edge_touching_squares(radius, side_length, num_squares):
    # Calculate angular spacing for side edges touching
    delta_theta = side_length / radius  # Angular spacing for touching edges

    fig, ax = plt.subplots(figsize=(6, 6))
    
    for i in range(num_squares):
        theta = i * delta_theta  # Angle for the current square
        x_center = radius * math.cos(theta)  # Center x-coordinate
        y_center = radius * math.sin(theta)  # Center y-coordinate

        # Calculate rotation angle (aligned along the radius)
        rotation_angle = theta

        # Define the corners of the square relative to its center
        half_side = side_length / 2
        corners = np.array([
            [-half_side, -half_side],  # Bottom-left
            [ half_side, -half_side],  # Bottom-right
            [ half_side,  half_side],  # Top-right
            [-half_side,  half_side],  # Top-left
            [-half_side, -half_side]  # Close the square
        ])

        # Rotate the corners
        rotation_matrix = np.array([
            [math.cos(rotation_angle), -math.sin(rotation_angle)],
            [math.sin(rotation_angle),  math.cos(rotation_angle)]
        ])
        rotated_corners = (corners @ rotation_matrix.T) + np.array([x_center, y_center])

        # Plot the square
        ax.plot(rotated_corners[:, 0], rotated_corners[:, 1], color="blue")

    # Draw the arc for reference
    arc_angles = [i * delta_theta for i in range(num_squares)]
    arc_x = [radius * math.cos(angle) for angle in arc_angles]
    arc_y = [radius * math.sin(angle) for angle in arc_angles]
    ax.plot(arc_x, arc_y, linestyle="--", color="gray", label="Arc Path")

    # Configure plot
    ax.set_aspect('equal')
    ax.set_xlim(-15, 15)
    ax.set_ylim(-5, 15)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(True)
    plt.title("Squares with Edges Touching along an Arc")
    plt.legend()
    plt.show()

# Plot squares with outer edges touching
num_squares_edges_touching = 106  # Adjustable based on the arc length
plot_edge_touching_squares(radius, side_length, num_squares_edges_touching)




# Plot rotated squares along the arc
#plot_rotated_squares(radius, side_length, delta_theta, num_squares)
