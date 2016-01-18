#!/usr/bin/python
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

# Some functions for dealing with the decks

from gi.repository import Gtk, Gio, Pango, GdkPixbuf, GLib
import threading

# import global values
import defs

import functions.collection
import functions.db

def gen_decks_display(deck_object, box):
        for widget in box.get_children():
                box.remove(widget)
        
        conn, c = functions.collection.connect_db()
        c.execute("""SELECT * FROM decks""")
        reponses_decks = c.fetchall()
        functions.collection.disconnect_db(conn)
        nb_decks = len(reponses_decks)
        if nb_decks < 1 :
                tmp_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                label_welcome = Gtk.Label()
                label_welcome.set_markup("<big>" + defs.STRINGS["decks_empty_welcome"] + "</big>")
                label_welcome.set_line_wrap(True)
                label_welcome.set_lines(2)
                label_welcome.set_ellipsize(Pango.EllipsizeMode.END)
                label_welcome.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                label_welcome.set_justify(Gtk.Justification.CENTER)
                tmp_box.pack_start(label_welcome, False, False, 0)
                tmp_box.set_halign(Gtk.Align.CENTER)
                
                button_new_deck = Gtk.MenuButton()
                button_new_deck.set_relief(Gtk.ReliefStyle.NONE)
                button_new_deck.set_vexpand(True)
                button_new_deck.set_margin_left(100)
                button_new_deck.set_margin_right(100)
                button_new_deck.set_can_focus(False)
                button_new_deck.add(tmp_box)
                button_new_deck.set_popover(gen_new_deck_popover(button_new_deck, deck_object))
                box.pack_start(button_new_deck, False, False, 0)
        else:
                # the details button
                deck_object.button_show_details = Gtk.MenuButton()
                image_button_show_details = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="text-editor-symbolic"), Gtk.IconSize.BUTTON)
                image_button_show_details.show()
                deck_object.button_show_details.add(image_button_show_details)
                deck_object.button_show_details.set_sensitive(False)
                
                ###### the content of right_content_top ######
                right_content_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                box.pack_start(right_content_top, False, True, 0)
                
                # we create the scrolledwindow which will display the decks
                scrolledwindow_decks = Gtk.ScrolledWindow()
                scrolledwindow_decks.set_min_content_width(150)
                scrolledwindow_decks.set_min_content_height(150)
                scrolledwindow_decks.set_hexpand(True)
                scrolledwindow_decks.set_shadow_type(Gtk.ShadowType.IN)
                
                # id_deck, name
                deck_object.store_list_decks = Gtk.ListStore(str, str)
                
                tree_decks = Gtk.TreeView(deck_object.store_list_decks)
                tree_decks.set_enable_search(False)
                renderer_decks = Gtk.CellRendererText()
                column_name_decks = Gtk.TreeViewColumn(defs.STRINGS["list_decks_nb"], renderer_decks, text=1)
                
                deck_object.label_nb_decks = Gtk.Label(defs.STRINGS["list_decks_nb"])
                deck_object.label_nb_decks.show()
                
                column_name_decks.set_widget(deck_object.label_nb_decks)
                column_name_decks.set_sort_column_id(1)
                deck_object.store_list_decks.set_sort_column_id(1, Gtk.SortType.ASCENDING)
                tree_decks.append_column(column_name_decks)
                
                deck_object.select_list_decks = tree_decks.get_selection()
                deck_object.gen_list_decks()
                deck_object.select_list_decks.connect("changed", deck_object.display_deck_content, "blip", "blop", tree_decks)
                
                scrolledwindow_decks.add(tree_decks)
                right_content_top.pack_start(scrolledwindow_decks, False, True, 0)
                
                # the buttons for managing decks
                button_new_deck = Gtk.MenuButton(defs.STRINGS["create_new_deck"])
                button_new_deck.set_popover(gen_new_deck_popover(button_new_deck, deck_object))
                
                button_estimate_deck = Gtk.Button(defs.STRINGS["estimate_deck"])
                button_estimate_deck.set_sensitive(False)
                
                button_delete_deck = Gtk.Button(defs.STRINGS["delete_deck"])
                button_delete_deck.set_sensitive(False)
                
                box_buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
                box_buttons.set_valign(Gtk.Align.CENTER)
                for button in [button_new_deck, button_estimate_deck, button_delete_deck]:
                        box_buttons.pack_start(button, False, True, 0)
                right_content_top.pack_start(box_buttons, False, True, 0)
                
                label_comm = Gtk.Label(defs.STRINGS["comment_deck"])
                scrolledwindow_comm = Gtk.ScrolledWindow()
                scrolledwindow_comm.set_hexpand(True)
                scrolledwindow_comm.set_min_content_height(150)
                scrolledwindow_comm.set_shadow_type(Gtk.ShadowType.IN)
                textview_comm = Gtk.TextView()
                textview_comm.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
                textview_comm.set_sensitive(False)
                scrolledwindow_comm.add(textview_comm)
                
                box_comm = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                box_comm.pack_start(label_comm, False, True, 0)
                box_comm.pack_start(scrolledwindow_comm, False, True, 0)
                right_content_top.pack_start(box_comm, False, True, 0)
                
                ###### the content of right_content_mid ######
                deck_object.label_nb_cards = Gtk.Label()
                box.pack_start(deck_object.label_nb_cards, False, True, 0)
                
                ###### the content of self.right_content_bot ######
                label_click_deck = Gtk.Label()
                label_click_deck.set_markup("<big>" + defs.STRINGS["decks_click_deck"] + "</big>")
                label_click_deck.set_line_wrap(True)
                label_click_deck.set_lines(2)
                label_click_deck.set_ellipsize(Pango.EllipsizeMode.END)
                label_click_deck.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                label_click_deck.set_justify(Gtk.Justification.CENTER)
                deck_object.right_content_bot.pack_start(label_click_deck, True, True, 0)
                
                deck_object.update_nb_decks()
                deck_object.mainbox.show_all()

