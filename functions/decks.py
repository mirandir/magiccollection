#!/usr/bin/python
# -*-coding:Utf-8 -*
#

# Copyright 2013-2016 mirandir

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
import time

# import global values
import defs

import functions.collection
import functions.db

def gen_decks_display(decks_object, box):
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
                button_new_deck.set_vexpand(True)
                button_new_deck.set_margin_left(100)
                button_new_deck.set_margin_right(100)
                button_new_deck.set_can_focus(False)
                button_new_deck.add(tmp_box)
                button_new_deck.set_popover(gen_new_deck_popover(button_new_deck, decks_object))
                box.pack_start(button_new_deck, False, False, 0)
        else:
                # the details button
                decks_object.button_show_details = Gtk.MenuButton()
                image_button_show_details = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="text-editor-symbolic"), Gtk.IconSize.BUTTON)
                image_button_show_details.show()
                decks_object.button_show_details.add(image_button_show_details)
                decks_object.button_show_details.set_sensitive(False)
                
                ###### the content of right_content_top ######
                right_content_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
                box.pack_start(right_content_top, False, True, 0)
                
                right_content_top_left = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
                right_content_top.pack_start(right_content_top_left, False, True, 0)
                
                # we create the scrolledwindow which will display the decks
                scrolledwindow_decks = Gtk.ScrolledWindow()
                scrolledwindow_decks.set_min_content_width(100)
                scrolledwindow_decks.set_min_content_height(100)
                scrolledwindow_decks.set_hexpand(True)
                scrolledwindow_decks.set_shadow_type(Gtk.ShadowType.IN)
                
                # id_deck, name, comment
                decks_object.store_list_decks = Gtk.ListStore(str, str, str)
                
                tree_decks = Gtk.TreeView(decks_object.store_list_decks)
                decks_object.treeview_list_decks = tree_decks
                tree_decks.set_enable_search(False)
                
                renderer_decks = Gtk.CellRendererText()
                column_name_decks = Gtk.TreeViewColumn(defs.STRINGS["list_decks_nb"], renderer_decks, text=1)
                decks_object.label_nb_decks = Gtk.Label(defs.STRINGS["list_decks_nb"])
                decks_object.label_nb_decks.show()
                column_name_decks.set_widget(decks_object.label_nb_decks)
                column_name_decks.set_sort_column_id(1)
                decks_object.store_list_decks.set_sort_column_id(1, Gtk.SortType.ASCENDING)
                tree_decks.append_column(column_name_decks)
                
                renderer_comment = Gtk.CellRendererText()
                column_comment_decks = Gtk.TreeViewColumn(defs.STRINGS["comment_deck"], renderer_comment, text=2)
                column_comment_decks.set_sort_column_id(2)
                tree_decks.append_column(column_comment_decks)
                
                decks_object.store_list_decks.set_sort_func(1, functions.various.compare_str, None)
                decks_object.store_list_decks.set_sort_func(2, functions.various.compare_str, None)
                
                decks_object.select_list_decks = tree_decks.get_selection()
                decks_object.gen_list_decks(None)
                
                scrolledwindow_decks.add(tree_decks)
                right_content_top_left.pack_start(scrolledwindow_decks, False, True, 0)
                
                # we create the toolbar and his buttons for managing decks
                button_new_deck = Gtk.MenuButton()
                button_new_deck.set_popover(gen_new_deck_popover(button_new_deck, decks_object))
                button_new_deck.set_tooltip_text(defs.STRINGS["create_new_deck"])
                button_new_deck.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="document-new-symbolic"), Gtk.IconSize.BUTTON))
                
                decks_object.button_change_comm_deck = Gtk.MenuButton()
                decks_object.button_change_comm_deck.set_popover(gen_edit_comm_name_deck_popover(decks_object.button_change_comm_deck, decks_object, decks_object.select_list_decks))
                decks_object.button_change_comm_deck.set_tooltip_text(defs.STRINGS["edit_comment_name_deck"])
                decks_object.button_change_comm_deck.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="document-edit-symbolic"), Gtk.IconSize.BUTTON))
                decks_object.button_change_comm_deck.set_sensitive(False)
                
                decks_object.button_estimate_deck = Gtk.Button()
                decks_object.button_estimate_deck.set_sensitive(False)
                decks_object.button_estimate_deck.connect("clicked", prepare_estimate_deck, decks_object.select_list_decks)
                decks_object.button_estimate_deck.set_tooltip_text(defs.STRINGS["estimate_deck"])
                decks_object.button_estimate_deck.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="accessories-calculator-symbolic"), Gtk.IconSize.BUTTON))
                
                button_delete_deck = Gtk.Button()
                button_delete_deck.set_sensitive(False)
                button_delete_deck.connect("clicked", prepare_delete_deck, decks_object.select_list_decks, decks_object)
                button_delete_deck.set_tooltip_text(defs.STRINGS["delete_deck"])
                button_delete_deck.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="user-trash-symbolic"), Gtk.IconSize.BUTTON))
                
                box_buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                for button in [button_new_deck, decks_object.button_change_comm_deck, decks_object.button_estimate_deck, button_delete_deck]:
                        box_buttons.pack_start(button, False, True, 0)
                right_content_top_left.pack_start(box_buttons, False, True, 0)
                                
                decks_object.select_list_decks.connect("changed", decks_object.display_deck_content, "blip", "blop", tree_decks, button_delete_deck)
                
                tree_decks.connect("row-activated", show_change_name_comment_deck, decks_object.button_change_comm_deck)
                
                ###### the content of right_content_mid ######
                decks_object.label_nb_cards = Gtk.Label()
                box.pack_start(decks_object.label_nb_cards, False, True, 0)
                
                ###### the content of self.right_content_bot ######
                label_click_deck = Gtk.Label()
                label_click_deck.set_markup("<big>" + defs.STRINGS["decks_click_deck"] + "</big>")
                label_click_deck.set_line_wrap(True)
                label_click_deck.set_lines(2)
                label_click_deck.set_ellipsize(Pango.EllipsizeMode.END)
                label_click_deck.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                label_click_deck.set_justify(Gtk.Justification.CENTER)
                decks_object.right_content_bot.pack_start(label_click_deck, True, True, 0)
                decks_object.right_content.pack_start(decks_object.right_content_bot, True, True, 0)
                
                decks_object.update_nb_decks()
                decks_object.mainbox.show_all()

