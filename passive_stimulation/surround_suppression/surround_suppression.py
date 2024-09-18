#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.82.01), September 16, 2024, at 15:39
If you publish work using this script please cite the relevant PsychoPy publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, gui
import numpy as np
from numpy.random import shuffle
import os

# Ensure that relative paths start from the same directory as this script
_thisDir = "C:\Users\Roberto\Documents\GitHub\openscope_psycode\passive_stimulation\surround_suppression"
os.chdir(_thisDir)

# Store info about the experiment session
expName = u'untitled'  # from the Builder filename that created this script
expInfo = {'participant': '', 'session': '001'}
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + 'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])
print(filename)

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
                                 extraInfo=expInfo, runtimeInfo=None,
                                 originPath=u'C:\\Users\\Roberto\\Documents\\temp\\untitled.psyexp',
                                 savePickle=True, saveWideText=True,
                                 dataFileName=filename)
# save a log file for detail verbose info
logFile = logging.LogFile(filename + '.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp

# Start Code - component code to be run before the window creation

# Setup the Window
win = visual.Window(
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
# store frame rate of monitor if we can measure it successfully
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    expInfo['frameRate'] = 60.0  # couldn't get a reliable measure so guess
    frameDur = 1.0 / 60.0

# Define stimulus parameters
diameters = [5, 15, 25, 35, 45]  # Diameters of the Gabors in degrees
spatial_freq = 0.04  # Spatial frequency in cycles/degree
temporal_freq = 2  # Temporal frequency in Hz
orientation = 0  # Orientation of the Gabor in degrees
num_trials_per_condition = 15  # Number of trials per condition

x_positions = np.arange(-10, 15, 10)  # [-10, 0, 10]
y_positions = np.arange(-10, 15, 10)  # [-10, 0, 10]
positions = []
for y in y_positions:
    for x in x_positions:
        # Only add positions where either x or y is 0 (but not both unless it's the center)
        if x == 0 or y == 0:
            positions.append({'posX': x, 'posY': y})

# Generate trial list
trial_list = []
for diameter in diameters:
    for pos in positions:
        for _ in range(num_trials_per_condition):
            trial_list.append({'diameter': diameter, 'posX': pos['posX'], 'posY': pos['posY']})

# Randomize trial order
shuffle(trial_list)

# Initialize components for Routine "trial"
trialClock = core.Clock()

# Create Gabor stimulus
gabor = visual.GratingStim(
    win=win,
    units='deg',
    size=21,  # will be updated each trial
    pos=(0, 0),  # will be updated each trial
    sf=spatial_freq,
    ori=orientation,
    mask='gauss',
    phase=0,
)

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine

# Set up handler to look after randomization of conditions etc
trials = data.TrialHandler(
    nReps=1,
    method='random',
    extraInfo=expInfo,
    trialList=trial_list,
    seed=None,
    name='trials',
)
thisExp.addLoop(trials)  # add the loop to the experiment
thisTrial = trials.trialList[0]  # so we can initialize stimuli with some values

# Start the experiment
for thisTrial in trials:
    currentLoop = trials
    # Abbreviate parameter names
    if thisTrial != None:
        for paramName in thisTrial.keys():
            exec (paramName + '= thisTrial[paramName]')

    # Update Gabor stimulus parameters
    gabor.size = diameter
    gabor.pos = (posX, posY)
    gabor.phase = 0  # Reset phase

    # Reset orientation variables at the start of each trial
    orientations = [0, 45, 90, 135]
    # Uncomment the next line if you want to randomize orientations

    np.random.shuffle(orientations)

    thisExp.addData('orientation', gabor.ori)

    orientation_index = 0
    gabor.ori = orientations[orientation_index]
    orientation_change_times = [0.0, 0.5, 1.0, 1.5]
    next_orientation_time = orientation_change_times[orientation_index]
    # Prepare to start Routine "trial"
    t = 0
    trialClock.reset()
    frameN = -1
    routineTimer.add(2.500000)  # 2s stimulus + 0.5s ITI
    continueRoutine = True

    # Calculate phase increment
    frame_rate = expInfo['frameRate']
    phase_increment = temporal_freq / frame_rate

    while continueRoutine and routineTimer.getTime() > 0:
        t = trialClock.getTime()
        frameN += 1

        # Update orientation every 0.5 seconds
        if t >= next_orientation_time and orientation_index < len(orientations):
            gabor.ori = orientations[orientation_index]
            orientation_index += 1
            if orientation_index < len(orientation_change_times):
                next_orientation_time = orientation_change_times[orientation_index]
            else:
                next_orientation_time = 2.0  # No further orientation changes

        # Update/draw components on each frame
        if t < 2.0:
            gabor.phase += phase_increment
            gabor.draw()
        else:
            pass  # Present blank screen (ITI)

        # Check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()

        # Refresh the screen
        win.flip()

    # End of trial routine
    thisExp.nextEntry()

win.close()
core.quit()
