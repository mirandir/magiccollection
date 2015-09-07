#!/usr/bin/env python3
# -*-coding:Utf-8 -*
#
# Main script for Magic Collection

import sys
import os
# imports mc
import objects.mc

import functions.various

import defs

os.chdir(defs.HOME)
functions.various.check_folders_config()

app = objects.mc.MagicCollection()

exit_status = app.run(sys.argv)
sys.exit(exit_status)
