import sys
import argparse
import yaml
import numpy as np
from six import iteritems
from camstim.change import DoCTask, DoCTrialGenerator
from camstim.behavior import Epoch
from camstim.sweepstim import MovieStim
from camstim.experiment import EObject, ETimer
from camstim import Stimulus, Window, Warp, SweepStim
from psychopy import monitors, visual
try:
    from pyglet.window import key
except:
    warnings.warn("Couldn't set up pyglet keybinds.", ImportWarning)
from qtpy import QtCore
import logging
import time
import zmq
from zro import Proxy
import datetime
import csv
import pickle as pkl
from copy import deepcopy
import os
import time

stage = Proxy("tcp://localhost:6001", serialization="json", timeout=.5)  # ZRO Proxy to PhidgetServer

try:
    stage.uptime
except zmq.error.Again:
    raise Exception("PhidgetServer is not running. Please start PhidgetServer before running this script.")


def run_optotagging(levels, conditions, waveforms, isis, sampleRate = 10000.):

    from toolbox.IO.nidaq import AnalogOutput
    from toolbox.IO.nidaq import DigitalOutput

    sweep_on = np.array([0,0,1,0,0,0,0,0], dtype=np.uint8)
    stim_on = np.array([0,0,1,1,0,0,0,0], dtype=np.uint8)
    stim_off = np.array([0,0,1,0,0,0,0,0], dtype=np.uint8)
    sweep_off = np.array([0,0,0,0,0,0,0,0], dtype=np.uint8)

    ao = AnalogOutput('Dev1', channels=[1])
    ao.cfg_sample_clock(sampleRate)

    do = DigitalOutput('Dev1', 2)

    do.start()
    ao.start()

    do.write(sweep_on)
    time.sleep(5)

    for i, level in enumerate(levels):

        print(level)

        data = waveforms[conditions[i]]

        do.write(stim_on)
        ao.write(data * level)
        do.write(stim_off)
        time.sleep(isis[i])

    do.write(sweep_off)
    do.clear()
    ao.clear()

def generatePulseTrain(pulseWidth, pulseInterval, numRepeats, riseTime, sampleRate = 10000.):

    data = np.zeros((int(sampleRate),), dtype=np.float64)
   # rise_samples =

    rise_and_fall = (((1 - np.cos(np.arange(sampleRate*riseTime/1000., dtype=np.float64)*2*np.pi/10))+1)-1)/2
    half_length = int(rise_and_fall.size / 2)
    rise = rise_and_fall[:half_length]
    fall = rise_and_fall[half_length:]

    peak_samples = int(sampleRate*(pulseWidth-riseTime*2)/1000)
    peak = np.ones((peak_samples,))

    pulse = np.concatenate((rise, \
                           peak, \
                           fall))

    interval = int(pulseInterval*sampleRate/1000.)

    for i in range(0, numRepeats):
        data[i*interval:i*interval+pulse.size] = pulse

    return data

