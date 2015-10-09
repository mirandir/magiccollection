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

# Decks class for Magic Collection

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GdkPixbuf
import sys
import os

# imports def.py
import defs
# imports objects
import objects.mc
# imports functions
import functions.cardviewer
import functions.config
import functions.db

class Decks:
        '''The decks class. Manage the decks part of MC.'''
        def __init__(self, mainwindow):
                self.mainstore = None
                self.mainselect = None
                
                self.mainbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
                self.mainbox.set_margin_top(5)
                self.mainbox.set_margin_bottom(5)
                self.mainbox.set_margin_left(5)
                self.mainbox.set_margin_right(5)
                
                mainwindow.main_stack.add_titled(self.mainbox, "decks", defs.STRINGS["decks"])
                
                self.card_viewer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
                right_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                self.mainbox.pack_start(self.card_viewer, False, False, 0)
                self.mainbox.pack_start(separator, False, False, 0)
                self.mainbox.pack_start(right_content, True, True, 0)
                
                # we load nothing in the card viewer
                self.load_card(None, 0)
                
                self.mainbox.show_all()
        
        def send_id_to_loader(self, selection, integer, TreeViewColumn, simple_search):
                model, pathlist = selection.get_selected_rows()
                if pathlist != None:
                        tree_iter = model.get_iter(pathlist[0])
                        id_ = model.get_value(tree_iter, 0)
                        self.load_card(id_, simple_search)
        
        def load_card(self, cardid, simple_search):
                '''Load a card in the card viewer'''
                functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
        
        def load_card_from_outside(self, widget, cardid, list_widgets_to_destroy, simple_search):
                for widget in list_widgets_to_destroy:
                        widget.destroy()
                functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
