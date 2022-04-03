#!/bin/bash
pip install --no-cache-dir -r requirements.txt

##############################################################
# Expand by adding running of scripts in d.entrypoint folder #
##############################################################
echo "Starting chatbot"
python bot.py