def show_change_name_comment_deck(treeview, treepath, column, button_change_comm_deck):
        button_change_comm_deck.emit("clicked")

def prepare_estimate_deck(button, select_list_decks):
        model_deck, pathlist_deck = select_list_decks.get_selected_rows()
        deck_name = model_deck[pathlist_deck][1]
        request = """SELECT DISTINCT id_card FROM collection WHERE deck = \"""" + deck_name + """\" OR deck_side = \"""" + deck_name + """\""""
        conn, c = functions.collection.connect_db()
        c.execute(request)
        responses_db = c.fetchall()
        functions.collection.disconnect_db(conn)
        ids_db_list = ""
        for id_card in responses_db:
                ids_db_list = ids_db_list + "\"" + id_card[0] + "\", "
        ids_db_list = ids_db_list[:-2]
        
        GLib.idle_add(functions.prices.show_estimate_dialog, "deck", ids_db_list, deck_name)

def prepare_delete_deck(button, select_list_decks, decks_object):
        def real_work(decks_object, deck_name):
                GLib.idle_add(decks_object.delete_deck, deck_name)
        model_deck, pathlist_deck = select_list_decks.get_selected_rows()
        deck_name = model_deck[pathlist_deck][1]
        dialog = Gtk.MessageDialog(defs.MAINWINDOW, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, defs.STRINGS["delete_deck_warning"].replace("%%%", deck_name))
        response = dialog.run()
        dialog.destroy()
        # -8 yes, -9 no
        if response == -8:        
                thread = threading.Thread(target = real_work, args = (decks_object, deck_name))
                thread.daemon = True
                thread.start()

def prepare_delete_from_deck(button, deck_name, selection, decks_object):
        model, pathlist = selection.get_selected_rows()
        ids_db_list_to_delete = []
        ids_db_list_proxies_to_delete = []
        for row in pathlist:
                if model[row][16] == 0:
                        ids_db_list_to_delete.append([model[row][0], model[row][17]])
                elif model[row][16] == 1:
                        ids_db_list_proxies_to_delete.append([model[row][0], model[row][15] * -1, model[row][17]])
        if len(ids_db_list_to_delete) > 0:
                GLib.idle_add(decks_object.move_row, deck_name, "", ids_db_list_to_delete)
        if len(ids_db_list_proxies_to_delete) > 0:
                GLib.idle_add(decks_object.change_nb_proxies, deck_name, ids_db_list_proxies_to_delete)

def prepare_deck_comment_save(textbuffer, decks_object):
        def real_prepare_deck_comment_save(textbuffer, decks_object):
                start = textbuffer.get_start_iter()
                end = textbuffer.get_end_iter()
                comment = textbuffer.get_text(start, end, False)
                model_deck, pathlist_deck = decks_object.select_list_decks.get_selected_rows()
                deck_name = model_deck[pathlist_deck][1]
                decks_object.update_deck_comment(deck_name, comment)
                
        if defs.CURRENT_SAVE_COMMENT_DECK_THREAD == None:
                # we are the first thread, we need to note this
                defs.CURRENT_SAVE_COMMENT_DECK_THREAD = 1
        else:
                defs.CURRENT_SAVE_COMMENT_DECK_THREAD += 1
        my_number = int(defs.CURRENT_SAVE_COMMENT_DECK_THREAD)
        defs.SAVE_COMMENT_DECK_TIMER = 250 # 250 ms
        
        # now, we wait until the end of the timer (or until another thread take our turn)
        go = 1
        while defs.SAVE_COMMENT_DECK_TIMER > 0:
                if my_number != defs.CURRENT_SAVE_COMMENT_DECK_THREAD:
                        # too bad, we have to stop now
                        go = 0
                        break
                else:
                        time.sleep(1 / 1000)
                        defs.SAVE_COMMENT_DECK_TIMER -= 1
        
        if go == 1:
                defs.CURRENT_SAVE_COMMENT_DECK_THREAD = None
                GLib.idle_add(real_prepare_deck_comment_save, textbuffer, decks_object)

