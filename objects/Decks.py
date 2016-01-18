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

from gi.repository import Gtk, Gio, GdkPixbuf, GLib, Pango, GLib
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
import functions.decks

class Decks:
        '''The decks class. Manage the decks part of MC.'''
        def __init__(self, mainwindow):
                self.mainstore = None
                self.mainselect = None
                self.store_list_decks = None
                self.select_list_decks = None
                
                self.label_nb_decks = None
                self.label_nb_cards = None
                self.button_show_details = None
                
                self.mainbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
                self.mainbox.set_margin_top(5)
                self.mainbox.set_margin_bottom(5)
                self.mainbox.set_margin_left(5)
                self.mainbox.set_margin_right(5)
                
                mainwindow.main_stack.add_titled(self.mainbox, "decks", defs.STRINGS["decks"])
                
                self.card_viewer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
                self.right_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                self.mainbox.pack_start(self.card_viewer, False, False, 0)
                self.mainbox.pack_start(separator, False, False, 0)
                self.mainbox.pack_start(self.right_content, True, True, 0)
                
                self.right_content_bot = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                functions.decks.gen_decks_display(self, self.right_content)
                self.right_content.pack_start(self.right_content_bot, True, True, 0)
                
                # we load nothing in the card viewer
                self.load_card(None, 0)
                
                self.mainbox.show_all()
        
        def create_new_deck(self, name_new_deck):
                '''Create the new deck.'''
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                
                c_coll.execute("""INSERT INTO decks VALUES(null, ?, ?, ?)""", (name_new_deck, "", "",))
                
                functions.collection.disconnect_db(conn_coll)
                functions.various.lock_db(False, None)
                
                if self.store_list_decks == None:
                        self.gen_decks_display(self.right_content)
                else:
                        self.gen_list_decks()
        
        def display_deck_content(self, selection, integer, TreeViewColumn, tree_editions):
                '''Displays the content of the deck 'deck_name' in self.right_content_bot.'''
                model, treeiter = selection.get_selected()
                if treeiter != None:
                        deck_name = model[treeiter][1]
                        #functions.decks.gen_deck_content(deck_name, self.right_content_bot, self)
                        GLib.idle_add(functions.decks.gen_deck_content, deck_name, self.right_content_bot, self)
        
        def add_cards_to_deck(self, deck_name, ids_coll_dict):
                '''Add the cards in 'ids_coll_dict' to the deck 'deck_name'.
                ids_coll_dict[id_coll] = id_db
                '''
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                for id_coll in ids_coll_dict.keys():
                        c_coll.execute("""UPDATE collection SET deck = ? WHERE id_coll = ?""", (deck_name, id_coll,))
                
                functions.collection.disconnect_db(conn_coll)
                functions.various.lock_db(False, None)
                
                # if this deck is the deck selected in the Decks mode, we need to add the cards to it
                c_added = []
                model, pathlist = self.select_list_decks.get_selected_rows()
                try:
                        current_deck_name = model[pathlist][1]
                except TypeError:
                        current_deck_name = ""
                if current_deck_name != "":
                        if current_deck_name == deck_name:
                                for i, card_data_deck in enumerate(self.mainstore):
                                        for card_in_coll_dict in ids_coll_dict.values():
                                                if card_data_deck[0] == card_in_coll_dict and card_data_deck[16] == 0:
                                                        # we need to +1 the quantity
                                                        self.mainstore[i][15] = self.mainstore[i][15] + 1
                                                        if card_data_deck[0] not in c_added:
                                                                c_added.append(card_data_deck[0])
                                # now, we need to add the cards which are not already in the deck
                                c_to_add = {}
                                for id_coll, id_db in ids_coll_dict.items():
                                        if id_db not in c_added:
                                                try:
                                                        c_to_add[id_db]
                                                except KeyError:
                                                        c_to_add[id_db] = 1
                                                else:
                                                        c_to_add[id_db] = c_to_add[id_db] + 1
                                
                                if len(c_to_add) > 0:
                                        conn, c = functions.db.connect_db()
                                        id_list_req = ""
                                        for card_tmp in c_to_add.keys():
                                                id_list_req = id_list_req + "\"" + card_tmp + "\"" + ", "
                                        id_list_req = id_list_req[:-2]
                                        reqq = """SELECT * FROM cards WHERE id IN (""" + id_list_req + """)"""
                                        c.execute(reqq)
                                        reponse_all = c.fetchall()
                                        functions.db.disconnect_db(conn)
                                        
                                        cards = functions.various.prepare_cards_data_for_treeview(reponse_all)
                                        for card in cards.values():
                                                italic = Pango.Style.NORMAL
                                                bold = 400
                                                nb = c_to_add[card["id_"]]
                                                self.mainstore.insert_with_valuesv(-1, range(17), [card["id_"], card["name"], card["edition_ln"], card["nameforeign"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold, italic, card["nb_variant"], nb, 0])
                                # we update the nb of cards
                                nb_cards = 0
                                for card_data_deck in self.mainstore:
                                        nb_cards = nb_cards + card_data_deck[15]
                                if nb_cards < 2:
                                        self.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck"].replace("%%%", str(nb_cards)))
                                else:
                                        self.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck_s"].replace("%%%", str(nb_cards)))
                
                # we need to italic the cards added in the deck
                new_id_db_to_italic = []
                for id_db in ids_coll_dict.values():
                        if id_db not in new_id_db_to_italic:
                                new_id_db_to_italic.append(id_db)
                
                coll_object = defs.MAINWINDOW.collection
                for i, row in enumerate(coll_object.mainstore):
                        if row[0] in new_id_db_to_italic:
                                coll_object.mainstore[i][13] = Pango.Style.ITALIC
                
                if coll_object.tree_coll.get_model() == coll_object.searchstore:
                        for i, row in enumerate(coll_object.searchstore):
                                if row[0] in new_id_db_to_italic:
                                        coll_object.mainstore[i][13] = Pango.Style.ITALIC
        
        def delete_cards_from_deck(self, deck_name, ids_coll_dict):
                '''Deletes the cards in 'ids_coll_dict' from the deck 'deck_name'.
                ids_coll_dict[id_coll] = id_db
                '''
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                for id_coll in ids_coll_dict.keys():
                        c_coll.execute("""UPDATE collection SET deck = ? WHERE id_coll = ?""", ("", id_coll,))
                conn_coll.commit()
                
                # we need the list of all cards in 'ids_coll_dict' which are still in a deck
                ids_list = ""
                for id_ in ids_coll_dict.values():
                        ids_list = ids_list + "\"" + id_ + "\", "
                ids_list = ids_list[:-2]
                c_coll.execute("""SELECT id_coll, id_card, deck FROM collection WHERE id_card IN (""" + ids_list + """) AND deck != \"\"""")
                responses_coll_in_deck = c_coll.fetchall()
                
                functions.collection.disconnect_db(conn_coll)
                functions.various.lock_db(False, None)
                
                # if this deck is the deck selected in the Decks mode, we need to update it
                row_to_delete = []
                model, pathlist = self.select_list_decks.get_selected_rows()
                try:
                        current_deck_name = model[pathlist][1]
                except TypeError:
                        current_deck_name = ""
                if current_deck_name != "":
                        if current_deck_name == deck_name:
                                for i, card_data_deck in enumerate(self.mainstore):
                                        for card_in_coll_dict in ids_coll_dict.values():
                                                if card_data_deck[0] == card_in_coll_dict and card_data_deck[16] == 0:
                                                        # we need to -1 the quantity
                                                        self.mainstore[i][15] = self.mainstore[i][15] - 1
                                                        if self.mainstore[i][15] < 1:
                                                                if i not in row_to_delete:
                                                                        row_to_delete.append(i)
                                for id_to_delete in reversed(row_to_delete):
                                        del(self.mainstore[id_to_delete])
                                # we update the nb of cards
                                nb_cards = 0
                                for card_data_deck in self.mainstore:
                                        nb_cards = nb_cards + card_data_deck[15]
                                if nb_cards < 2:
                                        self.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck"].replace("%%%", str(nb_cards)))
                                else:
                                        self.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck_s"].replace("%%%", str(nb_cards)))
                
                # we need to un-italic the cards deleted from the deck, if needed
                dict_responses_coll = {}
                for card_coll in responses_coll_in_deck:
                        id_coll, id_card, deck = card_coll
                        try:
                                dict_responses_coll[id_card]
                        except KeyError:
                                dict_responses_coll[id_card] = id_coll
                
                coll_object = defs.MAINWINDOW.collection
                for i, row in enumerate(coll_object.mainstore):
                        if row[0] not in dict_responses_coll.keys() and row[0] in ids_coll_dict.values():
                                coll_object.mainstore[i][13] = Pango.Style.NORMAL
                
                if coll_object.tree_coll.get_model() == coll_object.searchstore:
                        for i, row in enumerate(coll_object.searchstore):
                                if row[0] not in dict_responses_coll.keys() and row[0] in ids_coll_dict.values():
                                        coll_object.mainstore[i][13] = Pango.Style.NORMAL
        
        def delete_proxies(self, deck_name, proxies_dict_to_delete):
                '''Delete the proxy cards in 'proxies_dict_to_delete' of the deck 'deck_name'.
                proxies_dict_to_delete[id_db] = int (> 0)
                '''
                # first, we need the proxies list of this deck
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                
                c_coll.execute("""SELECT proxies FROM decks WHERE name = ?""", (deck_name,))
                response_proxies = c_coll.fetchone()
                dict_current_proxies = {}
                for proxy_data in response_proxies[0].split(";;;"):
                        id_, nb = proxy_data.split("ø")
                        dict_current_proxies[id_] = int(nb)
                
                for id_db, qnt in proxies_dict_to_delete.items():
                        dict_current_proxies[id_db] = dict_current_proxies[id_db] - int(qnt)
                        if dict_current_proxies[id_db] == 0:
                                del(dict_current_proxies[id_db])
                
                # now we prepare the proxies' data for writing
                proxies_str = ""
                for id_, qnt in dict_current_proxies.items():
                        proxies_str = proxies_str + id_ + "ø" + str(qnt) + ";;;"
                proxies_str = proxies_str[:-3]
                c_coll.execute("""UPDATE decks SET proxies = ? WHERE name = ?""", (proxies_str, deck_name,))
                
                functions.collection.disconnect_db(conn_coll)
                functions.various.lock_db(False, None)
                
                # if 'deck_name' is the deck selected in the Decks mode, we need to update it
                row_to_delete = []
                model, pathlist = self.select_list_decks.get_selected_rows()
                try:
                        current_deck_name = model[pathlist][1]
                except TypeError:
                        current_deck_name = ""
                if current_deck_name != "":
                        if current_deck_name == deck_name:
                                for i, card_data_deck in enumerate(self.mainstore):
                                        if card_data_deck[16] == 1:# proxy indicator
                                                for card_in_coll_dict in proxies_dict_to_delete.keys():
                                                        if card_data_deck[0] == card_in_coll_dict:
                                                                # we need to delete the row
                                                                if i not in row_to_delete:
                                                                        row_to_delete.append(i)
                                for id_to_delete in reversed(row_to_delete):
                                        del(self.mainstore[id_to_delete])
                                # we update the nb of cards
                                nb_cards = 0
                                for card_data_deck in self.mainstore:
                                        nb_cards = nb_cards + card_data_deck[15]
                                if nb_cards < 2:
                                        self.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck"].replace("%%%", str(nb_cards)))
                                else:
                                        self.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck_s"].replace("%%%", str(nb_cards)))
        
        def move_row(self, old_deck, new_deck, ids_db_list):
                '''Move all the cards in the list of ids_db from 'old_deck' to 'new_deck'. 'new_deck' can be "" to delete all these cards from 'old_deck'.'''
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                for id_db in ids_db_list:
                        c_coll.execute("""UPDATE collection SET deck = ? WHERE id_card = ? AND deck = ?""", (new_deck, id_db, old_deck,))
                conn_coll.commit()
                # we need the list of all cards in 'ids_db_list'
                ids_list = ""
                for id_ in ids_db_list:
                        ids_list = ids_list + "\"" + id_ + "\", "
                ids_list = ids_list[:-2]
                c_coll.execute("""SELECT id_coll, id_card, deck FROM collection WHERE id_card IN (""" + ids_list + """)""")
                responses_coll_in_deck = c_coll.fetchall()
                
                functions.collection.disconnect_db(conn_coll)
                functions.various.lock_db(False, None)
                
                # if 'old_deck' is the deck selected in the Decks mode, we need to update it
                row_to_delete = []
                model, pathlist = self.select_list_decks.get_selected_rows()
                try:
                        current_deck_name = model[pathlist][1]
                except TypeError:
                        current_deck_name = ""
                if current_deck_name != "":
                        if current_deck_name == old_deck:
                                for i, card_data_deck in enumerate(self.mainstore):
                                        for card_in_coll_dict in ids_db_list:
                                                if card_data_deck[0] == card_in_coll_dict and card_data_deck[16] == 0:
                                                        # we need to delete the row
                                                        if i not in row_to_delete:
                                                                row_to_delete.append(i)
                                for id_to_delete in reversed(row_to_delete):
                                        del(self.mainstore[id_to_delete])
                                # we update the nb of cards
                                nb_cards = 0
                                for card_data_deck in self.mainstore:
                                        nb_cards = nb_cards + card_data_deck[15]
                                if nb_cards < 2:
                                        self.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck"].replace("%%%", str(nb_cards)))
                                else:
                                        self.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck_s"].replace("%%%", str(nb_cards)))
                
                tmp_id_dict = {}
                for card_data in responses_coll_in_deck:
                        id_coll, id_card, deck = card_data
                        if deck != "":
                                in_deck = True
                        else:
                                in_deck = False
                        try:
                                tmp_id_dict[id_card]
                        except KeyError:
                                tmp_id_dict[id_card] = in_deck
                        else:
                                if tmp_id_dict[id_card]:
                                        pass
                                else:
                                        tmp_id_dict[id_card] = in_deck
                
                coll_object = defs.MAINWINDOW.collection
                for i, row in enumerate(coll_object.mainstore):
                        if row[0] in tmp_id_dict.keys():
                                if tmp_id_dict[row[0]]:
                                        coll_object.mainstore[i][13] = Pango.Style.ITALIC
                                else:
                                        coll_object.mainstore[i][13] = Pango.Style.NORMAL
                
                if coll_object.tree_coll.get_model() == coll_object.searchstore:
                        for i, row in enumerate(coll_object.searchstore):
                                if row[0] in tmp_id_dict.keys():
                                        if tmp_id_dict[row[0]]:
                                                coll_object.searchstore[i][13] = Pango.Style.ITALIC
                                        else:
                                                coll_object.searchstore[i][13] = Pango.Style.NORMAL
        
        def update_nb_decks(self):
                '''Update the label which displays the number of decks.'''
                if self.label_nb_decks != None:
                        conn_coll, c_coll = functions.collection.connect_db()
                        c_coll.execute("""SELECT COUNT(*) FROM decks""")
                        count_nb = c_coll.fetchone()[0]
                        functions.collection.disconnect_db(conn_coll)
                        self.label_nb_decks.set_text(defs.STRINGS["list_decks_nb"].replace("%%%", str(count_nb)))
        
        def gen_list_decks(self):
                if self.store_list_decks != None:
                        self.store_list_decks.clear()
                        conn_coll, c_coll = functions.collection.connect_db()
                        c_coll.execute("""SELECT id_deck, name FROM decks""")
                        responses = c_coll.fetchall()
                        functions.collection.disconnect_db(conn_coll)
                        
                        for id_deck, name in responses:
                                self.store_list_decks.append([str(id_deck), name])
                        self.update_nb_decks()
        
        def show_details(self, treeview, treepath, column, selection, button_show_details):
                if button_show_details.get_sensitive():
                        button_show_details.emit("clicked")
        
        def send_id_to_loader(self, selection, integer, TreeViewColumn, simple_search):
                model, pathlist = selection.get_selected_rows()
                if pathlist != []:
                        tree_iter = model.get_iter(pathlist[0])
                        id_ = model.get_value(tree_iter, 0)
                        self.load_card(id_, simple_search)
                        
                        nb_row_proxy = 0
                        for row in pathlist:
                                if model[row][16] == 1:
                                        nb_row_proxy += 1
                                        break
                        if nb_row_proxy == 0:
                                self.button_show_details.set_sensitive(True)
                                self.button_show_details.set_popover(functions.collection.gen_details_popover(self.button_show_details, selection)[0])
                                self.button_move.set_popover(functions.decks.gen_move_deck_popover(self.button_move, selection, self))
                                self.button_move.set_sensitive(True)
                        else:
                                self.button_show_details.set_sensitive(False)
                                self.button_move.set_sensitive(False)
                        self.delete_button.set_sensitive(True)
                else:
                        self.button_show_details.set_sensitive(False)
                        self.button_move.set_sensitive(False)
                        self.delete_button.set_sensitive(False)
        
        def load_card(self, cardid, simple_search):
                '''Load a card in the card viewer'''
                #GLib.idle_add(functions.cardviewer.gen_card_viewer, cardid, self.card_viewer, self, simple_search)
                functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
        
        def load_card_from_outside(self, widget, cardid, list_widgets_to_destroy, simple_search):
                #GLib.idle_add(functions.cardviewer.gen_card_viewer, cardid, self.card_viewer, self, simple_search)
                functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