def optotagging(mouse_id, operation_mode='experiment', level_list = [1.15, 1.28, 1.345], output_dir = 'C:/ProgramData/camstim/output/'):

    sampleRate = 10000

    # 1 s cosine ramp:
    data_cosine = (((1 - np.cos(np.arange(sampleRate, dtype=np.float64)
                                * 2*np.pi/sampleRate)) + 1) - 1)/2  # create raised cosine waveform

    # 1 ms cosine ramp:
    rise_and_fall = (
        ((1 - np.cos(np.arange(sampleRate*0.001, dtype=np.float64)*2*np.pi/10))+1)-1)/2
    half_length = int(rise_and_fall.size / 2)

    # pulses with cosine ramp:
    pulse_2ms = np.concatenate((rise_and_fall[:half_length], np.ones(
        (int(sampleRate*0.001),)), rise_and_fall[half_length:]))
    pulse_5ms = np.concatenate((rise_and_fall[:half_length], np.ones(
        (int(sampleRate*0.004),)), rise_and_fall[half_length:]))
    pulse_10ms = np.concatenate((rise_and_fall[:half_length], np.ones(
        (int(sampleRate*0.009),)), rise_and_fall[half_length:]))

    data_2ms_10Hz = np.zeros((sampleRate,), dtype=np.float64)

    for i in range(0, 10):
        interval = int(sampleRate / 10)
        data_2ms_10Hz[i*interval:i*interval+pulse_2ms.size] = pulse_2ms

    data_5ms = np.zeros((sampleRate,), dtype=np.float64)
    data_5ms[:pulse_5ms.size] = pulse_5ms

    data_10ms = np.zeros((sampleRate,), dtype=np.float64)
    data_10ms[:pulse_10ms.size] = pulse_10ms

    data_10s = np.zeros((sampleRate*10,), dtype=np.float64)
    data_10s[:-2] = 1

    ##### THESE STIMULI ADDED FOR OPENSCOPE GLO PROJECT #####
    data_10ms_5Hz = generatePulseTrain(10, 200, 5, 1) # 1 second of 5Hz pulse train. Each pulse is 10 ms wide
    data_6ms_40Hz = generatePulseTrain(6, 25, 40, 1)  # 1 second of 40 Hz pulse train. Each pulse is 6 ms wide
    #########################################################

    # for experiment

    isi = 1.5
    isi_rand = 0.5
    numRepeats = 50

    condition_list = [3, 4, 5]
    waveforms = [data_2ms_10Hz, data_5ms, data_10ms, data_cosine, data_10ms_5Hz, data_6ms_40Hz]

    opto_levels = np.array(level_list*numRepeats*len(condition_list)) #     BLUE
    opto_conditions = condition_list*numRepeats*len(level_list)
    opto_conditions = np.sort(opto_conditions)
    opto_isis = np.random.random(opto_levels.shape) * isi_rand + isi

    p = np.random.permutation(len(opto_levels))

    # implement shuffle?
    opto_levels = opto_levels[p]
    opto_conditions = opto_conditions[p]

    # for testing

    if operation_mode=='test_levels':
        isi = 2.0
        isi_rand = 0.0

        numRepeats = 2

        condition_list = [0]
        waveforms = [data_10s, data_10s]

        opto_levels = np.array(level_list*numRepeats*len(condition_list)) #     BLUE
        opto_conditions = condition_list*numRepeats*len(level_list)
        opto_conditions = np.sort(opto_conditions)
        opto_isis = np.random.random(opto_levels.shape) * isi_rand + isi

    elif operation_mode=='pretest':
        numRepeats = 1

        condition_list = [0]
        data_2s = data_10s[-sampleRate*2:]
        waveforms = [data_2s]

        opto_levels = np.array(level_list*numRepeats*len(condition_list)) #     BLUE
        opto_conditions = condition_list*numRepeats*len(level_list)
        opto_conditions = np.sort(opto_conditions)
        opto_isis = [1]*len(opto_conditions)
    #

    outputDirectory = output_dir
    fileDate = str(datetime.datetime.now()).replace(':', '').replace(
        '.', '').replace('-', '').replace(' ', '')[2:14]
    fileName = os.path.join(outputDirectory, fileDate + '_'+mouse_id + '.opto.pkl')

    print('saving info to: ' + fileName)
    fl = open(fileName, 'wb')
    output = {}

    output['opto_levels'] = opto_levels
    output['opto_conditions'] = opto_conditions
    output['opto_ISIs'] = opto_isis
    output['opto_waveforms'] = waveforms

    pkl.dump(output, fl)
    fl.close()
    print('saved.')

    #
    run_optotagging(opto_levels, opto_conditions,
                    waveforms, opto_isis, float(sampleRate))
"""
end of optotagging section
"""


# Configure logging level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class AddEpochDoc(DoCTask):
    started = QtCore.Signal()

    def start_epochs(self, list_epochs):
        print("starting new task")
        for indiv_epoch in list_epochs:
        # Attaching epoch
            self.started.connect(indiv_epoch.enter)
        self.start()

    def start(self):
        """ Starts the task. """
        super(DoCTask, self).start()
        # schedule a time for the task to end
        number_runs_rf = self._doc_config['number_runs_rf'] 
        if  self._doc_config['prologue']:
            prologue_offset = number_runs_rf*60
        else:
            prologue_offset = 0
        start_stop_padding = self._doc_config['start_stop_padding']
        self._task_scheduled_end = time.clock() + self._doc_config['max_task_duration_min'] * 60.0 + start_stop_padding + prologue_offset
        self.stim_off()
        self.started.emit()
        ETimer.singleShot(prologue_offset+start_stop_padding, self._next_trial)

