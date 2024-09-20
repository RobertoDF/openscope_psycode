## Installation

### Dependencies:

- Windows OS (see **Camstim package**)
- python 2.7
- psychopy 1.82.01
- camstim 0.2.4

### Installation with [Anaconda](https://docs.anaconda.com/anaconda/install/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html):

1. Navigate to repository and install conda environment.  
    `conda env create -f environment.yml`
2. Activate the environment.  
    `conda activate allen_stimulus`
3. Install the AIBS `camstim` package in the environment.  
    `pip install camstim/.`
4. Download required video clips from [movie_clips.zip](https://tigress-web.princeton.edu/~dmturner/allen_stimulus/movie_clips.zip)
   Extract into the `data` directory.

## Task

![Task blocks](images/Task_structure.png)
![Task blocks](images/Change_detection_task_structure.png)

## Passsive block

### Receptive fields mapping: 
Gabors (250 ms in duration without gaps between stimuli) of 20° in diameter presented in a 9x9 grid. Gabors will have a temporal frequency of 4 Hz, a spatial frequency of 0.08 cycles/degree and 3 orientation (0, 45 , 90). There will be 5 trials for each condition (81 positions). Total time: 81x3x0.250 s = 303.75 s = 5.0625 min.

### Surround suppression: 
Gabors (0.3 s duration separated by 0.2 s of blank screen) of 4 diameters (21˚, 36˚, 55˚, 75) presented in 5 locations. Gabors will have a temporal frequency of 2 Hz, a spatial frequency of 0.04 cycles/degree and 4 orientation (0, 45, 90, 135). There will be 18 trials for each condition (4 positions). Total time: 18x4x5x5x0.5 s = 900 s = 15 min. 
