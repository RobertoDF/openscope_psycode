#%%

import skvideo.io
import numpy as np

vid = skvideo.io.vread("data/Movie_sequence_6s.mp4")

vid_a = vid[0:120, :, :, 0]
vid_b = vid[121:241, :, :, 0]
vid_c = vid[240:360, :, :, 0]

np.save('data/movie_clip_A.npy', vid_a)
np.save('data/movie_clip_B.npy', vid_b)
np.save('data/movie_clip_C.npy', vid_c)
np.save('data/gray.npy', np.ones_like(vid_a)*128)