def textview_comment_save(textbuffer, decks_object, textview_comm):
        if textview_comm.get_sensitive():
                thread = threading.Thread(target = prepare_deck_comment_save, args = (textbuffer, decks_object))
                thread.daemon = True
                thread.start()

def gen_deck_content(deck_name, box, decks_object):
        '''Displays the cards of the deck.'''
        def _cards_from_deck_to_dict(responses):
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
                return(dict_cards_in_deck)
        
        def _proxies_from_deck_to_dict(responses_proxies):
                dict_proxies_in_deck = {}
                nb_proxies = 0
                if responses_proxies != "" and responses_proxies != None:
                        for card_proxy in responses_proxies.split(";;;"):
                                id_card, nb_card = card_proxy.split("ø")
                                bold = 400
                                italic = Pango.Style.ITALIC
                                dict_proxies_in_deck[id_card] = [int(nb_card), bold, italic]
                                nb_proxies = nb_proxies + int(nb_card)
                return(dict_proxies_in_deck, nb_proxies)
        
        def _gen_complete_list_of_ids(dict_cards_in_deck, dict_proxies_in_deck, responses_proxies):
                complete_list_of_ids = []
                for id_ in dict_cards_in_deck.keys():
                        if id_ not in complete_list_of_ids:
                                complete_list_of_ids.append(id_)
                if responses_proxies != None:
                        if len(responses_proxies) > 0:
                                for id_ in dict_proxies_in_deck.keys():
                                        if id_ not in complete_list_of_ids:
                                                complete_list_of_ids.append(id_)
                return(complete_list_of_ids)
        
        def _list_of_ids_into_str_for_sqlite(complete_list_of_ids):
                tmp_req = ""
                for tmp in complete_list_of_ids:
                        tmp_req = tmp_req + "\"" + str(tmp) + "\", "
                tmp_req = tmp_req[:-2]
                return(tmp_req)
        
        def _add_to_store(cards, side, dict_cards_in_deck, dict_proxies_in_deck, decksstore):
                for id_, card in cards.items():
                        if id_ in dict_cards_in_deck.keys():
                                nb_card = dict_cards_in_deck[id_][0]
                                bold_card = dict_cards_in_deck[id_][1]
                                italic_card = dict_cards_in_deck[id_][2]
                                
                                if side == 0:
                                        name = card["name"]
                                        nameforeign = card["nameforeign"]
                                else:
                                        name = "|" + defs.STRINGS["decks_sideboard"] + card["name"] + "|"
                                        nameforeign = "|" + defs.STRINGS["decks_sideboard"] + card["nameforeign"] + "|"
                                        italic_card = Pango.Style.ITALIC
                                
                                decksstore.insert_with_valuesv(-1, range(18), [card["id_"], name, card["edition_ln"], nameforeign, card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold_card, italic_card, card["nb_variant"], nb_card, 0, side])
                
                        if id_ in dict_proxies_in_deck.keys():
                                nb_card = dict_proxies_in_deck[id_][0]
                                bold_card = dict_proxies_in_deck[id_][1]
                                italic_card = dict_proxies_in_deck[id_][2]
                                
                                if side == 0:
                                        name = "-- " + card["name"]
                                        nameforeign = "-- " + card["nameforeign"]
                                else:
                                        name = "|" + defs.STRINGS["decks_sideboard"] + "-- " + card["name"] + "|"
                                        nameforeign = "|" + defs.STRINGS["decks_sideboard"] + "-- " + card["nameforeign"] + "|"
                                        italic_card = Pango.Style.ITALIC
                                
                                decksstore.insert_with_valuesv(-1, range(18), [card["id_"], name, card["edition_ln"], nameforeign, card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold_card, italic_card, card["nb_variant"], nb_card, 1, side])
        
        for widget in box.get_children():
                box.remove(widget)
        
        conn, c = functions.collection.connect_db()
        c.execute("""SELECT id_coll, id_card FROM collection WHERE deck = ?""", (deck_name,))
        responses = c.fetchall()
        c.execute("""SELECT id_coll, id_card FROM collection WHERE deck_side = ?""", (deck_name,))
        responses_side = c.fetchall()
        c.execute("""SELECT proxies, proxies_side FROM decks WHERE name = ?""", (deck_name,))
        responses_datadeck = c.fetchone()
        functions.collection.disconnect_db(conn)
        nb_cards = len(responses)
        nb_cards_side = len(responses_side)
        
        # we create the toolbar
        toolbar_box = Gtk.ButtonBox(Gtk.Orientation.HORIZONTAL)
        toolbar_box.set_layout(Gtk.ButtonBoxStyle.START)
        toolbar_box.set_spacing(4)
        # the buttons
        if functions.prices.check_prices_presence():
                decks_object.button_estimate_deck.set_sensitive(True)
        else:
                decks_object.button_estimate_deck.set_sensitive(False)
        
        decks_object.button_show_details = Gtk.MenuButton()
        decks_object.button_show_details.set_tooltip_text(defs.STRINGS["show_details_tooltip"])
        decks_object.button_show_details.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="text-editor-symbolic"), Gtk.IconSize.BUTTON))
        decks_object.delete_button = Gtk.Button()
        decks_object.delete_button.set_tooltip_text(defs.STRINGS["delete_from_deck_tooltip"])
        decks_object.delete_button.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="deck_delete-symbolic"), Gtk.IconSize.BUTTON))
        decks_object.button_change_quantity = Gtk.MenuButton()
        decks_object.button_change_quantity.set_tooltip_text(defs.STRINGS["change_quantity_tooltip"])
        decks_object.button_change_quantity.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="zoom-in-symbolic"), Gtk.IconSize.BUTTON))
        decks_object.button_move = Gtk.MenuButton()
        decks_object.button_move.set_tooltip_text(defs.STRINGS["move_to_other_deck_tooltip"])
        decks_object.button_move.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="send-to-symbolic"), Gtk.IconSize.BUTTON))
        
        decks_object.button_side = Gtk.MenuButton()
        decks_object.button_side.set_tooltip_text(defs.STRINGS["sideboard_tooltip"])
        decks_object.button_side.add(Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="application-x-addon-symbolic"), Gtk.IconSize.BUTTON))
        
        for button in [decks_object.button_show_details, decks_object.delete_button, decks_object.button_change_quantity, decks_object.button_move, decks_object.button_side]:
                button.set_sensitive(False)
                toolbar_box.add(button)
        toolbar_box.show_all()
        box.pack_end(toolbar_box, False, True, 0)  
        
        # the real cards in the deck
        dict_cards_in_deck = _cards_from_deck_to_dict(responses)
        
        # the real cards in the sideboard of the deck
        dict_cards_in_deck_side = _cards_from_deck_to_dict(responses_side)
        
        # the proxies in the deck
        dict_proxies_in_deck, nb_proxies_total = _proxies_from_deck_to_dict(responses_datadeck[0])
        nb_cards = nb_cards + nb_proxies_total
        
        # the proxies in the sideboard of the deck
        dict_proxies_in_deck_side, nb_proxies_side_total = _proxies_from_deck_to_dict(responses_datadeck[1])
        nb_cards_side = nb_cards_side + nb_proxies_side_total
        
        # the ids of the cards and the proxies in the deck (not in the sideboard)
        complete_list_of_ids = _gen_complete_list_of_ids(dict_cards_in_deck, dict_proxies_in_deck, responses_datadeck[0])
        
        # the ids of the cards and the proxies in the sideboard of the deck
        complete_list_of_ids_side = _gen_complete_list_of_ids(dict_cards_in_deck_side, dict_proxies_in_deck_side, responses_datadeck[1])
        
        if nb_cards < 2:
                decks_object.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck"].replace("%%%", str(nb_cards)))
        else:
                decks_object.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck_s"].replace("%%%", str(nb_cards)))
        
        if nb_cards_side > 0:
                tmp_text_cards = decks_object.label_nb_cards.get_text()
                tmp_text_side = defs.STRINGS["decks_in_sideboard"].replace("%%%", str(nb_cards_side))
                decks_object.label_nb_cards.set_text(defs.STRINGS["decks_order_cards_sideboard"].replace("{cards}", tmp_text_cards).replace("{sideboard}", tmp_text_side))
        
        conn, c = functions.db.connect_db()
        
        tmp_req = _list_of_ids_into_str_for_sqlite(complete_list_of_ids)
        request = """SELECT * FROM cards WHERE cards.id IN (""" + tmp_req + """)"""
        c.execute(request)
        reponses_db = c.fetchall()
        if nb_cards_side > 0:
                tmp_req_side = _list_of_ids_into_str_for_sqlite(complete_list_of_ids_side)
                request_side = """SELECT * FROM cards WHERE cards.id IN (""" + tmp_req_side + """)"""
                c.execute(request_side)
                reponses_db_side = c.fetchall()
        
        functions.db.disconnect_db(conn)
        
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_min_content_width(560)
        scrolledwindow.set_min_content_height(180)
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
        
        # "id", "name", "edition", "name_foreign", "colors", colors_pixbuf, "cmc", "type", "artist", "power", "toughness", "rarity", "bold", "italic", "nb_variant", "nb", "proxy", "in_sideboard"
        decks_object.mainstore = Gtk.ListStore(str, str, str, str, str, GdkPixbuf.Pixbuf, int, str, str, str, str, str, int, Pango.Style, str, int, int, int)
        tree_deck = Gtk.TreeView(decks_object.mainstore)
        decks_object.maintreeview = tree_deck
        tree_deck.set_enable_search(False)
        # some work with columns
        columns_to_display = functions.config.read_config("decks_columns").split(";")
        coll_columns_list = functions.various.gen_treeview_columns(columns_to_display, tree_deck)[0]
        
        select = tree_deck.get_selection()
        select.set_mode(Gtk.SelectionMode.MULTIPLE)
        select.connect("changed", decks_object.send_id_to_loader, "blip", "blop", 0)
        decks_object.mainselect = select
        scrolledwindow.add(tree_deck)
        
        tree_deck.connect("row-activated", decks_object.show_details, select, decks_object.button_show_details, decks_object.button_change_quantity)
        decks_object.delete_button.connect("clicked", prepare_delete_from_deck, deck_name, select, decks_object)
        
        tree_deck.show_all()
        scrolledwindow.show_all()
        
        box.pack_start(scrolledwindow, True, True, 0)
        
        cards = functions.various.prepare_cards_data_for_treeview(reponses_db)
        _add_to_store(cards, 0, dict_cards_in_deck, dict_proxies_in_deck, decks_object.mainstore)
        
        if nb_cards_side > 0:
                cards_side = functions.various.prepare_cards_data_for_treeview(reponses_db_side)
                _add_to_store(cards_side, 1, dict_cards_in_deck_side, dict_proxies_in_deck_side, decks_object.mainstore)
        
        decks_object.mainstore.set_sort_func(3, functions.various.compare_str, None)
        decks_object.mainstore.set_sort_func(9, functions.various.compare_str_and_int, None)
        decks_object.mainstore.set_sort_func(10, functions.various.compare_str_and_int, None)
        decks_object.mainstore.set_sort_column_id(7, Gtk.SortType.ASCENDING)
        decks_object.mainstore.set_sort_column_id(2, Gtk.SortType.ASCENDING)
        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                decks_object.mainstore.set_sort_column_id(3, Gtk.SortType.ASCENDING)
        else:
                decks_object.mainstore.set_sort_column_id(1, Gtk.SortType.ASCENDING)
        decks_object.displaying_deck = 0

