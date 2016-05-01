#!/usr/bin/env python3
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
                self.maintreeview = None
                self.store_list_decks = None
                self.select_list_decks = None
                self.treeview_list_decks = None
                
                self.label_nb_decks = None
                self.label_nb_cards = None
                self.button_show_details = None
                
                self.displaying_deck = 0
                
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
                
                # we load nothing in the card viewer
                self.load_card(None, 0)
                
                self.mainbox.show_all()
        
        def create_new_deck(self, name_new_deck):
                '''Create the new deck.'''
                functions.decks.write_new_deck_to_db(name_new_deck)
                
                if self.store_list_decks == None:
                        functions.decks.gen_decks_display(self, self.right_content)
                else:
                        self.gen_list_decks(name_new_deck)
        
        def rename_deck(self, name_old, name_new):
                '''Rename a deck.'''
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                
                c_coll.execute("""UPDATE decks SET name = ? WHERE name = ?""", (name_new, name_old,))
                c_coll.execute("""UPDATE collection SET deck = ? WHERE deck = ?""", (name_new, name_old,))
                c_coll.execute("""UPDATE collection SET deck_side = ? WHERE deck_side = ?""", (name_new, name_old,))
                
                functions.collection.disconnect_db(conn_coll)
                functions.various.lock_db(False, None)
                
                if self.store_list_decks == None:
                        functions.decks.gen_decks_display(self, self.right_content)
                else:
                        for i, elm in enumerate(self.store_list_decks):
                                if elm[1] == name_old:
                                        self.store_list_decks[i][1] = name_new
                                        break
                        for i, elm in enumerate(self.store_list_decks):
                                if elm[1] == name_new:
                                        self.treeview_list_decks.set_cursor(i)
                                        break
        
        def update_deck_comment(self, deck_name, new_comment):
                '''Write a new comment to the deck 'deck_name'.'''
                functions.decks.update_comment_deck_to_db(self, deck_name, new_comment)
        
        def display_deck_content(self, selection, integer, TreeViewColumn, tree_editions, button_delete_deck):
                '''Displays the content of the deck 'deck_name' in self.right_content_bot.'''
                if self.displaying_deck == 0:
                        model, treeiter = selection.get_selected()
                        if treeiter != None:
                                self.displaying_deck = 1
                                self.button_change_comm_deck.set_sensitive(True)
                                button_delete_deck.set_sensitive(True)
                                deck_name = model[treeiter][1]
                                GLib.idle_add(functions.decks.gen_deck_content, deck_name, self.right_content_bot, self)
                        else:
                                selection.select_path(0)
        
        def add_cards_to_deck(self, deck_name, ids_coll_dict, side):
                '''Add the cards in 'ids_coll_dict' to the deck 'deck_name'.
                ids_coll_dict[id_coll] = id_db
                side: 1 -> add to the sideboard, 0 -> add to the deck
                '''
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                
                col_name = "deck"
                if side == 1:
                        col_name = "deck_side"
                for id_coll in ids_coll_dict.keys():
                        c_coll.execute("""UPDATE collection SET """ + col_name + """ = ? WHERE id_coll = ?""", (deck_name, id_coll,))
                
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
                                                if card_data_deck[0] == card_in_coll_dict and card_data_deck[16] == 0 and card_data_deck[17] == side:
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
                                                bold = 400
                                                nb = c_to_add[card["id_"]]
                                                if side == 0:
                                                        name = card["name"]
                                                        nameforeign = card["nameforeign"]
                                                        italic = Pango.Style.NORMAL
                                                elif side == 1:
                                                        name = "|" + defs.STRINGS["decks_sideboard"] + card["name"] + "|"
                                                        nameforeign = "|" + defs.STRINGS["decks_sideboard"] + card["nameforeign"] + "|"
                                                        italic = Pango.Style.ITALIC
                                                
                                                self.mainstore.insert_with_valuesv(-1, range(18), [card["id_"], name, card["edition_ln"], nameforeign, card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold, italic, card["nb_variant"], nb, 0, side])
                                # we update the nb of cards
                                functions.decks.update_nb_cards_current_deck(self)
                
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
                ids_coll_dict[id_coll] = [id_db, side]
                '''
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                for id_coll, data in ids_coll_dict.items():
                        if data[1] == 0:
                                c_coll.execute("""UPDATE collection SET deck = ? WHERE id_coll = ?""", ("", id_coll,))
                        else:
                                c_coll.execute("""UPDATE collection SET deck_side = ? WHERE id_coll = ?""", ("", id_coll,))
                conn_coll.commit()
                
                # we need the list of all the cards like the cards in 'ids_coll_dict' which are still in a deck
                ids_list = ""
                for data in ids_coll_dict.values():
                        id_, side = data
                        ids_list = ids_list + "\"" + id_ + "\", "
                ids_list = ids_list[:-2]
                c_coll.execute("""SELECT id_coll, id_card, deck, deck_side FROM collection WHERE id_card IN (""" + ids_list + """) AND (deck != \"\" OR deck_side != \"\")""")
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
                                if self.mainstore != None:
                                        for i, card_data_deck in enumerate(self.mainstore):
                                                for data in ids_coll_dict.values():
                                                        card_in_coll_dict, side = data
                                                        if card_data_deck[0] == card_in_coll_dict and card_data_deck[16] == 0 and card_data_deck[17] == side:
                                                                # we need to -1 the quantity
                                                                self.mainstore[i][15] = self.mainstore[i][15] - 1
                                                                if self.mainstore[i][15] < 1:
                                                                        if i not in row_to_delete:
                                                                                row_to_delete.append(i)
                                        for id_to_delete in reversed(row_to_delete):
                                                del(self.mainstore[id_to_delete])
                                        # we update the nb of cards
                                        functions.decks.update_nb_cards_current_deck(self)
                
                # we need to un-italic the cards deleted from the deck, if needed
                dict_responses_coll = {}
                for card_coll in responses_coll_in_deck:
                        id_coll, id_card, deck, deck_side = card_coll
                        try:
                                dict_responses_coll[id_card]
                        except KeyError:
                                dict_responses_coll[id_card] = id_coll
                
                ids_coll_dict_ids_card_list = []
                for id_coll, data in ids_coll_dict.items():
                        id_db, side = data
                        ids_coll_dict_ids_card_list.append(id_db)
                
                coll_object = defs.MAINWINDOW.collection
                for i, row in enumerate(coll_object.mainstore):
                        if row[0] not in dict_responses_coll.keys() and row[0] in ids_coll_dict_ids_card_list:
                                coll_object.mainstore[i][13] = Pango.Style.NORMAL
                
                if coll_object.tree_coll.get_model() == coll_object.searchstore:
                        for i, row in enumerate(coll_object.searchstore):
                                if row[0] not in dict_responses_coll.keys() and row[0] in ids_coll_dict_ids_card_list:
                                        coll_object.mainstore[i][13] = Pango.Style.NORMAL
        
        def change_nb_proxies(self, deck_name, proxies_list_to_change):
                '''Change the quantity of proxy cards in 'proxies_list_to_change' for the deck 'deck_name'.
                proxies_list_to_change[[id_db, int (the modificator), side]]
                '''
                def _gen_dict_current_proxies(response_proxies):
                        dict_current_proxies = {}
                        for proxy_data in response_proxies.split(";;;"):
                                if proxy_data != "":
                                        id_, nb = proxy_data.split("ø")
                                        dict_current_proxies[id_] = int(nb)
                        return(dict_current_proxies)
                
                def _add_proxies_to_deckstore(dict_proxies_to_add, side):
                        conn, c = functions.db.connect_db()
                        tmp_req = ""
                        for tmp in dict_proxies_to_add.keys():
                                tmp_req = tmp_req + "\"" + str(tmp) + "\", "
                        tmp_req = tmp_req[:-2]
                        request = """SELECT * FROM cards WHERE cards.id IN (""" + tmp_req + """)"""
                        c.execute(request)
                        reponses_db = c.fetchall()
                        functions.db.disconnect_db(conn)
                        
                        cards = functions.various.prepare_cards_data_for_treeview(reponses_db)
                        for id_, card in cards.items():
                                nb_card = dict_proxies_to_add[id_]
                                name = "-- " + card["name"]
                                nameforeign = "-- " + card["nameforeign"]
                                if side == 1:
                                        name = "|" + defs.STRINGS["decks_sideboard"] + "-- " + card["name"] + "|"
                                        nameforeign = "|" + defs.STRINGS["decks_sideboard"] + "-- " + card["nameforeign"] + "|"
                                
                                self.mainstore.insert_with_valuesv(-1, range(18), [card["id_"], name, card["edition_ln"], nameforeign, card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], 400, Pango.Style.ITALIC, card["nb_variant"], nb_card, 1, side])
                
                # first, we need the proxies list of this deck
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                
                c_coll.execute("""SELECT proxies, proxies_side FROM decks WHERE name = ?""", (deck_name,))
                response_proxies = c_coll.fetchone()
                
                dict_current_proxies = _gen_dict_current_proxies(response_proxies[0])
                dict_current_proxies_side = _gen_dict_current_proxies(response_proxies[1])
                
                change_proxies = 0
                change_proxies_side = 0
                dict_proxies_to_add = {}
                dict_proxies_to_add_side = {}
                for data in proxies_list_to_change:
                        id_db, qnt, side = data
                        if side == 0:
                                change_proxies += 1
                                try:
                                        dict_current_proxies[id_db] = dict_current_proxies[id_db] + int(qnt)
                                except KeyError:
                                        if int(qnt) > 0:
                                                dict_current_proxies[id_db] = int(qnt)
                                                dict_proxies_to_add[id_db] = int(qnt)
                                if dict_current_proxies[id_db] == 0:
                                        del(dict_current_proxies[id_db])
                        else:
                                change_proxies_side += 1
                                try:
                                        dict_current_proxies_side[id_db] = dict_current_proxies_side[id_db] + int(qnt)
                                except KeyError:
                                        if int(qnt) > 0:
                                                dict_current_proxies_side[id_db] = int(qnt)
                                                dict_proxies_to_add_side[id_db] = int(qnt)
                                if dict_current_proxies_side[id_db] == 0:
                                        del(dict_current_proxies_side[id_db])
                
                # now we prepare the proxies' data for writing
                if change_proxies > 0:
                        proxies_str = ""
                        for id_, qnt in dict_current_proxies.items():
                                proxies_str = proxies_str + id_ + "ø" + str(qnt) + ";;;"
                        proxies_str = proxies_str[:-3]
                        c_coll.execute("""UPDATE decks SET proxies = ? WHERE name = ?""", (proxies_str, deck_name,))
                
                if change_proxies_side > 0:
                        proxies_str = ""
                        for id_, qnt in dict_current_proxies_side.items():
                                proxies_str = proxies_str + id_ + "ø" + str(qnt) + ";;;"
                        proxies_str = proxies_str[:-3]
                        c_coll.execute("""UPDATE decks SET proxies_side = ? WHERE name = ?""", (proxies_str, deck_name,))
                
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
                                                for data in proxies_list_to_change:
                                                        id_card, qnt, side = data
                                                        if side == card_data_deck[17]:# sideboard indicator
                                                                if card_data_deck[0] == id_card:
                                                                        self.mainstore[i][15] = self.mainstore[i][15] + qnt
                                                                        if self.mainstore[i][15] < 1:
                                                                                # we need to delete the row
                                                                                if i not in row_to_delete:
                                                                                        row_to_delete.append(i)
                                # we delete
                                for id_to_delete in reversed(row_to_delete):
                                        del(self.mainstore[id_to_delete])
                                # we add
                                if len(dict_proxies_to_add) > 0:
                                        _add_proxies_to_deckstore(dict_proxies_to_add, 0)
                                if len(dict_proxies_to_add_side) > 0:
                                        _add_proxies_to_deckstore(dict_proxies_to_add_side, 1)
                                
                                # we update the nb of cards
                                functions.decks.update_nb_cards_current_deck(self)
        
        def move_row(self, old_deck, new_deck, ids_db_list):
                '''Move all the cards in the list of ids_db from 'old_deck' to 'new_deck'. 'new_deck' can be "" to delete all these cards from 'old_deck'.
                ids_db_list = [[id_card, side], ...]
                '''
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                for data in ids_db_list:
                        id_db, side = data
                        if side == 0:
                                c_coll.execute("""UPDATE collection SET deck = ? WHERE id_card = ? AND deck = ?""", (new_deck, id_db, old_deck,))
                        else:
                                c_coll.execute("""UPDATE collection SET deck_side = ? WHERE id_card = ? AND deck_side = ?""", (new_deck, id_db, old_deck,))
                conn_coll.commit()
                # we need the list of all cards in 'ids_db_list'
                ids_list = ""
                for data in ids_db_list:
                        id_ = data[0]
                        ids_list = ids_list + "\"" + id_ + "\", "
                ids_list = ids_list[:-2]
                c_coll.execute("""SELECT id_coll, id_card, deck, deck_side FROM collection WHERE id_card IN (""" + ids_list + """)""")
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
                                        for data in ids_db_list:
                                                id_card, side = data
                                                if card_data_deck[0] == id_card and card_data_deck[16] == 0 and card_data_deck[17] == side:
                                                        # we need to delete the row
                                                        if i not in row_to_delete:
                                                                row_to_delete.append(i)
                                for id_to_delete in reversed(row_to_delete):
                                        del(self.mainstore[id_to_delete])
                                # we update the nb of cards
                                functions.decks.update_nb_cards_current_deck(self)
                
                tmp_id_dict = {}
                for card_data in responses_coll_in_deck:
                        id_coll, id_card, deck, deck_side = card_data
                        if deck == "" and deck_side == "":
                                in_deck = False
                        else:
                                in_deck = True
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
                coll_object.mainselect.emit("changed")
                
                if coll_object.tree_coll.get_model() == coll_object.searchstore:
                        for i, row in enumerate(coll_object.searchstore):
                                if row[0] in tmp_id_dict.keys():
                                        if tmp_id_dict[row[0]]:
                                                coll_object.searchstore[i][13] = Pango.Style.ITALIC
                                        else:
                                                coll_object.searchstore[i][13] = Pango.Style.NORMAL
        
        def switch_rows_sideboard(self, deck_name, ids_db_list):
                '''Switches the sideboard position of the db list.
                ids_db_list = [[id_db, proxy, current_side], ...]'''
                proxies_list_to_change = []
                
                functions.various.lock_db(True, None)
                conn_coll, c_coll = functions.collection.connect_db()
                
                for row in ids_db_list:
                        id_db, proxy, current_side = row
                        if current_side == 0:
                                if proxy == 0:
                                        # we put the cards in the sideboard
                                        c_coll.execute("""SELECT id_coll FROM collection WHERE deck = ? AND id_card = ?""", (deck_name, id_db,))
                                        ids_coll_list = c_coll.fetchall()
                                        # we update the collection
                                        for id_coll in ids_coll_list:
                                                c_coll.execute("""UPDATE collection SET deck = \"\", deck_side = ? WHERE id_coll = ?""", (deck_name, id_coll[0],))
                                        # we update the liststore, if needed
                                        model, pathlist = self.select_list_decks.get_selected_rows()
                                        try:
                                                current_deck_name = model[pathlist][1]
                                        except TypeError:
                                                current_deck_name = ""
                                        if current_deck_name != "":
                                                if current_deck_name == deck_name:
                                                        for card_data_deck in self.mainstore:
                                                                if card_data_deck[16] == 0 and card_data_deck[17] == 0 and card_data_deck[0] == id_db:
                                                                        card_data_deck[17] = 1
                                                                        card_data_deck[1] = "|" + defs.STRINGS["decks_sideboard"] + card_data_deck[1] + "|"
                                                                        card_data_deck[3] = "|" + defs.STRINGS["decks_sideboard"] + card_data_deck[3] + "|"
                                                                        card_data_deck[13] = Pango.Style.ITALIC
                                else:
                                        for card_data_deck in self.mainstore:
                                                if card_data_deck[16] == 1 and card_data_deck[17] == 0 and card_data_deck[0] == id_db:
                                                        proxies_list_to_change.append([id_db, card_data_deck[15] * -1, 0])
                                                        proxies_list_to_change.append([id_db, card_data_deck[15], 1])
                        elif current_side == 1:
                                if proxy == 0:
                                        # we remove the cards from the sideboard
                                        c_coll.execute("""SELECT id_coll FROM collection WHERE deck_side = ? AND id_card = ?""", (deck_name, id_db,))
                                        ids_coll_list = c_coll.fetchall()
                                        # we update the collection
                                        for id_coll in ids_coll_list:
                                                c_coll.execute("""UPDATE collection SET deck_side = \"\", deck = ? WHERE id_coll = ?""", (deck_name, id_coll[0],))
                                        # we update the liststore, if needed
                                        model, pathlist = self.select_list_decks.get_selected_rows()
                                        try:
                                                current_deck_name = model[pathlist][1]
                                        except TypeError:
                                                current_deck_name = ""
                                        if current_deck_name != "":
                                                if current_deck_name == deck_name:
                                                        for card_data_deck in self.mainstore:
                                                                if card_data_deck[16] == 0 and card_data_deck[17] == 1 and card_data_deck[0] == id_db:
                                                                        card_data_deck[17] = 0
                                                                        card_data_deck[1] = card_data_deck[1][1:-1].replace(defs.STRINGS["decks_sideboard"], "")
                                                                        card_data_deck[3] = card_data_deck[3][1:-1].replace(defs.STRINGS["decks_sideboard"], "")
                                                                        card_data_deck[13] = Pango.Style.NORMAL
                                else:
                                        for card_data_deck in self.mainstore:
                                                if card_data_deck[16] == 1 and card_data_deck[17] == 1 and card_data_deck[0] == id_db:
                                                        proxies_list_to_change.append([id_db, card_data_deck[15] * -1, 1])
                                                        proxies_list_to_change.append([id_db, card_data_deck[15], 0])
                
                functions.collection.disconnect_db(conn_coll)
                functions.various.lock_db(False, None)
                
                if len(proxies_list_to_change) > 0:
                        self.change_nb_proxies(deck_name, proxies_list_to_change)
                        # we need to select the initial selection of rows
                        for z, card_data_deck in enumerate(self.mainstore):
                                for i, data in enumerate(ids_db_list):
                                        id_db, proxy, side = data
                                        if side == 0:
                                                side = 1
                                        elif side == 1:
                                                side = 0
                                        if card_data_deck[16] == proxy and card_data_deck[17] == side and card_data_deck[0] == id_db:
                                                if i == 0:
                                                        self.maintreeview.set_cursor(z)
                                                self.mainselect.select_path(z)
                else:
                        self.mainselect.emit("changed")
                
                # we update the nb of cards
                functions.decks.update_nb_cards_current_deck(self)
        
        def delete_deck(self, deck_name):
                '''Delete a deck.'''
                functions.various.lock_db(True, None)
                conn_coll, c_coll = functions.collection.connect_db()
                c_coll.execute("""SELECT id_coll, id_card FROM collection WHERE deck = ? OR deck_side = ?""", (deck_name, deck_name,))
                responses_ids = c_coll.fetchall()
                ids_db_list = []
                for data in responses_ids:
                        if data[1] not in ids_db_list:
                                ids_db_list.append(data[1])
                # we need the data of all cards in 'ids_db_list'
                ids_str = ""
                for id_ in ids_db_list:
                        ids_str = ids_str + "\"" + id_ + "\", "
                ids_str = ids_str[:-2]
                c_coll.execute("""SELECT id_coll, id_card, deck, deck_side FROM collection WHERE id_card IN (""" + ids_str + """)""")
                responses = c_coll.fetchall()                
                
                c_coll.execute("""UPDATE collection SET deck = \"\", deck_side = \"\" WHERE deck = ? OR deck_side = ?""", (deck_name, deck_name,))
                c_coll.execute("""DELETE FROM decks WHERE name = ?""", (deck_name,))
                functions.collection.disconnect_db(conn_coll)
                functions.various.lock_db(False, None)
                
                model, pathlist = self.select_list_decks.get_selected_rows()
                del(model[pathlist])
                
                if self.update_nb_decks() < 1:
                        self.mainstore.clear()
                        self.label_nb_cards.set_text("")
                
                tmp_id_dict = {}
                for card_data in responses:
                        id_coll, id_card, deck, deck_side = card_data
                        if (deck != "" and deck != deck_name) or (deck_side != "" and deck_side != deck_name):
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
                if coll_object.mainstore != None:
                        for i, row in enumerate(coll_object.mainstore):
                                if row[0] in tmp_id_dict.keys():
                                        if tmp_id_dict[row[0]]:
                                                coll_object.mainstore[i][13] = Pango.Style.ITALIC
                                        else:
                                                coll_object.mainstore[i][13] = Pango.Style.NORMAL
                if coll_object.searchstore != None:
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
                        return(count_nb)
                else:
                        return(None)
        
        def gen_list_decks(self, deck_to_select):
                if self.store_list_decks != None:
                        self.displaying_deck = 1
                        self.store_list_decks.clear()
                        conn_coll, c_coll = functions.collection.connect_db()
                        c_coll.execute("""SELECT id_deck, name, comment FROM decks""")
                        responses = c_coll.fetchall()
                        functions.collection.disconnect_db(conn_coll)
                        
                        for id_deck, name, comment in responses:
                                self.store_list_decks.append([str(id_deck), name, comment.replace("\n", " ")])
                        self.update_nb_decks()
                        self.displaying_deck = 0
                        
                        if self.select_list_decks != None:
                                if deck_to_select == None:
                                        pass
                                else:
                                        for i, decks_data in enumerate(self.store_list_decks):
                                                if decks_data[1] == deck_to_select:
                                                        break
                                        self.select_list_decks.select_path(i)
                                        for i, elm in enumerate(self.store_list_decks):
                                                if elm[1] == deck_to_select:
                                                        self.treeview_list_decks.set_cursor(i)
                                                        break
        
        def show_details(self, treeview, treepath, column, selection, button_show_details, button_change_quantity):
                model, pathlist = selection.get_selected_rows()
                for row in pathlist:
                        if model[row][16] == 0:
                                if button_show_details.get_sensitive():
                                        button_show_details.emit("clicked")
                        elif model[row][16] == 1:
                                if button_change_quantity.get_sensitive():
                                        button_change_quantity.emit("clicked")
                        break
        
        def send_id_to_loader(self, selection, integer, TreeViewColumn, simple_search):
                model, pathlist = selection.get_selected_rows()
                if pathlist != []:
                        tree_iter = model.get_iter(pathlist[0])
                        id_ = model.get_value(tree_iter, 0)
                        self.load_card(id_, simple_search)
                        
                        nb_row_in_side = 0
                        nb_row_not_in_side = 0
                        for row in pathlist:
                                if model[row][17] == 1:
                                        nb_row_in_side += 1
                                else:
                                        nb_row_not_in_side += 1
                        if nb_row_in_side > 0 and nb_row_not_in_side > 0:
                                self.button_side.set_sensitive(False)
                        else:
                                self.button_side.set_sensitive(True)
                                self.button_side.set_popover(functions.decks.gen_sideboard_popover(self, self.button_side, selection, nb_row_in_side, nb_row_not_in_side))
                        
                        nb_row_proxy = 0
                        for row in pathlist:
                                if model[row][16] == 1:
                                        nb_row_proxy += 1
                        if nb_row_proxy == len(pathlist):
                                self.button_show_details.set_sensitive(False)
                        else:
                                self.button_show_details.set_sensitive(True)
                                self.button_show_details.set_popover(functions.collection.gen_details_popover(self.button_show_details, selection))
                        self.delete_button.set_sensitive(True)
                        self.button_move.set_popover(functions.decks.gen_move_deck_popover(self.button_move, selection, self))
                        self.button_move.set_sensitive(True)
                        
                        if len(pathlist) == 1:
                                self.button_change_quantity.set_sensitive(True)
                                self.button_change_quantity.set_popover(functions.decks.gen_deck_change_quantity_popover(self.button_change_quantity, selection, self))
                        else:
                                self.button_change_quantity.set_sensitive(False)
                else:
                        self.button_show_details.set_sensitive(False)
                        self.button_move.set_sensitive(False)
                        self.delete_button.set_sensitive(False)
                        self.button_change_quantity.set_sensitive(False)
        
        def load_card(self, cardid, simple_search):
                '''Load a card in the card viewer'''
                GLib.idle_add(functions.cardviewer.gen_card_viewer, cardid, self.card_viewer, self, simple_search)
                #functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
        
        def load_card_from_outside(self, widget, cardid, list_widgets_to_destroy, simple_search):
                GLib.idle_add(functions.cardviewer.gen_card_viewer, cardid, self.card_viewer, self, simple_search)
                #functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
