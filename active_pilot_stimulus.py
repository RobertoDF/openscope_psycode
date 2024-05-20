import sys
import argparse
import yaml
import numpy as np
from six import iteritems
from camstim.change import DoCTask, DoCTrialGenerator
from camstim.behavior import Epoch
from camstim.sweepstim import MovieStim
from camstim.experiment import EObject, ETimer
from psychopy import monitors

try:
    from pyglet.window import key
except:
    warnings.warn("Couldn't set up pyglet keybinds.", ImportWarning)
from qtpy import QtCore
from camstim import Window, Warp
import logging
import time
import zmq
from zro import Proxy
stage = Proxy("tcp://localhost:6001", serialization="json", timeout=.5)  # ZRO Proxy to PhidgetServer
logging.basicConfig(level=logging.DEBUG)

try:
    stage.uptime
except zmq.error.Again:
    raise Exception("PhidgetServer is not running. Please start PhidgetServer before running this script.")
from psychopy import visual
from camstim import Stimulus, Window, Warp


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
        start_stop_padding = self._doc_config['start_stop_padding']
        self._task_scheduled_end = time.clock() + self._doc_config['max_task_duration_min'] * 60.0 + start_stop_padding
        self.stim_off()
        self.started.emit()
        ETimer.singleShot(start_stop_padding, self._next_trial)

class DocNoLickSpout(Epoch):
    """ DoC Epoch that retracts the lick spout. """
    def __init__(self, stage, *args, **kwargs):
        super(DocNoLickSpout, self).__init__(*args, **kwargs)
        self.stage = stage
    def _on_entry(self):
        logging.info("Retracting lickspout")
        self.stage.retract_lickspout()
    def _on_exit(self):
        logging.info("Extending lickspout")
        self.stage.extend_lickspout()
    
class DocWithLickSpout(Epoch):
    """ DoC Epoch that retracts the lick spout. """
    def __init__(self, stage, *args, **kwargs):
        super(DocWithLickSpout, self).__init__(*args, **kwargs)
        self.stage = stage
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
        screen=1,
        monitor='Gamma1.Luminance50',
        color=stimulus['luminance_matching_intensity'],
        warp=Warp.Spherical,
    )
else : 
    window = Window(
        fullscr=True,
        screen=1,
        monitor='Gamma1.Luminance50',
        warp=Warp.Spherical,
    )

# Set up Task
params = {}
f = AddEpochDoc(window=window,
            auto_update=True,
            params=params)
t = DoCTrialGenerator(cfg=f.params) # This also subject to change
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
prologue = json_params.get('prologue', None)
if prologue:

    prologue_movie = MovieStim(
        window=window,
        start_time=0.0,
        stop_time=start_stop_padding,
        flip_v=True,
        **prologue['params']
    )
    f.add_static_stimulus(
        prologue_movie,
        when=0.0,
        name=prologue['name'],
    )

# add fingerprint to end of session
epilogue = json_params.get('epilogue', None)

injection_start = json_params.get('injection_start', 10)  
injection_end = json_params.get('injection_end', 20)

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
    no_lick_spout_epoch = DocNoLickSpout(stage = stage , task=f, delay=injection_start, duration=injection_end-injection_start)
    f.add_epoch(no_lick_spout_epoch)
    list_epochs.append(no_lick_spout_epoch)

    TrackSpaceBar = DocSpaceBarTracker(window=window)
    f.add_item(TrackSpaceBar)

    # Full screen gray period
    stimulus_obj = Stimulus(visual.GratingStim(window,
                            pos=(0, 0),
                            units='deg',
                            size=(250, 250),
                            mask="None",
                            texRes=256,
                            contrast=1,
                            sf=0,
                            ),
	    sweep_params={},
            sweep_length=injection_end-injection_start,
            start_time=injection_start,
            blank_length=0,
            blank_sweeps=0,
            fps=60,
            runs = 1,
            shuffle=False,
            save_sweep_table=True,
        )

    f.add_static_stimulus(
        stimulus_obj,
        when=injection_start,
        name="injection_period",
    )
if short_distrib_start1:
    DistribMod1 = DocDistribModifier(time_change=change_time_dist1, task=f, delay=short_distrib_start1, duration=short_distrib_end1-short_distrib_start1)
    f.add_epoch(DistribMod1)
    list_epochs.append(DistribMod1)
    
if short_distrib_start2:
    DistribMod2 = DocDistribModifier(time_change=change_time_dist2, task=f, delay=short_distrib_start2, duration=short_distrib_end2-short_distrib_start2)
    f.add_epoch(DistribMod2)
    list_epochs.append(DistribMod2)

# We only add the lick spout for the task
DocWithLickSpout = DocWithLickSpout(stage = stage, task=f, delay=start_stop_padding, duration=max_task_duration_min*60)
f.add_epoch(DocWithLickSpout)
list_epochs.append(DocWithLickSpout)

if epilogue:
    if prologue:
        assert epilogue['params']['frame_length'] == prologue['params']['frame_length'], "`frame_length` must match between prologue and epilogue"

    epilogue_movie = MovieStim(
        window=window,
        start_time=start_stop_padding,
        stop_time=None,
        flip_v=True,
        **epilogue['params']
    )
    f.add_static_stimulus(
        epilogue_movie,
        when='end',
        name=epilogue['name'],
    )

# Run it
f.start_epochs(list_epochs)