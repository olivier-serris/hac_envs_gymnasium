from setuptools import setup, find_packages

setup(
    name="hac_envs_gymnasium",
    packages=find_packages(),
    version="1.0",
    install_requires=[
        "numpy",
        "gymnasium",
        "mujoco-py==2.1.2.14",
        "gymnasium-robotics",
    ],
    include_package_data=True,
)
