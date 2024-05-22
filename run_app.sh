#!/bin/bash

# Activate the Conda environment
source activate audio_streaming_env
# conda install -n audio_streaming_env requests


python gui.py
# python server.py
# Run the server script