def prepare_move_cards(select_list_decks, selection, old_deck, decks_object):
        model_deck, pathlist_deck = select_list_decks.get_selected_rows()
        new_deck = model_deck[pathlist_deck][1]
        model, pathlist = selection.get_selected_rows()
        ids_db_list = []
        proxies_list_to_change_remove = []
        proxies_list_to_change_add = []
        for row in pathlist:
                if model[row][16] == 0:# not proxy
                        ids_db_list.append([model[row][0], model[row][17]])
                else:
                        proxies_list_to_change_remove.append([model[row][0], model[row][15] * -1, model[row][17]])
                        proxies_list_to_change_add.append([model[row][0], model[row][15], model[row][17]])
        if len(ids_db_list) > 0:
                GLib.idle_add(decks_object.move_row, old_deck, new_deck, ids_db_list)
        if len(proxies_list_to_change_add) > 0:
                GLib.idle_add(decks_object.change_nb_proxies, old_deck, proxies_list_to_change_remove)
                GLib.idle_add(decks_object.change_nb_proxies, new_deck, proxies_list_to_change_add)

def prepare_add_cards_deck(current_deck_name, ids_coll_dict, decks_object, side):
        GLib.idle_add(decks_object.add_cards_to_deck, current_deck_name, ids_coll_dict, side)

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
        
        def button_ok_clicked(button_ok, spinbutton, id_db, ids_cards_free_list, ids_cards_in_current_deck_list, ids_cards_in_current_deck_side_list, current_quantity, popover, selection, current_deck_name, decks_object, side):
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
                        
                        thread = threading.Thread(target = prepare_add_cards_deck, args = (current_deck_name, ids_coll_dict, decks_object, side))
                        thread.daemon = True
                        thread.start()
                elif new_value < current_quantity:
                        # we delete cards
                        nb_cards_to_delete = current_quantity - new_value
                        
                        ids_coll_dict = {}
                        nb_added = 0
                        if side == 0:
                                ids_card_current_to_use = ids_cards_in_current_deck_list
                        else:
                                ids_card_current_to_use = ids_cards_in_current_deck_side_list
                        for card_id_coll in reversed(ids_card_current_to_use):
                                ids_coll_dict[card_id_coll] = [id_db, side]
                                nb_added += 1
                                if nb_added == nb_cards_to_delete:
                                        break
                        thread = threading.Thread(target = prepare_delete_cards_deck, args = (current_deck_name, ids_coll_dict, decks_object))
                        thread.daemon = True
                        thread.start()
                        
                popover.hide()
        
        def button_ok_clicked_proxies(button, spinbutton, id_db, current_quantity, current_deck_name, popover, decks_object, side):
                new_quantity = spinbutton.get_value_as_int()
                diff = new_quantity - current_quantity
                proxies_list_to_change = [[id_db, diff, side]]
                GLib.idle_add(decks_object.change_nb_proxies, current_deck_name, proxies_list_to_change)
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
                        side = model[row][17]
                        current_quantity = model[row][15]
                        break
                
                if proxy == 0:
                        details_store = functions.collection.gen_details_store(selection)
                        ids_cards_free_list = []
                        ids_cards_in_current_deck_list = []
                        ids_cards_in_current_deck_side_list = []
                        cards_in_deck = 0
                        max_cards = len(details_store)
                        for card in details_store:
                                if card[10] == "" and card[14] == "":
                                        ids_cards_free_list.append(card[0])
                                else:
                                        cards_in_deck += 1
                                if card[10] == current_deck_name:
                                        ids_cards_in_current_deck_list.append(card[0])
                                if card[14] == current_deck_name:
                                        ids_cards_in_current_deck_side_list.append(card[0])
                        
                        cards_disp = max_cards - cards_in_deck + current_quantity
                        
                        adjustment = Gtk.Adjustment(value=current_quantity, lower=1, upper=cards_disp, step_increment=1, page_increment=10, page_size=0)
                else:
                        adjustment = Gtk.Adjustment(value=current_quantity, lower=1, upper=100, step_increment=1, page_increment=10, page_size=0)
                spinbutton = Gtk.SpinButton(adjustment=adjustment)
                quantity_box.pack_start(spinbutton, True, True, 0)
                
                button_ok = Gtk.Button(defs.STRINGS["change_quantity_validate"])
                button_ok.set_sensitive(False)
                quantity_box.pack_start(button_ok, True, True, 0)
                
                spinbutton.connect("value-changed", spinbutton_value_changed, button_ok, current_quantity)
                if proxy == 0:
                        button_ok.connect("clicked", button_ok_clicked, spinbutton, id_db, ids_cards_free_list, ids_cards_in_current_deck_list, ids_cards_in_current_deck_side_list, current_quantity, popover, selection, current_deck_name, decks_object, side)
                else:
                        button_ok.connect("clicked", button_ok_clicked_proxies, spinbutton, id_db, current_quantity, current_deck_name, popover, decks_object, side)
                
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
        
        def row_activated(a, b, c, popover, select_list_decks, selection, current_deck_name, decks_object):
                move_cards(None, popover, select_list_decks, selection, current_deck_name, decks_object)
        
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
                tree_decks.connect("row-activated", row_activated, popover, select_list_decks, selection, current_deck_name, decks_object)
                
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
        popover.props.width_request = 200
        popover.connect("show", popover_show, decks_object, move_deck_box, selection)
        popover.add(move_deck_box)
        return(popover)

