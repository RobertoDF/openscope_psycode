from camstim import MovieStim, SweepStim, Window
import logging


def make_movie_stim(movie_path, window):

    return MovieStim(movie_path=movie_path,
                     window=window,
                     frame_length=2.0/120.0,
                     size=(2560, 1440),
                     start_time=0.0,
                     stop_time=None,
                     flip_v=True,)


logging.basicConfig(level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

window = Window(fullscr=True,
                monitor='testMonitor',
                screen=1,)

g0 = make_movie_stim(movie_path="data/movie_clip_A.npy", window=window)
g0.set_display_sequence([(0.0, 2.0), (6.0, 8.0)])
g1 = make_movie_stim(movie_path="data/movie_clip_B.npy", window=window)
g1.set_display_sequence([(2.0, 4.0)])
g2 = make_movie_stim(movie_path="data/movie_clip_C.npy", window=window)
g2.set_display_sequence([(4.0, 6.0)])

config = {
    'sync_sqr': True,
}

ss = SweepStim(window,
               stimuli=[g0, g1, g2],
               # pre_blank_sec=1,
               # post_blank_sec=1,
               params=config,
               )

ss.run()
