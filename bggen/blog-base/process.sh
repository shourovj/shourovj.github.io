#!/bin/bash

pelican content -t ../saxon-theme -o ../../blog
python post_process.py