class DocNoLickSpout(Epoch):
    """ DoC Epoch that retracts the lick spout. """
    def __init__(self, stage, *args, **kwargs):
        super(DocNoLickSpout, self).__init__(*args, **kwargs)
        self.stage = stage

    # These setter and getter are needed to disconnect the epoch from the list of epochs in the task
    # Without these the epoch collide with another as epochs are assumed to not overlaps
    @property
    def _active(self):
        return self._is_active

    @_active.setter
    def _active(self, value):
        self._is_active = value

    def set_active(self, active):
        self._active = active

    def _on_entry(self):
        logging.info("Retracting lickspout")
        self.stage.retract_lickspout()
        self._task.stim_off()

    def _on_exit(self):
        logging.info("Extending lickspout")
        self.stage.extend_lickspout()
        self._task.stim_on()
           
class DocWithLickSpout(Epoch):
    """ DoC Epoch that retracts the lick spout. """
    def __init__(self, stage, *args, **kwargs):
        super(DocWithLickSpout, self).__init__(*args, **kwargs)
        self.stage = stage

    # These setter and getter are needed to disconnect the epoch from the list of epochs in the task
    # Without these the epoch collide with another as epochs are assumed to not overlaps
    @property
    def _active(self):
        return self._is_active

    @_active.setter
    def _active(self, value):
        self._is_active = value

    def set_active(self, active):
        self._active = active

    def _on_entry(self):
        logging.info("Extending lickspout")
        self.stage.extend_lickspout()

    def _on_exit(self):
        logging.info("Retracting lickspout")
        self.stage.retract_lickspout()

class DocDistribModifier(Epoch):
    """ DoC Epoch that modifies the distribution of the change stimuli. """
    def __init__(self, time_change=0.1, *args, **kwargs):
        super(DocDistribModifier, self).__init__(*args, **kwargs)
        self.time_change = time_change

    # These setter and getter are needed to disconnect the epoch from the list of epochs in the task
    # Without these the epoch collide with another as epochs are assumed to not overlaps
    @property
    def _active(self):
        return self._is_active

    @_active.setter
    def _active(self, value):
        self._is_active = value

    def set_active(self, active):
        self._active = active

    def _on_entry(self):
        logging.info("Changing time distribution to {}".format(self.time_change))
        self.old_time_change = self._task._trial_generator.change_time_scale 
        self._task._trial_generator.change_time_scale = self.time_change

    def _on_exit(self):
        logging.info("Changing time distribution back to {}".format(self.old_time_change))
        self._task._trial_generator.change_time_scale = self.old_time_change

class DocSpaceBarTracker(EObject):
    """ DoC object to track space bar presses.
    """

    def __init__(self, window=None):
        super(DocSpaceBarTracker, self).__init__()

        self._window = window
        self._update_count = 0
        self.keyspace_events = []

        self._keys = key.KeyStateHandler()
        if self._window:
            self._window.winHandle.push_handlers(self._keys)

        # lockout timer in case person holds key down
        self._lockout_timer = QtCore.QTimer()
        self._lockout_timer.timeout.connect(self._lockout_ended)
        self._lockout = False

    def update(self, index=None):
        self._update_count += 1
        if self._keys[key.SPACE]:
            if not self._lockout:              
                self.keyspace_events.append(self._update_count)
                logging.info("Space bar pressed at update {}".format(self._update_count))
                # HERE WE LOG THE SPACEBAR PRESS
                self._lockout = True
                self._lockout_timer.start(200)

    def _lockout_ended(self):
        self._lockout = False
        self._lockout_timer.stop()

    def package(self):
        # create set of frame indices the length of our frame_list
        self.keyspace_events = np.array(self.keyspace_events)
        return super(DocSpaceBarTracker, self).package()