def gen_edit_comm_name_deck_popover(button_change_comm_deck, decks_object, select_list_decks):
        '''Create the popover which let the user to edit the comment of the deck.'''
        def popover_show(popover, decks_object, select_list_decks):
                def real_show(popover, decks_object, select_list_decks):
                        def rename_deck(button, entry_name_deck, decks_object, popover, current_deck_name):
                                def real_rename_deck(button, entry_name_deck, decks_object, popover, current_deck_name):
                                        popover.hide()
                                        decks_object.rename_deck(current_deck_name, entry_name_deck.get_text())
                                GLib.idle_add(real_rename_deck, button, entry_name_deck, decks_object, popover, current_deck_name)
                        
                        def entry_changed(entry, ok_button, list_decks_names):
                                def real_entry_changed(entry, ok_button, list_decks_names):
                                        if defs.COLL_LOCK == False and entry.get_text() != "" and entry.get_text().lower() not in list_decks_names:
                                                ok_button.set_sensitive(True)
                                        else:
                                                ok_button.set_sensitive(False)
                                GLib.idle_add(real_entry_changed, entry, ok_button, list_decks_names)
                        
                        for widget in popover.get_children():
                                popover.remove(widget)
                        
                        model_deck, pathlist_deck = select_list_decks.get_selected_rows()
                        deck_name = model_deck[pathlist_deck][1]
                        
                        conn_coll, c_coll = functions.collection.connect_db()
                        c_coll.execute("""SELECT name FROM decks""")
                        responses = c_coll.fetchall()
                        list_decks_names = []
                        for tmp_deck_name in responses:
                                list_decks_names.append(tmp_deck_name[0].lower())
                        
                        c_coll.execute("""SELECT comment FROM decks WHERE name = \"""" + deck_name + """\"""")
                        response = c_coll.fetchone()
                        functions.collection.disconnect_db(conn_coll)
                        
                        box_comm = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
                        box_comm.set_margin_top(5)
                        box_comm.set_margin_bottom(5)
                        box_comm.set_margin_left(5)
                        box_comm.set_margin_right(5)
                        popover.add(box_comm)
                        
                        box_comm_name = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                        box_comm.pack_start(box_comm_name, True, True, 0)
                        label_name_deck = Gtk.Label(defs.STRINGS["edit_name_deck"])
                        entry_name_deck = Gtk.Entry()
                        entry_name_deck.set_text(deck_name)
                        ok_button = Gtk.Button(defs.STRINGS["change_deck_name"])
                        entry_name_deck.connect("changed", entry_changed, ok_button, list_decks_names)
                        ok_button.set_sensitive(False)
                        ok_button.connect("clicked", rename_deck, entry_name_deck, decks_object, popover, deck_name)
                        for widget in [label_name_deck, entry_name_deck, ok_button]:
                                box_comm_name.pack_start(widget, True, True, 0)
                        
                        box_comm_comment = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                        box_comm.pack_start(box_comm_comment, True, True, 0)
                        label_comm = Gtk.Label(defs.STRINGS["comment_deck"])
                        scrolledwindow_comm = Gtk.ScrolledWindow()
                        scrolledwindow_comm.set_hexpand(True)
                        scrolledwindow_comm.set_min_content_height(150)
                        scrolledwindow_comm.set_shadow_type(Gtk.ShadowType.IN)
                        textview_comm = Gtk.TextView()
                        textview_comm.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
                        textview_comm.set_sensitive(False)
                        textbuffer = textview_comm.get_buffer()
                        textbuffer.connect("changed", textview_comment_save, decks_object, textview_comm)
                        scrolledwindow_comm.add(textview_comm)
                        
                        textbuffer.set_text(response[0], -1)
                        if defs.COLL_LOCK == False:
                                textview_comm.set_sensitive(True)
                        
                        box_comm_comment.pack_start(label_comm, False, True, 0)
                        box_comm_comment.pack_start(scrolledwindow_comm, False, True, 0)
                        box_comm.show_all()
                
                GLib.idle_add(real_show, popover, decks_object, select_list_decks)
        
        popover = Gtk.Popover.new(button_change_comm_deck)
        popover.props.width_request = 300
        popover.connect("show", popover_show, decks_object, select_list_decks)
        return(popover)

