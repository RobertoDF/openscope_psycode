#%%

import skvideo.io
import numpy as np

vid = skvideo.io.vread("data/Movie_sequence_6s.mp4")

np.save('data/movie_clip_A.npy', vid[0:120, :, :, 0])
np.save('data/movie_clip_B.npy', vid[121:241, :, :, 0])
np.save('data/movie_clip_C.npy', vid[240:360, :, :, 0])