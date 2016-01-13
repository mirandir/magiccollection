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
import threading
import time

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
                coll_object.button_show_details = Gtk.MenuButton()
                coll_object.button_show_details.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="text-editor-symbolic"), Gtk.IconSize.BUTTON))
                coll_object.button_change_quantity = Gtk.Button()
                coll_object.button_change_quantity.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="zoom-in-symbolic"), Gtk.IconSize.BUTTON))
                coll_object.button_add_deck = Gtk.Button()
                coll_object.button_add_deck.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="deck_add-symbolic"), Gtk.IconSize.BUTTON))
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
                coll_object.mainstore = Gtk.ListStore(str, str, str, str, str, GdkPixbuf.Pixbuf, int, str, str, str, str, str, int, Pango.Style, str, int)
                tree_coll = Gtk.TreeView(coll_object.mainstore)
                coll_object.tree_coll = tree_coll
                tree_coll.set_enable_search(False)
                # some work with columns
                columns_to_display = functions.config.read_config("coll_columns").split(";")
                coll_columns_list = functions.various.gen_treeview_columns(columns_to_display, tree_coll)[0]
                coll_object.mainstore.set_sort_func(9, functions.various.compare_str_and_int, None)
                coll_object.mainstore.set_sort_func(10, functions.various.compare_str_and_int, None)
                
                select = tree_coll.get_selection()
                coll_object.select = select
                select.set_mode(Gtk.SelectionMode.MULTIPLE)
                select.connect("changed", coll_object.send_id_to_loader_with_selectinfo, "blip", "blop", 0, selectinfo_button, coll_object.button_show_details)
                selectinfo_button.connect("clicked", coll_object.selectinfo_click, select, popover_selectinfo)
                coll_object.mainselect = select
                scrolledwindow.add(tree_coll)
                
                tree_coll.connect("row-activated", coll_object.show_details, select, coll_object.button_show_details)
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

def prepare_update_details(selection, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, details_store, copy_details):
        '''If copy_details is 1, we copy-paste all details of the current card on all cards in the store.'''
        def real_prepare_update_details(selection, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, details_store):
                # we get details
                condition = ""
                for cond in defs.CONDITIONS.values():
                        if cond[1] == comboboxtext_condition.get_active_text():
                                condition = cond[0]
                                break
                lang = entry_lang.get_text()
                foil = ""
                if checkbutton_foil.get_active():
                        foil = "1"
                loaned = ""
                if checkbutton_loaned.get_active():
                        loaned = entry_loaned.get_text()
                textbuffer = textview_comment.get_buffer()
                start = textbuffer.get_start_iter()
                end = textbuffer.get_end_iter()
                comment = textbuffer.get_text(start, end, False)
                
                model, pathlist = selection.get_selected_rows()
                if copy_details == 1:
                        current_id = int(model[pathlist][0])
                        selection.select_all()
                        model, pathlist = selection.get_selected_rows()
                
                cards_to_update = {}
                for row in pathlist:
                        #id_coll, name, editionln, nameforeign, date, condition, lang, foil, loaned_to, comment, deck, bold, italic, id_db
                        id_coll = model[row][0]
                        try:
                                cards_to_update[id_coll]
                        except KeyError:
                                cards_to_update[id_coll] = [condition, lang, foil, loaned, comment]
                        else:
                                raise KeyError("Problem : id " + str(id_coll) + " has more than 1 occurrence in the Treeview !")
                
                new_id_db_to_bold = []
                new_id_db_to_unbold = []
                # we update the treeview according to the new informations
                for row in pathlist:
                        for id_coll, new_data in cards_to_update.items():
                                if model[row][0] == id_coll:
                                        condition, lang, foil, loaned, comment = new_data
                                        model[row][5] = condition
                                        model[row][6] = lang
                                        model[row][7] = foil
                                        model[row][8] = loaned
                                        model[row][9] = comment
                                        if comment != "":
                                                model[row][11] = 700
                                                new_id_db_to_bold.append(str(model[row][13]))
                                        else:
                                                model[row][11] = 400
                                                # any need of unbolding the row in the collection ?
                                                nb_with_comment = 0
                                                for card in details_store:
                                                        tmp_id_db = card[13]
                                                        if tmp_id_db == model[row][13]:
                                                                if card[11] == 700:
                                                                        nb_with_comment += 1
                                                if nb_with_comment == 0:
                                                        new_id_db_to_unbold.append(str(model[row][13]))
                
                defs.MAINWINDOW.collection.update_details(cards_to_update, new_id_db_to_bold, new_id_db_to_unbold)
                
                if copy_details == 1:
                        for row in pathlist:
                                if int(model[row][0]) == current_id:
                                        selection.unselect_all()
                                        selection.select_path(row)
                                        break
        
        if defs.CURRENT_SAVEDETAILS_THREAD == None:
                # we are the first thread, we need to note this
                defs.CURRENT_SAVEDETAILS_THREAD = 1
        else:
                defs.CURRENT_SAVEDETAILS_THREAD += 1
        my_number = int(defs.CURRENT_SAVEDETAILS_THREAD)
        defs.SAVEDETAILS_TIMER = 250 # 250 ms
        
        # now, we wait until the end of the timer (or until another thread take our turn)
        go = 1
        while defs.SAVEDETAILS_TIMER > 0:
                if my_number != defs.CURRENT_SAVEDETAILS_THREAD:
                        # too bad, we have to stop now
                        go = 0
                        break
                else:
                        time.sleep(1 / 1000)
                        defs.SAVEDETAILS_TIMER -= 1
        
        if go == 1:
                defs.CURRENT_SAVEDETAILS_THREAD = None
                GLib.idle_add(real_prepare_update_details, selection, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, details_store)

