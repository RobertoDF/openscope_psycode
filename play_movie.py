import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Sample 3D array (X, Y, Time) representing the movie
path = './data/movie_clip_C.npy'
movie_array = np.load(path)

# Function to update the displayed frame
def update_frame(frame_number):
    plt.clf()
    plt.imshow(movie_array[frame_number, :, :], cmap='gray', aspect='auto')
    plt.title('Frame: '+str(frame_number))

# Create the matplotlib figure
fig = plt.figure()

# Create the animation with a frame rate of 2 FPS (500 ms per frame)
ani = animation.FuncAnimation(fig, update_frame, frames=movie_array.shape[0], interval=1, repeat=True)

# Display the movie
plt.show()
