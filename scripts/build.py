from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.install import install
import subprocess

class CustomBuild(build_py):
    def run(self):
        subprocess.run(['make', 'build'], check=True)
        super().run()