def create_receptive_field_mapping(window, number_runs = 15):
    # should be 5 min long in total, number_runs = 5
    x = np.arange(-40,45,10)
    y = np.arange(-40,45,10)
    position = []
    for i in x:
        for j in y:
            position.append([i,j])

    stimulus = Stimulus(visual.GratingStim(window,
                        units='deg',
                        size=20,
                        mask="circle",
                        texRes=256,
                        sf=0.1,
                        ),
        sweep_params={
                'Pos':(position, 0),
                'Contrast': ([0.8], 4),
                'TF': ([4.0], 1),
                'SF': ([0.08], 2),
                'Ori': ([0,45,90], 3),
                },
        sweep_length=0.25,
        start_time=0.0,
        blank_length=0.0,
        blank_sweeps=0,
        runs=number_runs,
        shuffle=True,
        save_sweep_table=True,
        )
    stimulus.stim_path = r"C:\\not_a_stim_script\\receptive_field_block.stim"

    return stimulus


def init_grating(window, sweep_length, blank_length, contrast,  tf, sf, ori, size, positions, blank_sweeps, number_runs):

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
                                        runs                = number_runs,
                                        shuffle             = True,
                                        save_sweep_table    = True,
                                        )
        grating.stim_path = r"C:\\not_a_stim_script\\init_grating.stim"

        return grating

def create_surround_suppression_mapping(window, number_runs = 15):
    # 15 trials ideal, should be 15 min long in total
    sweep_length = 0.35
    blank_length = 0.15
    contrast = [.8]
    tf = 2
    sf = 0.04
    ori = [0, 45, 90, 135]
    size = [5, 15, 25, 35, 45]
    blank_sweeps = 0

    x_positions = np.arange(-10, 15, 10)
    y_positions = np.arange(-10, 15, 10)
    positions = []
    for y in y_positions:
        for x in x_positions:
            if x == 0 or y == 0:
                positions.append((x, y))

    gratings = []

    gratings.append(
        init_grating(window, sweep_length, blank_length, contrast, tf, sf, ori, size, positions, blank_sweeps, number_runs))

    stimulus.stim_path = r"C:\\not_a_stim_script\\receptive_field_block.stim"

    return gratings

def load_params():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", nargs="?", type=str, default="")

    args, _ = parser.parse_known_args() # <- this ensures that we ignore other arguments that might be needed by camstim
    # print args
    with open(args.json_path, 'r') as f:
        # we use the yaml package here because the json package loads as unicode, which prevents using the keys as parameters later
        params = yaml.load(f)
    return params

def load_stimulus_class(class_name):

    if class_name=='grating':
        from camstim.change import DoCGratingStimulus as DoCStimulus
    elif class_name=='images':
        from camstim.change import DoCImageStimulus as DoCStimulus
    else:
        raise Exception('no idea what Stimulus class to use for `{}`'.format(class_name))

    return DoCStimulus

def set_stimulus_groups(groups, stimulus_object):
    for group_name, group_params in iteritems(groups):
        for param, values in iteritems(group_params):
            stimulus_object.add_stimulus_group(group_name, param, values)

json_params = load_params()
stimulus = json_params['stimulus']

# start_padding_windowless implementation
start_padding_windowless = json_params.get("start_padding_windowless")
max_task_duration_min = json_params.get("max_task_duration_min")

if start_padding_windowless:
    logging.info("start_padding_windowless: {}s".format(start_padding_windowless))
    logging.info("Entering start_padding_windowless: {}s".format(start_padding_windowless))

    tic = time.time()
    try:
        while True:
            if time.time() - tic > start_padding_windowless:
                print('start_padding_windowless ended')
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print('start_padding_windowless aborted')
        sys.exit(1)

dev_mode = json_params.get("dev_mode", True)

if dev_mode:
    my_monitor = monitors.Monitor(name='Test')
    my_monitor.setSizePix((1280,800))
    my_monitor.setWidth(20)
    my_monitor.setDistance(15)
    my_monitor.saveMon()
    window = Window(size=[1024,768],
        fullscr=False,
        screen=0,
        monitor= my_monitor,
        warp=Warp.Spherical
    )
