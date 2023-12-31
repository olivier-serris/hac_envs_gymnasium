from gymnasium import spaces
from gymnasium_robotics import GoalEnv
from inspect import getfullargspec
from mujoco_py import MjViewer
import numpy as np
from typing import Optional

from .environment import Environment


class GymWrapper(GoalEnv):
    """Wraps HAC environment in gym environment.
    Assumes hac_env is an instance of Environment as defined in the
    original Hierarchical Actor-Critic implementation at
    https://github.com/andrew-j-levy/Hierarchical-Actor-Critc-HAC-
    """

    def __init__(self, hac_env, observation_space_bounds=None):
        self.hac_env = hac_env
        self.max_episode_steps = hac_env.max_actions
        self.viewer = None

        # action space
        action_low = hac_env.action_offset - hac_env.action_bounds
        action_high = hac_env.action_offset + hac_env.action_bounds
        self.action_space = spaces.Box(
            low=action_low, high=action_high, dtype=np.float32
        )

        # partial observation space
        if observation_space_bounds is None:
            # appropriate for UR5 and Pendulum
            partial_obs_space = spaces.Box(
                low=-np.inf, high=np.inf, shape=(hac_env.state_dim,), dtype=np.float32
            )
        else:
            partial_obs_space = spaces.Box(
                low=observation_space_bounds[:, 0],
                high=observation_space_bounds[:, 1],
                dtype=np.float32,
            )

        # goal spaces (Use goal space used for training in original paper)
        goal_low = np.array(hac_env.goal_space_train)[:, 0]
        goal_high = np.array(hac_env.goal_space_train)[:, 1]
        desired_goal_space = spaces.Box(low=goal_low, high=goal_high, dtype=np.float32)
        achieved_goal_space = desired_goal_space

        # observation space, including desired and achieved goal
        self.observation_space = spaces.Dict(
            {
                "observation": partial_obs_space,
                "desired_goal": desired_goal_space,
                "achieved_goal": achieved_goal_space,
            }
        )

        self.reset()

    def _get_obs(self, state):
        achieved_goal = self.hac_env.project_state_to_end_goal(self.hac_env.sim, state)
        obs = {
            "observation": state,
            "desired_goal": self.desired_goal,
            "achieved_goal": achieved_goal,
        }
        return obs

    def compute_reward(self, achieved_goal, desired_goal, info):
        tolerance = self.hac_env.end_goal_thresholds
        abs_dist = np.abs((desired_goal - achieved_goal))
        goal_reached = (abs_dist <= tolerance).all(axis=-1)
        reward = goal_reached - 1
        return reward.flatten()

    def step(self, action):
        state = self.hac_env.execute_action(action)
        self.n_steps += 1
        obs = self._get_obs(state)
        info = {}
        reward = self.compute_reward(obs["achieved_goal"], obs["desired_goal"], info)
        terminated = reward == 0.0
        truncated = np.logical_and(
            np.logical_not(terminated), self.n_steps >= self.max_episode_steps
        )
        info["is_success"] = terminated

        return obs, reward, terminated, truncated, info

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        if seed:
            np.random.seed(seed)
        self.desired_goal = self.hac_env.get_next_goal(test=False)
        spec = getfullargspec(self.hac_env.reset_sim)
        if "next_goal" in spec.args:
            state = self.hac_env.reset_sim(self.desired_goal)
        else:
            state = self.hac_env.reset_sim()
        obs = self._get_obs(state)
        self.n_steps = 0
        return obs, {}

    def update_subgoals(self, subgoals):
        self.hac_env.display_subgoals(subgoals + [None])

    def update_timed_subgoals(self, timed_subgoals, tolerances):
        subgoals = [tg.goal for tg in timed_subgoals if tg is not None]
        # NOTE: Visualization of time component of timed subgoals is not supported
        # by HAC environments.
        self.update_subgoals(subgoals)

    def render(self):
        if self.viewer is None:
            self.viewer = MjViewer(self.hac_env.sim)
        self.viewer.render()

    def compute_terminated(self, achieved_goal, desired_goal, info):
        return self.compute_reward(achieved_goal, desired_goal, info) == 0
