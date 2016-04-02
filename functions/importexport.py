#!/usr/bin/env python3
# -*-coding:Utf-8 -*
#

# Copyright 2013-2015 mirandir

# This file is part of Magic Collection.
#
# Magic Collection is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License (version 3) as published by
# the Free Software Foundation.
#
# Magic Collection is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Magic Collection.  If not, see <http://www.gnu.org/licenses/>.

# Functions related to import/export the collection and the decks

from gi.repository import Gtk, GLib
import os
from datetime import date
import shutil
import sys

# imports def.py
import defs

# imports functions
import functions.various
import functions.collection

def import_data():
        '''This function imports the collection and the decks from a SQLite file.'''
        if defs.COLL_LOCK:
                functions.various.message_dialog(defs.STRINGS["import_collection_busy"], 0)
        else:
                # dear user, are you sure ?
                dialogconfirm = Gtk.MessageDialog(defs.MAINWINDOW, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, defs.STRINGS["import_areyousure"])
                responseconfirm = dialogconfirm.run()
                dialogconfirm.destroy()
                if responseconfirm == -8:
                        lastsave = functions.collection.backup_coll("forced")
                        dialog = Gtk.FileChooserDialog(defs.STRINGS["import"], defs.MAINWINDOW, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
                        filefilter = Gtk.FileFilter()
                        filefilter.set_name(defs.STRINGS["exportimport_filetype"])
                        filefilter.add_pattern("*.mcollection")
                        dialog.add_filter(filefilter)
                        restart = 0
                        response = dialog.run()
                        if response == Gtk.ResponseType.OK:
                                filename = dialog.get_filename()
                                try:
                                        shutil.copy(filename, os.path.join(defs.HOMEMC, "collection.sqlite"))
                                except:
                                        functions.various.message_dialog(defs.STRINGS["import_error"], 0)
                                        functions.collection.restore_backup(lastsave)
                                else:
                                        functions.various.message_dialog(defs.STRINGS["import_success"], 0)
                                        restart = 1
                        dialog.destroy()
                        if restart == 1:
                                python = sys.executable
                                os.execl(python, python, os.path.join(defs.PATH_MC, "magic_collection.py"))

def export_data():
        '''This function exports the collection and the decks to a SQLite file.'''
        if defs.COLL_LOCK:
                functions.various.message_dialog(defs.STRINGS["export_collection_busy"], 0)
        else:
                functions.various.lock_db(True, None)
                # we get the current date
                today = date.today()
                month = '%02d' % today.month
                day = '%02d' % today.day
                rtoday = str(today.year) + str(month) + str(day)
                dialog = Gtk.FileChooserDialog(defs.STRINGS["export"], defs.MAINWINDOW, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
                dialog.set_do_overwrite_confirmation(True)
                filefilter = Gtk.FileFilter()
                filefilter.set_name(defs.STRINGS["exportimport_filetype"])
                filefilter.add_pattern("*.mcollection")
                dialog.add_filter(filefilter)
                
                if defs.OS == "windows":
                        user = functions.various.valid_filename_os(os.environ["USERNAME"])
                else:
                        user = functions.various.valid_filename_os(os.environ["USER"])
                
                dialog.set_current_name(defs.STRINGS["export_filename"].replace("%user%", user).replace("%date%", rtoday) + ".mcollection")
                
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                        filename = dialog.get_filename()
                        # we test if we can write here
                        try:
                                open(filename, 'w')
                        except:
                                functions.various.message_dialog(defs.STRINGS["export_write_impossible"], 0)
                        else:
                                os.remove(filename)
                                shutil.copy(os.path.join(defs.HOMEMC, "collection.sqlite"), filename)
                dialog.destroy()
                functions.various.lock_db(False, None)
