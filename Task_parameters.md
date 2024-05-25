## Change detection task parameters

Our version of the change detection task (CDT) introduces two modifications:
*   2 CDT blocks within session separated by a break to allow injection
*  Each CDT block is further divided in two sections (short & long) in which the image changes are drawn from different distributions

#### Some parameters regarding these modifictions have to be optimized

1. Duration of the pre and post blocks
2. Duration of the short & long sections within each CDT

## Duration of the pre and post blocks

The aim is to have similar performance/engagement between the two pre- post- injection blocks.
It is paramount that the mouse is not satiated after the 
first block, therefore not engaging in the task afterward. 

### Option 1
To ensure similar engagement we can look at the the mean reward amount or number 
of hit trials per session in the 
[visual-behavior-neuropixels dataset](https://portal.brain-map.org/circuits-behavior/visual-behavior-neuropixels)
and dynamically change the block duration contingent on the number of hit trials/rewards accumulated.

Training is structured in the following stages (12 example mice):
![Training_stages_example_mice](images/Training_stages_example_mice.png)

We compute the average reward per mouse during the last 2 stages of training:
![total_reward_volume](images/total_reward_volume.png)
or on recording days only:
![total_reward_volume](images/total_reward_volume_2.png)

We also compute the number of hit trials during the last 2 stages of training:
![hit_trial](images/Hit_trial.png)
or on recording days only:![hit_trial](images/Hit_trial_2.png)

### Option 2

We can hardcode the duration of the blocks by looking at 
the mean time necessary to reach 50% of the total reward in each session. Analysis run 
on 153 sessions, all recording sessions available, including sessions with abnormalities 
in either histology or recorded activity (`cache.get_ecephys_session_table(filter_abnormalities=False)`).

![Half_reward](images/Half_reward.png)


## Duration of the short & long sections within each CDT

The aim here is to have the same number of hit trials in each section. We can expect the mice to 
collect more rewards in the section where image changes tend to happen earlier. We should adjust for this 
by reducing the duration of this section. First step here is to decide precisely the parameters of the 
distributions. From the proposal: *"The coefficient of the geometric distributions 
(change_time_scale) will be 0.1 and 0.4."*