def gen_new_deck_popover(button_new_deck, decks_object):
        '''Create the popover which create deck.'''
        def popover_show(popover, decks_object):
                def create_deck(button, entry_name_deck, decks_object, popover):
                        def real_create_deck(button, entry_name_deck, decks_object, popover):
                                popover.hide()
                                decks_object.create_new_deck(entry_name_deck.get_text())
                        GLib.idle_add(real_create_deck, button, entry_name_deck, decks_object, popover)
                
                def entry_changed(entry, ok_button, list_decks_names):
                        def real_entry_changed(entry, ok_button, list_decks_names):
                                if defs.COLL_LOCK == False and entry.get_text() != "" and entry.get_text().lower() not in list_decks_names:
                                        ok_button.set_sensitive(True)
                                else:
                                        ok_button.set_sensitive(False)
                        GLib.idle_add(real_entry_changed, entry, ok_button, list_decks_names)
                
                def entry_activate(entry_name_deck, ok_button, list_decks_names, decks_object, popover):
                        if defs.COLL_LOCK == False and entry_name_deck.get_text() != "" and entry_name_deck.get_text().lower() not in list_decks_names and ok_button.get_sensitive:
                                create_deck(None, entry_name_deck, decks_object, popover)
                
                def real_show(popover, decks_object):
                        for widget in popover.get_children():
                                popover.remove(widget)
                        
                        new_deck_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                        new_deck_box.set_margin_top(5)
                        new_deck_box.set_margin_bottom(5)
                        new_deck_box.set_margin_left(5)
                        new_deck_box.set_margin_right(5)
                        popover.add(new_deck_box)
                        
                        conn_coll, c_coll = functions.collection.connect_db()
                        c_coll.execute("""SELECT name FROM decks""")
                        responses = c_coll.fetchall()
                        functions.collection.disconnect_db(conn_coll)
                        list_decks_names = []
                        for deck_name in responses:
                                list_decks_names.append(deck_name[0].lower())
                        
                        label_name_deck = Gtk.Label(defs.STRINGS["create_new_deck_name"])
                        entry_name_deck = Gtk.Entry()
                        ok_button = Gtk.Button(defs.STRINGS["create_new_deck_ok"])
                        entry_name_deck.connect("changed", entry_changed, ok_button, list_decks_names)
                        entry_name_deck.connect("activate", entry_activate, ok_button, list_decks_names, decks_object, popover)
                        ok_button.set_sensitive(False)
                        ok_button.connect("clicked", create_deck, entry_name_deck, decks_object, popover)
                        for widget in [label_name_deck, entry_name_deck, ok_button]:
                                new_deck_box.pack_start(widget, True, True, 0)
                        new_deck_box.show_all()
                        entry_name_deck.grab_focus()
                
                GLib.idle_add(real_show, popover, decks_object)
        
        popover = Gtk.Popover.new(button_new_deck)
        popover.props.width_request = 300
        popover.connect("show", popover_show, decks_object)
        return(popover)

