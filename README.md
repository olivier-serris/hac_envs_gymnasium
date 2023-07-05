# Three environments from the Hierarchical Actor-Critic paper wrapped in gymnasium interface

The original implementation of the Hierarchical Actor-Critic algorithm and the environments provided in this package (without gym compatibility) can be found in [Andrew Levy's GitHub repository](https://github.com/andrew-j-levy/Hierarchical-Actor-Critc-HAC-).

This repository is adapted from : 
https://github.com/martius-lab/HiTS/tree/master/hac_envs



## Installation

```bash
pip install ./
```

## Usage

```python
import gymnasium
import hac_envs_gymnasium

pendulum_env = gym.make("PendulumHAC-v1")
ur5_reacher_env = gym.make("UR5Reacher-v1")
ant_4_rooms_env = gym.make("AntFourRooms-v1")
```
