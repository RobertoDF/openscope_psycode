# -*- coding: utf-8 -*-
# Stimulus design
#
# 1. For the random stimulus order (days #0 and #5):
#
#     - there are 4 difference choices of a 2 sec duration stimulus
#       – movie clip A
#       – movie clip B
#       – movie clip C
#       – a constant grey screen, X
#
#     - these will be displayed in a randomized order.
#     - this order will be exactly the same on day #0 and day #5.
#     - there will be 525 repeats of each of the 4 stimuli.
#
# 2. For the sequence stimulus order (day #1 – #4):
#
#     - the 3 movie clips are shown in the same repeated order, ABC, for 50 minutes.
#     - this will result in 500 repeats of this movie clip sequence.
#     - in the last 20 minutes, the stimuli will be shown in a random order with the grey screen intermixed, as on days
#       #0 and #5
#     - a different random sequence will be chosen and kept the same across days #1 – #4.
#     - this will result in 150 repeats of each of these 4 stimuli.


import argparse
import numpy as np
import os

from psychopy import monitors
from camstim import MovieStim, SweepStim, Window, Warp

import logging

# Make logging a bit prettier
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Paths to the movie clip files to load.
movie_clip_files = ['data/movie_clip_A.npy', 'data/movie_clip_B.npy', 'data/movie_clip_C.npy', 'data/gray.npy']

# Set of debug movie clip s to load. These videos have blinking letters to make clips easier to recognize.
# If they don't exist yet make sure to run gen_letter_videos.py first. Comment out if not debugging!
# movie_clip_files = ['data/A_blinking_video.npy', 'data/B_blinking_video.npy', 'data/C_blinking_video.npy',
#                     'data/gray.npy']

MOVIE_ZIP_URL = "https://tigress-web.princeton.edu/~dmturner/allen_stimulus/movie_clips.zip"
for clip_path in movie_clip_files:
    if not os.path.exists(clip_path):
        raise ValueError("Movie clip file not found: {}. Make sure ".format(clip_path) +
                         "to download from {} and extract them to the data folder.".format(MOVIE_ZIP_URL))


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

            # The movie clips should be 2 seconds long and should be played at 60 fps.
            s = MovieStim(movie_path=movie_paths[i],
                          window=window,
                          frame_length=1.0 / 60.0,
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

    parser = argparse.ArgumentParser("stimulus")
    parser.add_argument("day", help="An integer representing the day of the experiment. Defaults to Day 0.",
                        nargs='?', type=int, default=0)
    args = parser.parse_args()

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

    if args.day == 0 or args.day == 5:
        order = order70
    else:
        order = np.concatenate((order50, order20))

    ss = make_movie_stimulus(movie_clip_files, order, window)

    ss.run()