def gen_sideboard_popover(decks_object, button_side, selection, nb_row_in_side, nb_row_not_in_side):
        '''Creates the popover which add / remove from the sideboard.'''
        def popover_show(popover, decks_object, ids_db_list, sideboard_box, nb_row_in_side, nb_row_not_in_side):
                def button_sideboard_clicked(button, deck_name, ids_db_list, popover, decks_object):
                        def switch_sideboard(deck_name, ids_db_list, popover, decks_object):
                                popover.hide()
                                decks_object.switch_rows_sideboard(deck_name, ids_db_list)
                        
                        GLib.idle_add(switch_sideboard, deck_name, ids_db_list, popover, decks_object)
                
                for widget in sideboard_box.get_children():
                        sideboard_box.remove(widget)
                
                model_deck, pathlist_deck = decks_object.select_list_decks.get_selected_rows()
                deck_name = model_deck[pathlist_deck][1]
                
                model, pathlist = selection.get_selected_rows()
                ids_db_list = []
                for row in pathlist:
                        id_db = model[row][0]
                        proxy = model[row][16]
                        side = model[row][17]
                        ids_db_list.append([id_db, proxy, side])
                
                button_add_sideboard = Gtk.Button(defs.STRINGS["sideboard_add"])
                button_add_sideboard.connect("clicked", button_sideboard_clicked, deck_name, ids_db_list, popover, decks_object)
                button_remove_sideboard = Gtk.Button(defs.STRINGS["sideboard_remove"])
                button_remove_sideboard.connect("clicked", button_sideboard_clicked, deck_name, ids_db_list, popover, decks_object)
                
                sideboard_box.pack_start(button_remove_sideboard, True, True, 0)
                sideboard_box.pack_start(button_add_sideboard, True, True, 0)
                
                sideboard_box.show_all()
                
                model, pathlist = selection.get_selected_rows()
                if len(pathlist) == nb_row_in_side:
                        button_remove_sideboard.set_sensitive(True)
                        button_add_sideboard.set_sensitive(False)
                else:
                        button_remove_sideboard.set_sensitive(False)
                        button_add_sideboard.set_sensitive(True)
        
        sideboard_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sideboard_box.set_margin_top(5)
        sideboard_box.set_margin_bottom(5)
        sideboard_box.set_margin_left(5)
        sideboard_box.set_margin_right(5)
        popover = Gtk.Popover.new(button_side)
        
        popover.connect("show", popover_show, decks_object, selection, sideboard_box, nb_row_in_side, nb_row_not_in_side)
        popover.add(sideboard_box)
        return(popover)

