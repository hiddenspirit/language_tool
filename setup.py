from setuptools import setup
from setuptools.command.build_py import build_py
import os
import sys

# Ensure current directory is in sys.path for isolated builds
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class CustomBuildPy(build_py):
    def run(self):
        # Download LanguageTool only when building a wheel or installing (not sdist)
        if "sdist" not in sys.argv:
            from download_lt import download_lt
            download_lt()
        super().run()

setup(
    cmdclass={
        'build_py': CustomBuildPy,
    }
)