def prepare_delete_card(cards_to_delete):
        GLib.idle_add(defs.MAINWINDOW.collection.del_collection, cards_to_delete)

def gen_details_popover(button_show_details, selection):
        '''Displays details for the current selection of cards.'''
        
        def select_changed(selection, integer, TreeViewColumn, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, scrolledwindow_comment, textview_comment, button_add_deck, button_copy_details, button_delete_deck, button_remove):
                model, pathlist = selection.get_selected_rows()
                if len(pathlist) > 0:
                        for widget in [comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, button_add_deck, button_copy_details, button_delete_deck, button_remove]:
                                widget.set_sensitive(False)
                        
                        if len(pathlist) == 1:
                                button_copy_details.set_sensitive(True)
                                
                                id_coll, name, editionln, nameforeign, date, condition, lang, foil, loaned_to, comment, deck, bold, italic, id_db = model[pathlist]
                                
                                if condition == "mint":
                                        comboboxtext_condition.set_active(0)
                                elif condition == "near_mint":
                                        comboboxtext_condition.set_active(1)
                                elif condition == "excellent":
                                        comboboxtext_condition.set_active(2)
                                elif condition == "played":
                                        comboboxtext_condition.set_active(3)
                                elif condition == "poor":
                                        comboboxtext_condition.set_active(4)
                                else:
                                        comboboxtext_condition.set_active(-1)
                                
                                if lang != "":
                                        entry_lang.set_text(lang)
                                else:
                                        entry_lang.set_text("")
                                
                                if foil == "1":
                                        checkbutton_foil.set_active(True)
                                else:
                                        checkbutton_foil.set_active(False)
                                
                                if loaned_to != "":
                                        entry_loaned.set_text(loaned_to)
                                        checkbutton_loaned.set_active(True)
                                else:
                                        checkbutton_loaned.set_active(False)
                                        entry_loaned.set_text("")
                                
                                if comment != "":
                                        textview_comment.get_buffer().set_text(comment, -1)
                                else:
                                        textview_comment.get_buffer().set_text("", -1)
                        else:
                                button_copy_details.set_sensitive(False)
                                comboboxtext_condition.set_active(-1)
                                entry_lang.set_text("")
                                checkbutton_foil.set_active(False)
                                entry_loaned.set_text("")
                                checkbutton_loaned.set_active(False)
                                textview_comment.get_buffer().set_text("", -1)
                        
                        if defs.COLL_LOCK == False:
                                nb_cards_in_deck = 0
                                for row in pathlist:
                                        if model[row][10] != "":
                                                nb_cards_in_deck += 1
                                
                                if nb_cards_in_deck == 0:
                                        button_add_deck.set_sensitive(True)
                                        button_remove.set_sensitive(True)
                                else:
                                        button_add_deck.set_sensitive(False)
                                        button_remove.set_sensitive(False)
                                if nb_cards_in_deck == len(pathlist):
                                        button_delete_deck.set_sensitive(True)
                                else:
                                        button_delete_deck.set_sensitive(False)
                                
                                for widget in [comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, textview_comment]:
                                        widget.set_sensitive(True)
                                if checkbutton_loaned.get_active():
                                        entry_loaned.set_sensitive(True)
                        else:
                                for widget in [entry_loaned, button_add_deck, button_copy_details, button_delete_deck, button_remove]:
                                        widget.set_sensitive(False)
                else:
                        for widget in [comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, button_add_deck, button_copy_details, button_delete_deck, button_remove]:
                                widget.set_sensitive(False)
                        comboboxtext_condition.set_active(-1)
                        entry_lang.set_text("")
                        checkbutton_foil.set_active(False)
                        entry_loaned.set_text("")
                        checkbutton_loaned.set_active(False)
                        textview_comment.get_buffer().set_text("", -1)
        
        def copy_details(widget, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, selection, details_store):
                if widget.get_sensitive():
                        thread = threading.Thread(target = prepare_update_details, args = (selection, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, details_store, 1))
                        thread.daemon = True
                        thread.start()
        
        def delete_card(button, selection, details_store):
                model, pathlist = selection.get_selected_rows()
                cards_to_delete = {}
                rows_to_delete = []
                for row in pathlist:
                        #id_coll, name, editionln, nameforeign, date, condition, lang, foil, loaned_to, comment, deck, bold, italic, id_db
                        cards_to_delete[model[row][0]] = model[row][13]
                        rows_to_delete.append(row)
                
                if len(cards_to_delete) > 0:
                        for row in reversed(rows_to_delete):
                                del(model[row])
                        
                        thread = threading.Thread(target = prepare_delete_card, args = ([cards_to_delete]))
                        thread.daemon = True
                        thread.start()
        
        def widget_save_details(widget, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, selection, details_store):
                if widget.get_sensitive():
                        thread = threading.Thread(target = prepare_update_details, args = (selection, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, details_store, 0))
                        thread.daemon = True
                        thread.start()
        
        def entry_loaned_save_details(widget, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, selection, details_store):
                if widget.get_sensitive() and checkbutton_loaned.get_active() == True:
                        thread = threading.Thread(target = prepare_update_details, args = (selection, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, details_store, 0))
                        thread.daemon = True
                        thread.start()
        
        def checkbutton_loaned_save_details(widget, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, selection, details_store):
                if widget.get_active() == False and widget.get_sensitive() and entry_loaned.get_text() != "":
                        entry = Gtk.Entry()
                        entry.set_text("")
                        thread = threading.Thread(target = prepare_update_details, args = (selection, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry, textview_comment, details_store, 0))
                        thread.daemon = True
                        thread.start()
                if widget.get_active() == True and widget.get_sensitive() and entry_loaned.get_text() != "":
                        thread = threading.Thread(target = prepare_update_details, args = (selection, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, details_store, 0))
                        thread.daemon = True
                        thread.start()
        
        def textview_comment_save_details(widget, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, selection, details_store):
                if textview_comment.get_sensitive():
                        thread = threading.Thread(target = prepare_update_details, args = (selection, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, details_store, 0))
                        thread.daemon = True
                        thread.start()
        
        def popover_show(popover, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, scrolledwindow_comment):
                if defs.COLL_LOCK:
                        for widget in [comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment]:
                                widget.set_sensitive(False)
        
        details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        details_box.set_margin_top(5)
        details_box.set_margin_bottom(5)
        details_box.set_margin_left(5)
        details_box.set_margin_right(5)
        
        model, pathlist = selection.get_selected_rows()
        
        # first, we get the list of all cards' ids
        ids_list = ""
        for row in pathlist:
                ids_list = ids_list + "\"" + model[row][0] + "\", "
        ids_list = ids_list[:-2]
        # we get data in the collection for this list
        conn, c = connect_db()
        c.execute("""SELECT * FROM collection WHERE id_card IN (""" + ids_list + """)""")
        reponses_coll = c.fetchall()
        disconnect_db(conn)
        
        # we create a (cleaner) dict with reponses_coll
        dict_responses_coll = {}
        for card_coll in reponses_coll:
                id_coll, id_card, date, condition, lang, foil, loaned_to, comment, deck = card_coll
                try:
                        dict_responses_coll[id_card]
                except KeyError:
                        dict_responses_coll[id_card] = [[id_coll, date, condition, lang, foil, loaned_to, comment, deck]]
                else:
                        dict_responses_coll[id_card].append([id_coll, date, condition, lang, foil, loaned_to, comment, deck])
        
        if len(dict_responses_coll) > 0:
                # we create widgets for displaying the cards
                scrolledwindow = Gtk.ScrolledWindow()
                scrolledwindow.set_min_content_width(250)
                scrolledwindow.set_min_content_height(150)
                scrolledwindow.set_hexpand(True)
                scrolledwindow.set_vexpand(True)
                scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
                
                # we need : id_coll, name, editionln, nameforeign, date, condition, lang, foil, loaned_to, comment, deck, bold, italic, id_db
                details_store = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str, str, int, Pango.Style, str)
                details_tree = Gtk.TreeView(details_store)
                details_tree.set_enable_search(False)
                # columns
                if "name_foreign" in functions.config.read_config("coll_columns").split(";") and defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                        columns_to_display = ["id_coll", "name_foreign", "edition"]
                        coll_columns_dict, renderer_dict = functions.various.gen_treeview_columns(columns_to_display, details_tree)
                        renderer_dict["name_foreign"].set_fixed_size(90, 25)
                else:
                        columns_to_display = ["id_coll", "name", "edition"]
                        coll_columns_dict, renderer_dict = functions.various.gen_treeview_columns(columns_to_display, details_tree)
                        renderer_dict["name"].set_fixed_size(90, 25)
                renderer_dict["id_coll"].set_fixed_size(10, 25)
                renderer_dict["edition"].set_fixed_size(40, 25)
                
                grid_details, label_add_condition, comboboxtext_condition, label_add_lang, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, label_add_comment, scrolledwindow_comment, textview_comment = functions.various.gen_details_widgets()
                for widget in [comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment]:
                        widget.set_sensitive(False)
                
                # we create the toolbar and his buttons
                button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                
                button_add_deck = Gtk.Button()
                button_add_deck.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="deck_add-symbolic"), Gtk.IconSize.BUTTON))
                
                button_copy_details = Gtk.Button()
                button_copy_details.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="edit-copy-symbolic"), Gtk.IconSize.BUTTON))
                
                button_delete_deck = Gtk.Button()
                button_delete_deck.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="deck_delete-symbolic"), Gtk.IconSize.BUTTON))
                
                button_remove = Gtk.Button()
                button_remove.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="edit-delete-symbolic"), Gtk.IconSize.BUTTON))
                
                for button in [button_add_deck, button_copy_details, button_delete_deck, button_remove]:
                        button.set_sensitive(False)
                        button_box.pack_start(button, True, True, 0)
                
                select = details_tree.get_selection()
                select.set_mode(Gtk.SelectionMode.MULTIPLE)
                select.connect("changed", select_changed, "blip", "blop", comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, scrolledwindow_comment, textview_comment, button_add_deck, button_copy_details, button_delete_deck, button_remove)
                scrolledwindow.add(details_tree)
                
                button_copy_details.connect("clicked", copy_details, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, select, details_store)
                button_remove.connect("clicked", delete_card, select, details_store)
                
                # we connect the widgets to widget_save_details
                comboboxtext_condition.connect("changed", widget_save_details, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, select, details_store)
                entry_lang.connect("changed", widget_save_details, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, select, details_store)
                checkbutton_foil.connect("toggled", widget_save_details, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, select, details_store)
                # we need a specific one for some widgets
                checkbutton_loaned.connect("toggled", checkbutton_loaned_save_details, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, select, details_store)
                entry_loaned.connect("changed", entry_loaned_save_details, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, select, details_store)
                textview_comment.get_buffer().connect("changed", textview_comment_save_details, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment, select, details_store)
                
                for row in pathlist:
                        card_id = model[row][0]
                        card_name = model[row][1]
                        card_editionln = model[row][2]
                        card_nameforeign = model[row][3]
                        
                        # id_coll, name, editionln, nameforeign, date, condition, lang, foil, loaned_to, comment, deck, bold, italic, id_db
                        for card in dict_responses_coll[card_id]:
                                id_coll, date, condition, lang, foil, loaned_to, comment, deck = card
                                bold = 400
                                if comment != "":
                                        bold = 700
                                italic = Pango.Style.NORMAL
                                if deck != "":
                                        italic = Pango.Style.ITALIC
                                
                                details_store.insert_with_valuesv(-1, range(15), [str(id_coll), card_name, card_editionln, card_nameforeign, date, condition, lang, foil, loaned_to, comment, deck, bold, italic, card_id])
                        
                if "name_foreign" in functions.config.read_config("coll_columns").split(";") and defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                        details_store.set_sort_column_id(3, Gtk.SortType.ASCENDING)
                else:
                        details_store.set_sort_column_id(1, Gtk.SortType.ASCENDING)
                
                box1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
                details_box.pack_start(box1, True, True, 0)
                
                box1.pack_start(scrolledwindow, True, True, 0)
                
                box1.pack_start(button_box, False, True, 0)
                
                box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
                details_box.pack_start(box2, True, True, 0)
                
                box2.pack_start(grid_details, True, True, 0)
                
                details_box.show_all()
                popover = Gtk.Popover.new(button_show_details)
                popover.connect("show", popover_show, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview_comment)
                popover.add(details_box)
                popover.props.width_request = 550
                return(popover)
        else:
                return(None)

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
                coll_object.searchstore = Gtk.ListStore(str, str, str, str, str, GdkPixbuf.Pixbuf, int, str, str, str, str, str, int, Pango.Style, str, int)
                
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
                comboboxtext.set_wrap_width(2)
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
