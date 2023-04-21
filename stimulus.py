import numpy as np

from psychopy import monitors
from camstim import MovieStim, SweepStim, Window, Warp

import logging

# Make logging a bit prettier
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Change depending on the DAY of the experiment. Maybe this should be a command line argument?
DAY = 0

# Paths to the movie clip files to load.
movie_clip_files = ['data/movie_clip_A.npy', 'data/movie_clip_B.npy', 'data/movie_clip_C.npy', 'data/gray.npy']

# Set of debug movie clips to load. These videos have blinking letters to make clips easier to recognize.
# If they don't exist yet make sure to run gen_letter_videos.py first. Comment out if not debugging!
movie_clip_files = ['data/A_blinking_video.npy', 'data/B_blinking_video.npy', 'data/C_blinking_video.npy',
                    'data/gray.npy']

# Load the random movie clip order that were provided by Prof. Berry. Subtracts 1 from each value to
# convert from 1-indexed to 0-indexed.
order20 = (np.loadtxt('data/stimulus_orderings/movie_order_random_20min.txt').astype(int) - 1)
order50 = (np.loadtxt('data/stimulus_orderings/movie_order_random_50min.txt').astype(int) - 1)
order70 = (np.loadtxt('data/stimulus_orderings/movie_order_random_70min.txt').astype(int) - 1)


def make_movie_stimulus(movie_paths, order, window):
    """Generate a Stimulus that plays a series of movie clips in a specified order."""

    # Convert the order into a list of display sequence tuples. There should be one display sequence list per movie
    # clip. Each display sequence list contains a set of tuples of the form (start_second, stop_second). Theses tuples
    # define the start and stop time for when to play the clip and are determined by the order vector
    all_starts = np.arange(0, 2 * len(order), 2).astype(float)
    display_sequences = []
    for i in np.unique(order):
        display_sequences.append(list(zip(all_starts[order == i], all_starts[order == i] + 2.0)))

    # Load each movie clip into its own MovieStim object. The display sequence will be set later so the clips play
    # in the correct order.
    stims = []
    for i in np.unique(order):

        # If the order index is less than the number of movie clips, load the movie clip.
        if i < len(movie_paths):
            s = MovieStim(movie_path=movie_paths[i],
                          window=window,
                          frame_length=2.0 / 120.0,
                          size=(1920, 1080),
                          start_time=0.0,
                          stop_time=None,
                          flip_v=True, runs=len(display_sequences[i]))
            s.set_display_sequence(display_sequences[i])
        else:
            raise ValueError("Order index is greater than the number of movie clips.")

        stims.append(s)

    stim = SweepStim(window,
                     stimuli=stims,
                     # pre_blank_sec=1,
                     # post_blank_sec=1,
                     params=config,
                     )

    return stim


if __name__ == "__main__":

    # Copied monitor and window setup from:
    # https://github.com/AllenInstitute/openscope-glo-stim/blob/main/test-scripts/cohort-1-test-12min-drifting.py

    dist = 15.0
    wid = 52.0

    monitor = monitors.Monitor("testMonitor", distance=dist, width=wid) #"Gamma1.Luminance50"

    # Create display window
    window = Window(fullscr=True, # Will return an error due to default size. Ignore.
                    monitor=monitor,  # Will be set to a gamma calibrated profile by MPE
                    screen=0,
                    warp=Warp.Spherical
                    )

    config = {
        'sync_sqr': True,
    }

    if DAY == 0 or DAY == 5:
        order = order20
    else:
        order = order50

    ss = make_movie_stimulus(movie_clip_files, order, window)

    ss.run()
