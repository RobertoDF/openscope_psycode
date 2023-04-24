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

### Stimulus design

1. For the random stimulus order (days #0 and #5):

   * there are 4 difference choices of a 2 sec duration stimulus 
     * movie clip A 
     * movie clip B 
     * movie clip C 
     * a constant grey screen, X
   * these will be displayed in a randomized order.
   * this order will be exactly the same on day #0 and day #5. 
   * there will be 525 repeats of each of the 4 stimuli.


2. For the sequence stimulus order (day #1 – #4):

   * the 3 movie clips are shown in the same repeated order, ABC, for 50 minutes. 
   * this will result in 500 repeats of this movie clip sequence. 
   * in the last 20 minutes, the stimuli will be shown in a random order with the grey screen intermixed, as on days #0 and #5
   * a different random sequence will be chosen and kept the same across days #1 – #4.
   * this will result in 150 repeats of each of these 4 stimuli.