def prepare_delete_from_deck(button, deck_name, selection, decks_object):
        model, pathlist = selection.get_selected_rows()
        ids_db_list_to_delete = []
        ids_db_dict_proxies_to_delete = {}
        for row in pathlist:
                if model[row][16] == 0:
                        ids_db_list_to_delete.append(model[row][0])
                elif model[row][16] == 1:
                        ids_db_dict_proxies_to_delete[model[row][0]] = model[row][15] * -1
        if ids_db_list_to_delete != []:
                GLib.idle_add(decks_object.move_row, deck_name, "", ids_db_list_to_delete)
        if ids_db_dict_proxies_to_delete != {}:
                GLib.idle_add(decks_object.change_nb_proxies, deck_name, ids_db_dict_proxies_to_delete)

def gen_deck_content(deck_name, box, decks_object):
        '''Displays the cards of the deck.'''
        for widget in box.get_children():
                box.remove(widget)
        
        conn, c = functions.collection.connect_db()
        c.execute("""SELECT id_coll, id_card FROM collection WHERE deck = ?""", (deck_name,))
        responses = c.fetchall()
        c.execute("""SELECT proxies FROM decks WHERE name = ?""", (deck_name,))
        responses_proxies = c.fetchone()
        functions.collection.disconnect_db(conn)
        nb_cards = len(responses)
        
        # we create the toolbar
        toolbar_box = Gtk.ButtonBox(Gtk.Orientation.HORIZONTAL)
        toolbar_box.set_layout(Gtk.ButtonBoxStyle.START)
        toolbar_box.set_spacing(4)
        # the buttons
        decks_object.button_show_details = Gtk.MenuButton()
        decks_object.button_show_details.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="text-editor-symbolic"), Gtk.IconSize.BUTTON))
        decks_object.delete_button = Gtk.Button()
        decks_object.delete_button.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="deck_delete-symbolic"), Gtk.IconSize.BUTTON))
        decks_object.button_change_quantity = Gtk.MenuButton()
        decks_object.button_change_quantity.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="zoom-in-symbolic"), Gtk.IconSize.BUTTON))
        decks_object.button_move = Gtk.MenuButton()
        decks_object.button_move.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="send-to-symbolic"), Gtk.IconSize.BUTTON))
        
        for button in [decks_object.button_show_details, decks_object.delete_button, decks_object.button_change_quantity, decks_object.button_move]:
                button.set_sensitive(False)
                toolbar_box.add(button)
        toolbar_box.show_all()
        box.pack_end(toolbar_box, False, True, 0)  
        
        # the real cards in the deck
        dict_cards_in_deck = {}
        for card_deck in responses: 
                id_card = card_deck[1]
                bold = 400
                italic = Pango.Style.NORMAL
                try:
                        nb_card = dict_cards_in_deck[id_card][0]
                except KeyError:
                        dict_cards_in_deck[id_card] = [1, bold, italic]
                else:
                        dict_cards_in_deck[id_card][0] = nb_card + 1
        
        # the proxies
        dict_proxies_in_deck = {}
        if responses_proxies[0] != "":
                nb_proxies = 0
                for card_proxy in responses_proxies[0].split(";;;"):
                        id_card, nb_card = card_proxy.split("ø")
                        bold = 400
                        italic = Pango.Style.ITALIC
                        dict_proxies_in_deck[id_card] = [int(nb_card), bold, italic]
                        nb_proxies = nb_proxies + int(nb_card)
                nb_cards = nb_cards + nb_proxies
        
        complete_list_of_ids = []
        for id_ in dict_cards_in_deck.keys():
                if id_ not in complete_list_of_ids:
                        complete_list_of_ids.append(id_)
        if len(responses_proxies) > 0:
                for id_ in dict_proxies_in_deck.keys():
                        if id_ not in complete_list_of_ids:
                                complete_list_of_ids.append(id_)
        
        if nb_cards < 2:
                decks_object.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck"].replace("%%%", str(nb_cards)))
        else:
                decks_object.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck_s"].replace("%%%", str(nb_cards)))
        
        conn, c = functions.db.connect_db()
        tmp_req = ""
        for tmp in complete_list_of_ids:
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
        
        # "id", "name", "edition", "name_foreign", "colors", colors_pixbuf, "cmc", "type", "artist", "power", "toughness", "rarity", "bold", "italic", "nb_variant", "nb", "proxy"
        decks_object.mainstore = Gtk.ListStore(str, str, str, str, str, GdkPixbuf.Pixbuf, int, str, str, str, str, str, int, Pango.Style, str, int, int)
        tree_coll = Gtk.TreeView(decks_object.mainstore)
        decks_object.tree_coll = tree_coll
        tree_coll.set_enable_search(False)
        # some work with columns
        columns_to_display = functions.config.read_config("decks_columns").split(";")
        coll_columns_list = functions.various.gen_treeview_columns(columns_to_display, tree_coll)[0]
        decks_object.mainstore.set_sort_func(9, functions.various.compare_str_and_int, None)
        decks_object.mainstore.set_sort_func(10, functions.various.compare_str_and_int, None)
        
        select = tree_coll.get_selection()
        select.set_mode(Gtk.SelectionMode.MULTIPLE)
        select.connect("changed", decks_object.send_id_to_loader, "blip", "blop", 0)
        decks_object.mainselect = select
        scrolledwindow.add(tree_coll)
        
        tree_coll.connect("row-activated", decks_object.show_details, select, decks_object.button_show_details, decks_object.button_change_quantity)
        decks_object.delete_button.connect("clicked", prepare_delete_from_deck, deck_name, select, decks_object)
        
        tree_coll.show_all()
        scrolledwindow.show_all()
        
        box.pack_start(scrolledwindow, True, True, 0)
        
        cards = functions.various.prepare_cards_data_for_treeview(reponses_db)
        
        for id_, card in cards.items():
                if id_ in dict_cards_in_deck.keys():
                        nb_card = dict_cards_in_deck[id_][0]
                        bold_card = dict_cards_in_deck[id_][1]
                        italic_card = dict_cards_in_deck[id_][2]
                        
                        decks_object.mainstore.insert_with_valuesv(-1, range(17), [card["id_"], card["name"], card["edition_ln"], card["nameforeign"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold_card, italic_card, card["nb_variant"], nb_card, 0])
        
                if id_ in dict_proxies_in_deck.keys():
                        nb_card = dict_proxies_in_deck[id_][0]
                        bold_card = dict_proxies_in_deck[id_][1]
                        italic_card = dict_proxies_in_deck[id_][2]
                        
                        decks_object.mainstore.insert_with_valuesv(-1, range(17), [card["id_"], "-- " + card["name"], card["edition_ln"], "-- " + card["nameforeign"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold_card, italic_card, card["nb_variant"], nb_card, 1])
        
        decks_object.mainstore.set_sort_column_id(7, Gtk.SortType.ASCENDING)
        decks_object.mainstore.set_sort_column_id(2, Gtk.SortType.ASCENDING)
        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                decks_object.mainstore.set_sort_column_id(3, Gtk.SortType.ASCENDING)
        else:
                decks_object.mainstore.set_sort_column_id(1, Gtk.SortType.ASCENDING)

def prepare_move_cards(select_list_decks, selection, old_deck, decks_object):
        model_deck, pathlist_deck = select_list_decks.get_selected_rows()
        new_deck = model_deck[pathlist_deck][1]
        model, pathlist = selection.get_selected_rows()
        ids_db_list = []
        for row in pathlist:
                ids_db_list.append(model[row][0])
        GLib.idle_add(decks_object.move_row, old_deck, new_deck, ids_db_list)

def prepare_add_cards_deck(current_deck_name, ids_coll_dict, decks_object):
        GLib.idle_add(decks_object.add_cards_to_deck, current_deck_name, ids_coll_dict)

def prepare_delete_cards_deck(current_deck_name, ids_coll_dict, decks_object):
        GLib.idle_add(decks_object.delete_cards_from_deck, current_deck_name, ids_coll_dict)

def gen_deck_change_quantity_popover(button_change_quantity, selection, decks_object):
        '''Generate the popover which allow to change the quantity of the card selected in the deck selected.'''
        def spinbutton_value_changed(spinbutton, button_ok, current_quantity):
                value = spinbutton.get_value_as_int()
                if value != current_quantity and defs.COLL_LOCK == False:
                        button_ok.set_sensitive(True)
                else:
                        button_ok.set_sensitive(False)
        
        def button_ok_clicked(button_ok, spinbutton, id_db, ids_cards_free_list, ids_cards_in_current_deck_list, current_quantity, popover, selection, current_deck_name, decks_object):
                new_value = spinbutton.get_value_as_int()
                if new_value > current_quantity:
                        # we add cards
                        nb_cards_to_add = new_value - current_quantity
                        
                        ids_coll_dict = {}
                        nb_added = 0
                        for card_id_coll in reversed(ids_cards_free_list):
                                ids_coll_dict[card_id_coll] = id_db
                                nb_added += 1
                                if nb_added == nb_cards_to_add:
                                        break
                        
                        thread = threading.Thread(target = prepare_add_cards_deck, args = (current_deck_name, ids_coll_dict, decks_object))
                        thread.daemon = True
                        thread.start()
                elif new_value < current_quantity:
                        # we delete cards
                        nb_cards_to_delete = current_quantity - new_value
                        
                        ids_coll_dict = {}
                        nb_added = 0
                        for card_id_coll in reversed(ids_cards_in_current_deck_list):
                                ids_coll_dict[card_id_coll] = id_db
                                nb_added += 1
                                if nb_added == nb_cards_to_delete:
                                        break
                        thread = threading.Thread(target = prepare_delete_cards_deck, args = (current_deck_name, ids_coll_dict, decks_object))
                        thread.daemon = True
                        thread.start()
                        
                popover.hide()
        
        def button_ok_clicked_proxies(button, spinbutton, id_db, current_quantity, current_deck_name, popover, decks_object):
                new_quantity = spinbutton.get_value_as_int()
                diff = new_quantity - current_quantity
                proxies_dict_to_change = {id_db: diff}
                GLib.idle_add(decks_object.change_nb_proxies, current_deck_name, proxies_dict_to_change)
                popover.hide()
        
        def popover_show(popover, button_change_quantity, selection, quantity_box, decks_object):
                for widget in quantity_box.get_children():
                        quantity_box.remove(widget)
                
                model_deck, pathlist_deck = decks_object.select_list_decks.get_selected_rows()
                current_deck_name = model_deck[pathlist_deck][1]
                
                model, pathlist = decks_object.mainselect.get_selected_rows()
                for row in pathlist:
                        id_db = model[row][0]
                        proxy = model[row][16]
                        current_quantity = model[row][15]
                        break
                
                if proxy == 0:
                        details_store = functions.collection.gen_details_store(selection)
                        ids_cards_free_list = []
                        ids_cards_in_current_deck_list = []
                        cards_in_deck = 0
                        max_cards = len(details_store)
                        for card in details_store:
                                if card[10] == "":
                                        ids_cards_free_list.append(card[0])
                                else:
                                        cards_in_deck += 1
                                if card[10] == current_deck_name:
                                        ids_cards_in_current_deck_list.append(card[0])
                        
                        cards_disp = max_cards - cards_in_deck + current_quantity
                        
                        adjustment = Gtk.Adjustment(value=current_quantity, lower=1, upper=cards_disp, step_increment=1, page_increment=10, page_size=0)
                else:
                        adjustment = Gtk.Adjustment(value=current_quantity, lower=1, upper=100, step_increment=1, page_increment=10, page_size=0)
                label_change_quantity = Gtk.Label(defs.STRINGS["change_quantity"])
                quantity_box.pack_start(label_change_quantity, True, True, 0)
                spinbutton = Gtk.SpinButton(adjustment=adjustment)
                quantity_box.pack_start(spinbutton, True, True, 0)
                
                button_ok = Gtk.Button(defs.STRINGS["change_quantity_validate"])
                button_ok.set_sensitive(False)
                quantity_box.pack_start(button_ok, True, True, 0)
                
                spinbutton.connect("value-changed", spinbutton_value_changed, button_ok, current_quantity)
                if proxy == 0:
                        button_ok.connect("clicked", button_ok_clicked, spinbutton, id_db, ids_cards_free_list, ids_cards_in_current_deck_list, current_quantity, popover, selection, current_deck_name, decks_object)
                else:
                        button_ok.connect("clicked", button_ok_clicked_proxies, spinbutton, id_db, current_quantity, current_deck_name, popover, decks_object)
                
                quantity_box.show_all()
        
        quantity_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        quantity_box.set_margin_top(5)
        quantity_box.set_margin_bottom(5)
        quantity_box.set_margin_left(5)
        quantity_box.set_margin_right(5)
        popover = Gtk.Popover.new(button_change_quantity)
        popover.connect("show", popover_show, button_change_quantity, selection, quantity_box, decks_object)
        popover.add(quantity_box)
        return(popover)

def gen_move_deck_popover(button_move, selection, decks_object):
        '''Create the popover which allow the user to move all the cards selected to one deck to another.'''
        def select_changed(selection, ok_button):
                model, treeiter = selection.get_selected()
                if treeiter == None:
                        ok_button.set_sensitive(False)
                else:
                        ok_button.set_sensitive(True)
        
        def popover_show(popover, decks_object, move_deck_box, selection):
                for widget in move_deck_box.get_children():
                        move_deck_box.remove(widget)
                
                model, pathlist = decks_object.select_list_decks.get_selected_rows()
                current_deck_name = model[pathlist][1]
                
                scrolledwindow_decks = Gtk.ScrolledWindow()
                scrolledwindow_decks.set_min_content_width(150)
                scrolledwindow_decks.set_min_content_height(150)
                scrolledwindow_decks.set_hexpand(True)
                scrolledwindow_decks.set_shadow_type(Gtk.ShadowType.IN)
                
                # id_deck, name
                store_list_decks = Gtk.ListStore(str, str)
                
                tree_decks = Gtk.TreeView(store_list_decks)
                tree_decks.set_enable_search(False)
                renderer_decks = Gtk.CellRendererText()
                column_name_decks = Gtk.TreeViewColumn(defs.STRINGS["list_decks_nb"].replace("(%%%)", ""), renderer_decks, text=1)
                
                column_name_decks.set_sort_column_id(1)
                store_list_decks.set_sort_column_id(1, Gtk.SortType.ASCENDING)
                tree_decks.append_column(column_name_decks)
                
                select_list_decks = tree_decks.get_selection()
                ok_button = Gtk.Button(defs.STRINGS["create_new_deck_ok"])
                select_list_decks.connect("changed", select_changed, ok_button)
                
                conn_coll, c_coll = functions.collection.connect_db()
                c_coll.execute("""SELECT id_deck, name FROM decks""")
                responses = c_coll.fetchall()
                functions.collection.disconnect_db(conn_coll)
                
                for id_deck, name in responses:
                        if name != current_deck_name:
                                store_list_decks.append([str(id_deck), name])
                
                scrolledwindow_decks.add(tree_decks)
                
                ok_button.set_sensitive(False)
                ok_button.connect("clicked", move_cards, popover, select_list_decks, selection, current_deck_name, decks_object)
                
                move_label = Gtk.Label(defs.STRINGS["move_to_other_deck"])
                
                move_deck_box.pack_start(move_label, True, True, 0)
                move_deck_box.pack_start(scrolledwindow_decks, True, True, 0)
                move_deck_box.pack_start(ok_button, True, True, 0)
                move_deck_box.show_all()
        
        def move_cards(button, popover, select_list_decks, selection, old_deck, decks_object):
                thread = threading.Thread(target = prepare_move_cards, args = (select_list_decks, selection, old_deck, decks_object))
                thread.daemon = True
                thread.start()
                popover.hide()
        
        move_deck_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        move_deck_box.set_margin_top(5)
        move_deck_box.set_margin_bottom(5)
        move_deck_box.set_margin_left(5)
        move_deck_box.set_margin_right(5)
        popover = Gtk.Popover.new(button_move)
        popover.props.width_request = 300
        popover.connect("show", popover_show, decks_object, move_deck_box, selection)
        popover.add(move_deck_box)
        return(popover)

def gen_new_deck_popover(button_new_deck, deck_object):
        '''Create the popover which create deck.'''
        def create_deck(button, entry_name_deck, deck_object, popover):
                popover.hide()
                deck_object.create_new_deck(entry_name_deck.get_text())
        
        def popover_show(popover, deck_object, new_deck_box):
                for widget in new_deck_box.get_children():
                        new_deck_box.remove(widget)
                label_name_deck = Gtk.Label(defs.STRINGS["create_new_deck_name"])
                entry_name_deck = Gtk.Entry()
                ok_button = Gtk.Button(defs.STRINGS["create_new_deck_ok"])
                ok_button.connect("clicked", create_deck, entry_name_deck, deck_object, popover)
                if defs.COLL_LOCK:
                        ok_button.set_sensitive(False)
                else:
                        ok_button.set_sensitive(True)
                for widget in [label_name_deck, entry_name_deck, ok_button]:
                        new_deck_box.pack_start(widget, True, True, 0)
                new_deck_box.show_all()
                entry_name_deck.grab_focus()
        
        new_deck_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        new_deck_box.set_margin_top(5)
        new_deck_box.set_margin_bottom(5)
        new_deck_box.set_margin_left(5)
        new_deck_box.set_margin_right(5)
        popover = Gtk.Popover.new(button_new_deck)
        popover.props.width_request = 300
        popover.connect("show", popover_show, deck_object, new_deck_box)
        popover.add(new_deck_box)
        return(popover)
