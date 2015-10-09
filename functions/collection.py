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

# Some functions for dealing with the collection

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GdkPixbuf, Pango
import os
import sqlite3

# imports def.py
import defs
import functions.various
import functions.db

def read_coll(box, coll_object):
        '''Read the collection and display it in the 'box' widget'''
        for widget in box.get_children():
                box.remove(widget)
        
        conn, c = connect_db()
        c.execute("""SELECT id, name, nb_variant, edition, comment, deck FROM collection""")
        reponses_coll = c.fetchall()
        disconnect_db(conn)
        nb_coll = len(reponses_coll)
        if nb_coll < 1 :
                label_welcome = Gtk.Label()
                label_welcome.set_markup("<big>" + defs.STRINGS["coll_empty_welcome"] + "</big>")
                label_welcome.set_line_wrap(True)
                label_welcome.set_lines(2)
                label_welcome.set_ellipsize(Pango.EllipsizeMode.END)
                label_welcome.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                box.pack_start(label_welcome, True, True, 0)
        else:
                # we create the toolbar
                #toolbar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                toolbar_box = Gtk.ButtonBox(Gtk.Orientation.HORIZONTAL)
                toolbar_box.set_layout(Gtk.ButtonBoxStyle.START)
                toolbar_box.set_spacing(4)
                # the buttons
                coll_object.button_show_details = Gtk.Button()
                coll_object.button_show_details.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="edit-find-replace-symbolic"), Gtk.IconSize.BUTTON))
                coll_object.button_change_quantity = Gtk.Button()
                coll_object.button_change_quantity.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="text-editor-symbolic"), Gtk.IconSize.BUTTON))
                coll_object.button_add_deck = Gtk.Button()
                coll_object.button_add_deck.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="document-new-symbolic"), Gtk.IconSize.BUTTON))
                coll_object.button_estimate = Gtk.Button()
                coll_object.button_estimate.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="accessories-calculator-symbolic"), Gtk.IconSize.BUTTON))
                coll_object.button_delete = Gtk.Button()
                coll_object.button_delete.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="user-trash-symbolic"), Gtk.IconSize.BUTTON))
                
                for button in [coll_object.button_show_details, coll_object.button_change_quantity, coll_object.button_add_deck, coll_object.button_estimate, coll_object.button_delete]:
                        button.set_sensitive(False)
                        toolbar_box.add(button)
                        #toolbar_box.pack_start(button, False, False, 0)
                coll_object.button_delete.set_sensitive(True)
                coll_object.button_estimate.set_sensitive(True)
                toolbar_box.show_all()
                toolbar_box.set_child_secondary(coll_object.button_estimate, True)
                toolbar_box.set_child_secondary(coll_object.button_delete, True)
                box.pack_end(toolbar_box, False, True, 0)
                
                box_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                box_top.set_halign(Gtk.Align.CENTER)
                box.pack_start(box_top, False, False, 0)
                
                # this label displays the number of cards in the collection
                if nb_coll == 1:
                        coll_object.label_nb_card_coll = Gtk.Label(defs.STRINGS["nb_card_coll"].replace("%%%", str(nb_coll)))
                else:
                        coll_object.label_nb_card_coll = Gtk.Label(defs.STRINGS["nb_card_coll_s"].replace("%%%", str(nb_coll)))
                coll_object.label_nb_card_coll.show()
                box_top.pack_start(coll_object.label_nb_card_coll, False, False, 0)
                
                # this button displays the current selection, if any
                selectinfo_button = Gtk.MenuButton(defs.STRINGS["info_select_none_coll"])
                selectinfo_button.set_relief(Gtk.ReliefStyle.NONE)
                popover_selectinfo = Gtk.Popover.new(selectinfo_button)
                popover_selectinfo.set_position(Gtk.PositionType.BOTTOM)
                selectinfo_button.set_popover(popover_selectinfo)
                # we load a specific CSS for this widget
                context_selectinfo_button = selectinfo_button.get_style_context()
                style_provider = Gtk.CssProvider()
                style_provider.load_from_path(os.path.join(defs.PATH_MC, "css", "infoselect_button.css"))
                Gtk.StyleContext.add_provider(context_selectinfo_button, style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                selectinfo_button.show()
                box_top.pack_start(selectinfo_button, False, False, 0)
                selectinfo_button.set_sensitive(False)
                box_top.show_all()
                
                dict_rowcards_in_coll = {}
                where_request = []
                for card_coll in reponses_coll:
                        id_, name, nb_variant, edition, comment, deck = card_coll
                        
                        unique_name = functions.various.get_unique_name(name, nb_variant, edition)
                        bold = 400
                        italic = Pango.Style.NORMAL
                        if deck != "":
                                bold = 700
                        if comment != "":
                                italic = Pango.Style.ITALIC
                        try:
                                nb_card = dict_rowcards_in_coll[unique_name][0]
                        except KeyError:
                                dict_rowcards_in_coll[unique_name] = [1, bold, italic]
                        else:
                                current_bold = dict_rowcards_in_coll[unique_name][1]
                                current_italic = dict_rowcards_in_coll[unique_name][2]
                                if current_bold != bold:
                                        current_bold = 1
                                if current_italic != italic:
                                        current_italic = 1
                                dict_rowcards_in_coll[unique_name] = [nb_card + 1, current_bold, current_italic]
                
                # SQLite limits the number of arguments to 1000                
                conn, c = functions.db.connect_db()
                tmp_req = ""
                for tmp in dict_rowcards_in_coll.keys():
                        tmp_req = tmp_req + "\"" + tmp.replace('"', '""') + "\", "
                tmp_req = tmp_req[:-2]
                request = """SELECT * FROM cards WHERE (name || nb_variante || edition) IN (""" + tmp_req + """)"""
                c.execute(request)
                reponses_db = c.fetchall()
                
                functions.db.disconnect_db(conn)
                
                scrolledwindow = Gtk.ScrolledWindow()
                scrolledwindow.set_min_content_width(560)
                scrolledwindow.set_min_content_height(180)
                scrolledwindow.set_hexpand(True)
                scrolledwindow.set_vexpand(True)
                scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
                
                # "id", "name", "edition", "name_foreign", "colors", colors_pixbuf, "cmc", "type", "artist", "power", "toughness", "rarity", "bold", "italic", "nb_variant", "nb", "unique_name"
                coll_object.mainstore = Gtk.ListStore(str, str, str, str, str, GdkPixbuf.Pixbuf, str, str, str, str, str, str, int, Pango.Style, str, str, str)
                tree_coll = Gtk.TreeView(coll_object.mainstore)
                coll_object.tree_coll = tree_coll
                tree_coll.set_enable_search(False)
                # some work with columns
                columns_to_display = functions.config.read_config("coll_columns").split(";")
                coll_columns_list = functions.various.gen_treeview_columns(columns_to_display, tree_coll)
                
                select = tree_coll.get_selection()
                coll_object.select = select
                select.set_mode(Gtk.SelectionMode.MULTIPLE)
                select.connect("changed", coll_object.send_id_to_loader_with_selectinfo, "blip", "blop", 0, selectinfo_button)
                selectinfo_button.connect("clicked", coll_object.selectinfo_click, select, popover_selectinfo)
                coll_object.mainselect = select
                scrolledwindow.add(tree_coll)
                
                tree_coll.show_all()
                scrolledwindow.show_all()
                
                box.pack_start(scrolledwindow, True, True, 0)
                
                cards = functions.various.prepare_cards_data_for_treeview(reponses_db)
                
                for unique_name, card in cards.items():
                        nb_card = dict_rowcards_in_coll[unique_name][0]
                        bold_card = dict_rowcards_in_coll[unique_name][1]
                        italic_card = dict_rowcards_in_coll[unique_name][2]
                        
                        coll_object.mainstore.insert_with_valuesv(-1, range(17), [card["id_"], card["name"], card["edition_ln"], card["nameforeign"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold_card, italic_card, card["nb_variant"], nb_card, unique_name])
                
                coll_object.mainstore.set_sort_column_id(7, Gtk.SortType.ASCENDING)
                coll_object.mainstore.set_sort_column_id(2, Gtk.SortType.ASCENDING)
                if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                        coll_object.mainstore.set_sort_column_id(3, Gtk.SortType.ASCENDING)
                else:
                        coll_object.mainstore.set_sort_column_id(1, Gtk.SortType.ASCENDING)

def connect_db():
        '''Return the connection to the collection'DB and the cursor'''
        conn = sqlite3.connect(os.path.join(defs.HOMEMC, "collection.sqlite"))
        conn.create_function('py_lara', 1, functions.various.py_lara)
        conn.create_function('py_int', 1, functions.various.py_int)
        conn.create_function('py_lower', 1, functions.various.py_lower)
        c = conn.cursor()
        return(conn, c)

def disconnect_db(conn):
        conn.commit()
        conn.close()

def create_db_coll():
        conn, c = connect_db()
        # we create the table 'collection'
        c.execute("""
        CREATE TABLE IF NOT EXISTS collection(
             id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
             name TEXT,
             nb_variant TEXT,
             edition TEXT,
             date TEXT,
             condition TEXT,
             lang TEXT,
             foil TEXT,
             loaned_to TEXT,
             comment TEXT,
             deck TEXT
        )
        """)
        
        # we create the table 'decks'
        c.execute("""
        CREATE TABLE IF NOT EXISTS decks(
             id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
             name TEXT,
             comment TEXT,
             proxies TEXT
        )
        """)
        
        disconnect_db(conn)
