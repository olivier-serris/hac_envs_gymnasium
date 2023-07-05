import gymnasium as gym
import hac_envs_gymnasium
import os
from xpag.wrappers import gym_vec_env
from xpag.wrappers.reset_done import ResetDoneWrapper
import numpy as np


def test_episode():
    os.environ["LD_PRELOAD"] = "/usr/lib/x86_64-linux-gnu/libGLEW.so"
    env = gym.make("UR5Reacher-v1")
    obs, info = env.reset()
    for _ in range(10_000):
        res = env.step(env.action_space.sample())


def test_render():
    env = gym.make("UR5Reacher-v1")
    obs, info = env.reset()
    for _ in range(10_000):
        res = env.step(env.action_space.sample())
        env.render()


def test_reset_done():
    env = gym.make("UR5Reacher-v1")
    env = ResetDoneWrapper(env)
    obs, info = env.reset()
    for _ in range(10_000):
        observation, reward, terminated, truncated, info = env.step(
            env.action_space.sample()
        )
        done = np.logical_or(terminated, truncated)
        if done.any():
            env.reset_done(0, np.array(done).reshape((1, 1)))


def test_xpag():
    env, eval_env, infos = gym_vec_env("UR5Reacher-v1", num_envs=5)
    # print(env.single_observation_space)
    obs, info = env.reset()
    # print(obs)

    for _ in range(10_000):
        observation, reward, terminated, truncated, info = env.step(
            env.action_space.sample()
        )
        done = np.logical_or(terminated, truncated)
        if done.any():
            env.reset_done(done)
            # env.reset()


if __name__ == "__main__":
    test_episode()
    test_render()
    test_reset_done()
    test_xpag()
    print("-----------------------END OF THE MAIN THREAD-----------------------")
