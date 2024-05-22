#!/bin/bash
# source ~/.zshrc
# eval "$(conda shell.zsh hook)"
#Create and activate a new Conda environment
conda create -n audio_streaming_env python=3.8
conda activate audio_streaming_env

# Install necessary Python packages
conda install -n audio_streaming_env flask pyaudio pyzmq numpy msgpack-python pyaudio requests