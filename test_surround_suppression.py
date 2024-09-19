from camstim import Stimulus, Window, Warp, SweepStim
from psychopy import monitors, visual
import numpy as np

# Setup the Window

window = visual.Window(
    size=(1920, 1080),
    fullscr=False,
    screen=0,
    allowGUI=False,
    allowStencil=True,
    monitor='testMonitor',
    color=[0, 0, 0],
    colorSpace='rgb',
    blendMode='avg',
    useFBO=True,
    units='deg',
)

def init_grating(window, sweep_length, blank_length, contrast,  tf, sf, ori, size, positions, blank_sweeps):

        grating = Stimulus(visual.GratingStim(window,
                                        units               = 'deg',
                                        mask                = "circle",
                                        texRes              = 256,
                                        ),
                                        sweep_params        = { 'Contrast': ([contrast], 0),
                                                                'TF': ([tf], 2),
                                                                'SF': ([sf], 3),
                                                                'Ori': (ori, 4),
                                                                "Size": (size, 5),
                                                                "Pos": (positions, 6)
                                                                 },

                                        sweep_length        = sweep_length,
                                        start_time          = 0.0,
                                        blank_length        = blank_length,
                                        blank_sweeps        = blank_sweeps,
                                        runs                = 10,
                                        shuffle             = True,
                                        save_sweep_table    = True,
                                        )
        grating.stim_path = r"C:\\not_a_stim_script\\init_grating.stim"

        return grating


sweep_length = 0.35
blank_length = 0.15
contrast = [.8]
tf = 2
sf = 0.04
ori = [0,45,90,135]
size = [5, 15, 25, 35, 45]
blank_sweeps = 0

x_positions = np.arange(-10, 15, 10)
y_positions = np.arange(-10, 15, 10)
positions = []
for y in y_positions:
    for x in x_positions:
        if x == 0 or y == 0:
            positions.append((x,  y))


gratings=[]

gratings.append( init_grating(window, sweep_length, blank_length, contrast,  tf, sf, ori, size, positions, blank_sweeps))

ss = SweepStim(window,
               stimuli=gratings,
               pre_blank_sec=1,
               post_blank_sec=1,
               params={},  # will be set by MPE to work on the rig
               )
ss.run()