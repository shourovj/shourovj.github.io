#!/bin/bash

pelican . -t ../saxon-theme -o ../../blog
python post_process.py