def write_new_deck_to_db(name_new_deck):
        '''Write the new deck to the collection database.'''
        conn_coll, c_coll = functions.collection.connect_db()
        functions.various.lock_db(True, None)
        
        c_coll.execute("""INSERT INTO decks VALUES(null, ?, ?, ?, ?, ?, ?)""", (name_new_deck, "", "", "", "", "",))
        
        functions.collection.disconnect_db(conn_coll)
        functions.various.lock_db(False, None)

def update_comment_deck_to_db(decks_object, deck_name, new_comment):
        '''Write the new comment of the deck to the collection database and update the list.'''
        def update_comment_in_decks_list(deck_name, decks_object):
                if decks_object != None:
                        try:
                                for i, elm in enumerate(decks_object.store_list_decks):
                                        if elm[1] == deck_name:
                                                decks_object.store_list_decks[i][2] = new_comment.replace("\n", " ")
                                                break
                        except:
                                pass
        
        conn_coll, c_coll = functions.collection.connect_db()
        functions.various.lock_db(True, None)
        c_coll.execute("""UPDATE decks SET comment = ? WHERE name = ?""", (new_comment, deck_name,))
        functions.collection.disconnect_db(conn_coll)
        functions.various.lock_db(False, None)
        
        GLib.idle_add(update_comment_in_decks_list, deck_name, decks_object)

def update_nb_cards_current_deck(decks_object):
        '''Counts the number of cards in the current deck, and update the GtkLabel "label_nb_cards".'''
        nb_cards = 0
        nb_cards_side = 0
        for card_data_deck in decks_object.mainstore:
                if card_data_deck[17] == 0:
                        nb_cards = nb_cards + card_data_deck[15]
                else:
                        nb_cards_side = nb_cards_side + card_data_deck[15]
        if nb_cards < 2:
                decks_object.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck"].replace("%%%", str(nb_cards)))
        else:
                decks_object.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck_s"].replace("%%%", str(nb_cards)))
        if nb_cards_side > 0:
                tmp_text_cards = decks_object.label_nb_cards.get_text()
                tmp_text_side = defs.STRINGS["decks_in_sideboard"].replace("%%%", str(nb_cards_side))
                decks_object.label_nb_cards.set_text(defs.STRINGS["decks_order_cards_sideboard"].replace("{cards}", tmp_text_cards).replace("{sideboard}", tmp_text_side))