elif "luminance_matching_intensity" in stimulus:
    window = Window(
        fullscr=True,
        screen=0,
        monitor='Gamma1.Luminance50',
        color=stimulus['luminance_matching_intensity'],
        warp=Warp.Spherical,
    )
else: 
    window = Window(
        fullscr=True,
        screen=0,
        monitor='Gamma1.Luminance50',
        warp=Warp.Spherical,
    )

# Set up Task
params = {}
f = AddEpochDoc(window=window,
            auto_update=True,
            params=params)
t = DoCTrialGenerator(cfg=f.params) 
f.set_trial_generator(t)

# Set up our DoC stimulus
DoCStimulus = load_stimulus_class(stimulus['class'])
stimulus_object = DoCStimulus(window, **stimulus['params'])

if "groups" in stimulus:
    set_stimulus_groups(stimulus['groups'],stimulus_object)

# Add our DoC stimulus to the Task
f.set_stimulus(stimulus_object, stimulus['class'])

start_stop_padding = json_params.get('start_stop_padding', 0.5)

# add prologue to start of session
prologue = json_params.get('prologue', False)
number_runs_rf = json_params.get('number_runs_rf', 1) # 8 is the number of repeats for prod(8min)
prologue_offset = 0
if prologue:
    epilogue_stim_pre = create_receptive_field_mapping(window, number_runs_rf)
    f.add_static_stimulus(
        epilogue_stim_pre,
        when=0.0,
        name="pre_receptive_field_mapping",
    )
    prologue_offset = number_runs_rf*60

injection_start = json_params.get('injection_start', None)  
injection_end = json_params.get('injection_end', None)
short_distrib_start1 = json_params.get('short_distrib_start1', None)  
short_distrib_end1 = json_params.get('short_distrib_end1', None)
change_time_dist1 = json_params.get('change_time_dist1', 0.4)

short_distrib_start2 = json_params.get('short_distrib_start2', None)  
short_distrib_end2 = json_params.get('short_distrib_end2', None)
change_time_dist2 = json_params.get('change_time_dist2', 0.4)

list_epochs = []
# We add the gray period for the injection
if injection_start!=None:
    # We add the epoch to remove the lick spout
    no_lick_spout_epoch = DocNoLickSpout(stage = stage , task=f, delay=prologue_offset+start_stop_padding+injection_start, duration=injection_end-injection_start)
    list_epochs.append(no_lick_spout_epoch)

    TrackSpaceBar = DocSpaceBarTracker(window=window)
    f.add_item(TrackSpaceBar)

if short_distrib_start1:
    DistribMod1 = DocDistribModifier(time_change=change_time_dist1, task=f, delay=prologue_offset+start_stop_padding+short_distrib_start1, duration=short_distrib_end1-short_distrib_start1)
    list_epochs.append(DistribMod1)
    
if short_distrib_start2:
    DistribMod2 = DocDistribModifier(time_change=change_time_dist2, task=f, delay=prologue_offset+start_stop_padding+short_distrib_start2, duration=short_distrib_end2-short_distrib_start2)
    list_epochs.append(DistribMod2)

# We only add the lick spout for the task
doc_object = DocWithLickSpout(stage = stage, task=f, delay=prologue_offset+start_stop_padding, duration=max_task_duration_min*60)
list_epochs.append(doc_object)

epilogue = json_params.get('epilogue', False)
if epilogue:
    epilogue_stim_post = create_receptive_field_mapping(window, number_runs_rf)
    f.add_static_stimulus(
        epilogue_stim_post,
        when='end',
        name="post_receptive_field_mapping"
    )

try:
    f.start_epochs(list_epochs)
except SystemExit:
    print("We prevent camstim exiting the script to complete optotagging")

opto_disabled = json_params.get('disable_opto', True)

if not(opto_disabled):
    from camstim.misc import get_config
    from camstim.zro import agent
    opto_params = deepcopy(json_params.get("opto_params"))
    opto_params["mouse_id"] = json_params["mouse_id"]
    opto_params["output_dir"] = agent.OUTPUT_DIR

    #Read opto levels from ZooKeeper
    opto_params["level_list"] = get_config('Optogenetics')["level_list"]

    optotagging(**opto_params)