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

from gi.repository import Gtk, Gio, GdkPixbuf, Pango, GLib
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
        c.execute("""SELECT id_coll, id_card, comment, deck FROM collection""")
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
                toolbar_box = Gtk.ButtonBox(Gtk.Orientation.HORIZONTAL)
                toolbar_box.set_layout(Gtk.ButtonBoxStyle.START)
                toolbar_box.set_spacing(4)
                # the buttons
                coll_object.button_search_coll = Gtk.ToggleButton()
                coll_object.button_search_coll.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="edit-find-symbolic"), Gtk.IconSize.BUTTON))
                coll_object.button_show_details = Gtk.Button()
                coll_object.button_show_details.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="text-editor-symbolic"), Gtk.IconSize.BUTTON))
                coll_object.button_change_quantity = Gtk.Button()
                coll_object.button_change_quantity.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="text-editor-symbolic"), Gtk.IconSize.BUTTON))
                coll_object.button_add_deck = Gtk.Button()
                coll_object.button_add_deck.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="document-new-symbolic"), Gtk.IconSize.BUTTON))
                coll_object.button_estimate = Gtk.Button()
                coll_object.button_estimate.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="accessories-calculator-symbolic"), Gtk.IconSize.BUTTON))
                coll_object.button_delete = Gtk.Button()
                coll_object.button_delete.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="user-trash-symbolic"), Gtk.IconSize.BUTTON))
                
                for button in [coll_object.button_search_coll, coll_object.button_show_details, coll_object.button_change_quantity, coll_object.button_add_deck, coll_object.button_estimate, coll_object.button_delete]:
                        button.set_sensitive(False)
                        toolbar_box.add(button)
                coll_object.button_search_coll.set_sensitive(True)
                coll_object.button_delete.set_sensitive(True)
                coll_object.button_estimate.set_sensitive(True)
                toolbar_box.show_all()
                toolbar_box.set_child_secondary(coll_object.button_estimate, True)
                toolbar_box.set_child_secondary(coll_object.button_delete, True)
                box.pack_end(toolbar_box, False, True, 0)
                
                # we create the SearchBar for searching in the collection
                searchbar = Gtk.SearchBar()
                searchbar.get_style_context().remove_class("search-bar")
                coll_object.button_search_coll.connect("toggled", show_hide_searchbar, searchbar)
                searchbar.add(gen_grid_search_coll(coll_object, searchbar))
                box.pack_end(searchbar, False, True, 0)
                
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
                        id_coll, id_card, comment, deck = card_coll
                        
                        bold = 400
                        italic = Pango.Style.NORMAL
                        if deck != "":
                                italic = Pango.Style.ITALIC
                        if comment != "":
                                bold = 700
                        try:
                                nb_card = dict_rowcards_in_coll[id_card][0]
                        except KeyError:
                                dict_rowcards_in_coll[id_card] = [1, bold, italic]
                        else:
                                current_bold = dict_rowcards_in_coll[id_card][1]
                                current_italic = dict_rowcards_in_coll[id_card][2]
                                if current_bold != bold:
                                        current_bold = 700
                                if current_italic != italic:
                                        current_italic = Pango.Style.ITALIC
                                dict_rowcards_in_coll[id_card] = [nb_card + 1, current_bold, current_italic]
                
                # SQLite limits the number of arguments to 1000                
                conn, c = functions.db.connect_db()
                tmp_req = ""
                for tmp in dict_rowcards_in_coll.keys():
                        tmp_req = tmp_req + "\"" + str(tmp) + "\", "
                tmp_req = tmp_req[:-2]
                request = """SELECT * FROM cards WHERE cards.id IN (""" + tmp_req + """)"""
                c.execute(request)
                reponses_db = c.fetchall()
                
                functions.db.disconnect_db(conn)
                
                scrolledwindow = Gtk.ScrolledWindow()
                scrolledwindow.set_min_content_width(560)
                scrolledwindow.set_min_content_height(180)
                scrolledwindow.set_hexpand(True)
                scrolledwindow.set_vexpand(True)
                scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
                
                # "id", "name", "edition", "name_foreign", "colors", colors_pixbuf, "cmc", "type", "artist", "power", "toughness", "rarity", "bold", "italic", "nb_variant", "nb"
                coll_object.mainstore = Gtk.ListStore(str, str, str, str, str, GdkPixbuf.Pixbuf, str, str, str, str, str, str, int, Pango.Style, str, str)
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
                
                for id_, card in cards.items():
                        nb_card = dict_rowcards_in_coll[id_][0]
                        bold_card = dict_rowcards_in_coll[id_][1]
                        italic_card = dict_rowcards_in_coll[id_][2]
                        
                        coll_object.mainstore.insert_with_valuesv(-1, range(17), [card["id_"], card["name"], card["edition_ln"], card["nameforeign"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold_card, italic_card, card["nb_variant"], nb_card])
                
                coll_object.mainstore.set_sort_column_id(7, Gtk.SortType.ASCENDING)
                coll_object.mainstore.set_sort_column_id(2, Gtk.SortType.ASCENDING)
                if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                        coll_object.mainstore.set_sort_column_id(3, Gtk.SortType.ASCENDING)
                else:
                        coll_object.mainstore.set_sort_column_id(1, Gtk.SortType.ASCENDING)

def show_hide_searchbar(togglebutton, searchbar):
        '''Show / hide the searchbar'''
        if togglebutton.get_active():
                searchbar.get_style_context().add_class("search-bar")
                searchbar.show()
                searchbar.set_search_mode(True)
        else:
                searchbar.set_search_mode(False)
                searchbar.get_style_context().remove_class("search-bar")

def gen_grid_search_coll(coll_object, searchbar):
        '''Return a GtkGrid with all widgets for searching in the collection.'''
        def comboboxtext_changed(comboboxtext, entry):
                defs.MAINWINDOW.advancedsearch.comboboxtext_changed(comboboxtext, entry)
        
        def on_button_radio_op(button, name, entry, popover):
                defs.MAINWINDOW.advancedsearch.on_button_radio_op(button, name, entry, popover)
        
        def entry_operator_choice(entry, icon, void):
                defs.MAINWINDOW.advancedsearch.entry_operator_choice(entry, icon, void)
        
        def update_button_search_and_reset(entry, entry1, entry2, entry3, entry4, button_search, button_reset_search):
                text_in_entry = 0
                for widget in [entry1, entry2, entry3, entry4]:
                        if widget.get_text() != "":
                                text_in_entry = 1
                
                if text_in_entry == 0:
                        sensitive = False
                else:
                        sensitive = True
                if defs.AS_LOCK == False and defs.COLL_LOCK == False:
                        button_search.set_sensitive(sensitive)
                button_reset_search.set_sensitive(sensitive)
        
        def back_to_coll(button):
                def coll_count_cards():
                        conn, c = connect_db()
                        c.execute("""SELECT * FROM collection""")
                        reponses_coll = c.fetchall()
                        disconnect_db(conn)
                        nb_coll = len(reponses_coll)
                        if nb_coll == 1:
                                coll_object.label_nb_card_coll.set_label(defs.STRINGS["nb_card_coll"].replace("%%%", str(nb_coll)))
                        else:
                                coll_object.label_nb_card_coll.set_label(defs.STRINGS["nb_card_coll_s"].replace("%%%", str(nb_coll)))
                        
                coll_object.tree_coll.set_model(coll_object.mainstore)
                button.set_sensitive(False)
                GLib.idle_add(coll_count_cards)
        
        def reset_search(button, entry1, entry2, entry3, entry4):
                defs.MAINWINDOW.advancedsearch.reset_search(button, entry1, entry2, entry3, entry4)
        
        def launch_request(request, dict_rowcards_in_coll, quantity_card_req):
                conn, c = functions.db.connect_db()
                c.execute("ATTACH DATABASE ? AS db_coll", (os.path.join(defs.HOMEMC, "collection.sqlite"),))
                c.execute(request)
                reponses_db = c.fetchall()
                functions.db.disconnect_db(conn)
                coll_object.searchstore = Gtk.ListStore(str, str, str, str, str, GdkPixbuf.Pixbuf, str, str, str, str, str, str, int, Pango.Style, str, str)
                
                cards = functions.various.prepare_cards_data_for_treeview(reponses_db)
                nb_results = len(reponses_db)
                nb_cards_disp = 0
                
                for id_, card in cards.items():
                        nb_card = dict_rowcards_in_coll[id_][0]
                        bold_card = dict_rowcards_in_coll[id_][1]
                        italic_card = dict_rowcards_in_coll[id_][2]
                        
                        coll_object.searchstore.insert_with_valuesv(-1, range(17), [card["id_"], card["name"], card["edition_ln"], card["nameforeign"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold_card, italic_card, card["nb_variant"], nb_card])
                        nb_cards_disp = nb_cards_disp + nb_card
                
                coll_object.searchstore.set_sort_column_id(7, Gtk.SortType.ASCENDING)
                coll_object.searchstore.set_sort_column_id(2, Gtk.SortType.ASCENDING)
                if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                        coll_object.searchstore.set_sort_column_id(3, Gtk.SortType.ASCENDING)
                else:
                        coll_object.searchstore.set_sort_column_id(1, Gtk.SortType.ASCENDING)
                
                coll_object.tree_coll.set_model(coll_object.searchstore)
                coll_object.button_back_coll.set_sensitive(True)
                
                if quantity_card_req != None:
                        nb_results = nb_cards_disp
                if nb_results < 2:
                        coll_object.label_nb_card_coll.set_label(defs.STRINGS["nb_card_found_coll"].replace("%%%", str(nb_results)))
                else:
                        coll_object.label_nb_card_coll.set_label(defs.STRINGS["nb_card_found_coll_s"].replace("%%%", str(nb_results)))
        
        def prepare_request(widget, search_widgets_list, overlay_right_content):
                if defs.AS_LOCK == False and defs.COLL_LOCK == False:
                        request_list = functions.db.prepare_request(search_widgets_list, "coll")
                        request = request_list[0]
                        quantity_card_req = request_list[1]
                        if request != None:
                                conn, c = connect_db()
                                c.execute("""SELECT * FROM collection""")
                                reponses_coll = c.fetchall()
                                disconnect_db(conn)
                                
                                dict_rowcards_in_coll = {}
                                where_request = []
                                for card_coll in reponses_coll:
                                        id_coll, id_card, date, condition, lang, foil, loaned_to, comment, deck = card_coll
                                        
                                        bold = 400
                                        italic = Pango.Style.NORMAL
                                        if deck != "":
                                                italic = Pango.Style.ITALIC
                                        if comment != "":
                                                bold = 700
                                        try:
                                                nb_card = dict_rowcards_in_coll[id_card][0]
                                        except KeyError:
                                                dict_rowcards_in_coll[id_card] = [1, bold, italic]
                                        else:
                                                current_bold = dict_rowcards_in_coll[id_card][1]
                                                current_italic = dict_rowcards_in_coll[id_card][2]
                                                if current_bold != bold:
                                                        current_bold = 700
                                                if current_italic != italic:
                                                        current_italic = Pango.Style.ITALIC
                                                dict_rowcards_in_coll[id_card] = [nb_card + 1, current_bold, current_italic]
                                
                                # SQLite limits the number of arguments to 1000                
                                tmp_req = ""
                                for tmp in dict_rowcards_in_coll.keys():
                                        tmp_req = tmp_req + "\"" + str(tmp) + "\", "
                                tmp_req = tmp_req[:-2]
                                request = request + """ AND cards.id IN (""" + tmp_req + """)"""
                                
                                if quantity_card_req != None:
                                        request = request + """ GROUP BY coll.id_card """ + quantity_card_req
                                
                                GLib.idle_add(launch_request, request, dict_rowcards_in_coll, quantity_card_req)                                
        
        box_search_coll = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_search_coll_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box_search_coll_top.set_homogeneous(True)
        
        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(4)
        
        comboboxtext1 = Gtk.ComboBoxText()
        comboboxtext2 = Gtk.ComboBoxText()
        comboboxtext3 = Gtk.ComboBoxText()
        comboboxtext4 = Gtk.ComboBoxText()
        for comboboxtext in [comboboxtext1, comboboxtext2, comboboxtext3, comboboxtext4]:
                for i in range(len(defs.SEARCH_ITEMS)):
                        comboboxtext.append(defs.SEARCH_ITEMS[i][0], defs.SEARCH_ITEMS[i][1])
        
        entry1 = Gtk.Entry()
        entry2 = Gtk.Entry()
        entry3 = Gtk.Entry()
        entry4 = Gtk.Entry()
        
        searchbar.connect_entry(entry1)
        
        comboboxtext1.set_active(0)
        comboboxtext1.connect("changed", comboboxtext_changed, entry1)
        comboboxtext2.set_active(2)
        comboboxtext2.connect("changed", comboboxtext_changed, entry2)
        comboboxtext3.set_active(1)
        comboboxtext3.connect("changed", comboboxtext_changed, entry3)
        comboboxtext4.set_active(3)
        comboboxtext4.connect("changed", comboboxtext_changed, entry4)
        
        button_reset_search = Gtk.Button()
        button_reset_search.set_sensitive(False)
        button_reset_search.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="edit-clear-all-symbolic"), Gtk.IconSize.BUTTON))
        button_reset_search.connect("clicked", reset_search, entry1, entry2, entry3, entry4)
        
        button_search = Gtk.Button(defs.STRINGS["search_coll"])
        coll_object.button_search = button_search
        button_search.set_sensitive(False)
        button_search.connect("clicked", prepare_request, [[entry1, comboboxtext1], [entry2, comboboxtext2], [entry3, comboboxtext3], [entry4, comboboxtext4]], coll_object.overlay_right_content)
        
        button_back_coll = Gtk.Button(defs.STRINGS["back_to_coll"])
        coll_object.button_back_coll = button_back_coll
        button_back_coll.set_sensitive(False)
        button_back_coll.connect("clicked", back_to_coll)
        
        for entry in [entry1, entry2, entry3, entry4]:
                icon_search = Gio.ThemedIcon(name="edit-find-symbolic")
                entry.set_icon_from_gicon(Gtk.EntryIconPosition.SECONDARY, icon_search)
                entry.set_icon_sensitive(Gtk.EntryIconPosition.SECONDARY, False)
                if defs.DISPLAY_WIDTH > 1024:
                        entry.set_size_request(230, -1)
                entry.connect("icon-press", entry_operator_choice)
                entry.connect("activate", prepare_request, [[entry1, comboboxtext1], [entry2, comboboxtext2], [entry3, comboboxtext3], [entry4, comboboxtext4]], coll_object.overlay_right_content)
                entry.connect("changed", update_button_search_and_reset, entry1, entry2, entry3, entry4, button_search, button_reset_search)
        
        box_search_coll_top_left = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box_search_coll_top_left.pack_start(button_search, False, False, 0)
        box_search_coll_top_left.pack_start(button_reset_search, False, False, 0)
        
        box_search_coll_top_right = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box_search_coll_top_right.pack_start(button_back_coll, False, False, 0)
        
        box_search_coll_top.pack_start(box_search_coll_top_left, False, False, 0)
        box_search_coll_top.pack_start(box_search_coll_top_right, False, False, 0)
        box_search_coll.pack_start(box_search_coll_top, False, False, 0)
        
        grid.attach(comboboxtext1, 1, 1, 1, 1)
        grid.attach_next_to(entry1, comboboxtext1, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(comboboxtext2, entry1, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(entry2, comboboxtext2, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(comboboxtext3, comboboxtext1, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(entry3, comboboxtext3, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(comboboxtext4, entry3, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(entry4, comboboxtext4, Gtk.PositionType.RIGHT, 1, 1)
        
        box_search_coll.pack_start(grid, False, False, 0)
        box_search_coll.show_all()
        
        return(box_search_coll)

def connect_db():
        '''Return the connection to the collection'DB and the cursor'''
        conn = sqlite3.connect(os.path.join(defs.HOMEMC, "collection.sqlite"))
        conn.create_function('py_lara', 1, functions.various.py_lara)
        conn.create_function('py_int', 1, functions.various.py_int)
        conn.create_function('py_lower', 1, functions.various.py_lower)
        conn.create_function('py_remove_hyphen', 1, functions.various.py_remove_hyphen)
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
             id_coll INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
             id_card TEXT,
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
             id_deck INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
             name TEXT,
             comment TEXT,
             proxies TEXT
        )
        """)
        
        disconnect_db(conn)
