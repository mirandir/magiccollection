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

# Collection class for Magic Collection

from gi.repository import Gtk, Gio, GdkPixbuf, Pango, GLib
import sys
import os
import time
from datetime import date

# imports def.py
import defs
# imports objects
import objects.mc
# imports functions
import functions.cardviewer
import functions.config
import functions.db
import functions.collection

class Collection:
        '''The collection class. Manage the collection part of MC.'''
        def __init__(self, mainwindow):
                self.mainstore = None
                self.mainselect = None
                
                self.searchstore = None
                
                self.mainbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
                self.mainbox.set_margin_top(5)
                self.mainbox.set_margin_bottom(5)
                self.mainbox.set_margin_left(5)
                self.mainbox.set_margin_right(5)
                
                mainwindow.main_stack.add_titled(self.mainbox, "collection", defs.STRINGS["collection"])
                
                self.card_viewer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
                self.overlay_right_content = Gtk.Overlay()
                self.right_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                
                self.overlay_right_content.add(self.right_content)
                self.mainbox.pack_start(self.card_viewer, False, False, 0)
                self.mainbox.pack_start(separator, False, False, 0)
                self.mainbox.pack_start(self.overlay_right_content, True, True, 0)
                
                if os.path.isfile(os.path.join(defs.HOMEMC, "collection.sqlite")) == False:
                        # we create the collection db
                        functions.collection.create_db_coll()
                
                if os.path.isfile(os.path.join(defs.HOMEMC, "collection.sqlite")):
                        functions.collection.read_coll(self.right_content, self)
                else:
                        label_error_coll = Gtk.Label()
                        label_error_coll.set_markup("<big>" + defs.STRINGS["db_coll_error"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</big>")
                        label_error_coll.props.halign = Gtk.Align.CENTER
                        self.right_content.pack_start(label_error_coll, True, True, 0)
                
                # we load nothing in the card viewer
                self.load_card(None, 0)
                
                self.mainbox.show_all()
                
        def add_collection(self, cards_list, spinner_labels):
                '''Add cards to the collection. Each member of "cards_list" must have 6 elements : the card ID in the DB, condition, lang, foil, loaned_to, comment, nb.'''                       
                def select_rows(rows_to_select):
                        try:
                                self.select.unselect_all()
                        except AttributeError:
                                pass
                        
                        for po, nb_row in enumerate(rows_to_select):
                                if po == 0:
                                        self.tree_coll.set_cursor(nb_row)
                                self.select.select_path(nb_row) # FIXME: this freezes GTK after selecting rows, why ??
                
                try:
                        if self.tree_coll.get_model() == self.mainstore:
                                GLib.idle_add(self.select.unselect_all)
                except AttributeError:
                        pass
                
                conn, c = functions.db.connect_db()
                conn_coll, c_coll = functions.collection.connect_db()
                cards_data_for_update_store_as = []
                
                id_list_req = ""
                for card_tmp in cards_list:
                        id_list_req = id_list_req + "\"" + card_tmp[0] + "\"" + ", "
                id_list_req = id_list_req[:-2]
                reqq = """SELECT * FROM cards WHERE id IN (""" + id_list_req + """)"""
                c.execute(reqq)
                reponse_all = c.fetchall()
                functions.db.disconnect_db(conn)
                
                # we must be sure to lock the access for the db of the collection
                if defs.COLL_LOCK == False:
                        functions.various.lock_db(True, None)
                
                for card_to_add in cards_list:
                        cardid, condition, lang, foil, loaned_to, comment, nb = card_to_add
                        card_found = 0
                        for reponse in reponse_all:
                                if str(reponse[0]) == str(cardid):
                                        card_found = 1
                                        break
                        
                        if card_found == 0:
                                print("Something is wrong in the universe. In fact, only in the database but...")
                        else:
                                id_, name, nb_variante, names, edition_code, name_chinesetrad, name_chinesesimp, name_french, name_german, name_italian, name_japanese, name_korean, name_portuguesebrazil, name_portuguese, name_russian, name_spanish, colors, manacost, cmc, multiverseid, imageurl, type_, artist, text, flavor, power, toughness, loyalty, rarity, layout, number, variations = reponse
                                
                                current_id_ = id_
                                
                                # the current date
                                today = date.today()
                                month = '%02d' % today.month
                                day = '%02d' % today.day
                                current_date = str(today.year) + "-" + str(month) + "-" + str(day)
                                
                                for z in range(nb):
                                        # we add the card to the collection DB
                                        c_coll.execute("""
                                        INSERT INTO collection VALUES(null, ?, ?, ?, ?, ?, ?, ?, ?)""", (id_, current_date, condition, lang, foil, loaned_to, comment, ""))
                                
                                # we update the collection store / treeview
                                i = 0
                                card_added = 0
                                if self.mainstore == None:
                                        conn_coll.commit()
                                        defs.READ_COLL_FINISH = False
                                        GLib.idle_add(functions.collection.read_coll, self.right_content, self)
                                        while defs.READ_COLL_FINISH != True:
                                                time.sleep(1 / 1000)
                                        defs.READ_COLL_FINISH = False
                                        cards = functions.various.prepare_cards_data_for_treeview([reponse])
                                        for card in cards.values():
                                                cards_data_for_update_store_as.append([card["name"], card["edition_ln"]])
                                else:
                                        try:
                                                if self.tree_coll.get_model() == self.mainstore:
                                                        GLib.idle_add(self.label_nb_card_coll.set_text, defs.STRINGS["nb_card_coll_s"].replace("%%%", "--"))
                                        except:
                                                pass
                                        for row in self.mainstore:
                                                id_ = row[0]
                                                if current_id_ == id_:
                                                        # another card like us is in the collection => curent nb + nb
                                                        self.mainstore[i][15] = int(self.mainstore[i][15]) + int(nb)
                                                        if comment != "":
                                                                # we need to bold the row
                                                                self.mainstore[i][12] = 700
                                                        card_added = 1
                                                i += 1
                                        
                                        if self.tree_coll.get_model() == self.searchstore:
                                                for j, row in enumerate(self.searchstore):
                                                        id_ = row[0]
                                                        if current_id_ == id_:
                                                                # another card like us is in the searchstore => curent nb + nb
                                                                self.searchstore[j][15] = int(self.searchstore[j][15]) + int(nb)
                                                                if comment != "":
                                                                        # we need to bold the row
                                                                        self.searchstore[j][12] = 700
                                        
                                        if card_added == 0:
                                                # we need to add a new row
                                                cards = functions.various.prepare_cards_data_for_treeview([reponse])
                                                for card in cards.values():
                                                        italic = Pango.Style.NORMAL
                                                        bold = 400
                                                        if comment != "":
                                                                bold = 700
                                                        self.mainstore.insert_with_valuesv(-1, range(17), [card["id_"], card["name"], card["edition_ln"], card["nameforeign"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold, italic, card["nb_variant"], nb])
                                                        cards_data_for_update_store_as.append([card["name"], card["edition_ln"]])
                
                if cards_data_for_update_store_as != []:
                        GLib.idle_add(defs.MAINWINDOW.advancedsearch.update_current_store_bold, cards_data_for_update_store_as)
                
                if self.tree_coll.get_model() == self.mainstore:
                        # we count the number of cards in the collection
                        conn_coll.commit()
                        c_coll.execute("""SELECT COUNT(*) FROM collection""")
                        count_nb = c_coll.fetchone()[0]
                        if count_nb == 1:
                                GLib.idle_add(self.label_nb_card_coll.set_text, defs.STRINGS["nb_card_coll"].replace("%%%", str(count_nb)))
                        else:
                                GLib.idle_add(self.label_nb_card_coll.set_text, defs.STRINGS["nb_card_coll_s"].replace("%%%", str(count_nb)))
                        
                        # we select the rows of added cards, and set the cursor on the first
                        rows_to_select = []
                        for nb_row, row in enumerate(self.mainstore):
                                for new_card in cards_list:
                                        if new_card[0] == row[0]:
                                                rows_to_select.append(nb_row)
                        GLib.idle_add(select_rows, rows_to_select)
                
                functions.collection.disconnect_db(conn_coll)
                functions.various.lock_db(False, None)
                
                if spinner_labels != None:
                        GLib.idle_add(spinner_labels.destroy)
        
        def del_all_collection_decks(self):
                '''Delete all decks and all cards in the collection (caution).'''
                # we are not monsters, we make a backup
                today = date.today()
                m = '%02d' % today.month
                d = '%02d' % today.day
                date_today = str(today.year) + str(m) + str(d)
                
                back_folder = os.path.join(defs.HOMEMC, "backup")
                if (os.path.isdir(back_folder)) == False:
                        os.mkdir(back_folder)
                os.rename(os.path.join(defs.HOMEMC, "collection.sqlite"), os.path.join(back_folder, "collection_" + date_today + ".sql"))
                
                python = sys.executable
                os.execl(python, python, os.path.join(defs.PATH_MC, "magic_collection.py"))
        
        def del_collection(self, cards_to_delete):
                '''Delete the cards in 'cards_to_delete'.'''
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                
                for id_coll in cards_to_delete.keys():
                        c_coll.execute("""DELETE from collection WHERE id_coll = ?""", (id_coll,))
                
                conn_coll.commit()
                
                # we need to update the treeview of the collection and of the search
                new_id_db_to_bold = []
                new_id_db_to_unbold = []
                # we need to find the ids_db of all current ids_coll
                ids_list = ""
                for id_ in cards_to_delete.values():
                        ids_list = ids_list + "\"" + str(id_) + "\", "
                ids_list = ids_list[:-2]
                c_coll.execute("""SELECT id_card, comment FROM collection WHERE id_card IN (""" + ids_list + """)""")
                reponses_coll = c_coll.fetchall()
                
                dict_responses_coll = {}
                for card_coll in reponses_coll:
                        id_card, comment = card_coll
                        try:
                                dict_responses_coll[id_card]
                        except KeyError:
                                if comment != "":
                                        dict_responses_coll[id_card] = [1, True]
                                else:
                                        dict_responses_coll[id_card] = [1, False]
                        else:
                                if dict_responses_coll[id_card][1]:
                                        dict_responses_coll[id_card] = [dict_responses_coll[id_card][0] + 1, True]
                                else:
                                        if comment != "":
                                                dict_responses_coll[id_card] = [dict_responses_coll[id_card][0] + 1, True]
                                        else:
                                                dict_responses_coll[id_card] = [dict_responses_coll[id_card][0] + 1, False]
                
                for id_deleted in cards_to_delete.values():
                        if id_deleted not in dict_responses_coll.keys():
                                dict_responses_coll[id_deleted] = [0, False]
                
                rows_to_delete = []
                rows_to_delete_search = []
                for i, row in enumerate(self.mainstore):
                        try:
                                q, bold = dict_responses_coll[row[0]]
                        except KeyError:
                                pass
                        else:
                                if q == 0:
                                        rows_to_delete.append(i)
                                else:
                                        if bold:
                                                self.mainstore[i][12] = 700
                                        else:
                                                self.mainstore[i][12] = 400
                                        self.mainstore[i][15] = q
                        
                if self.tree_coll.get_model() == self.searchstore:
                        for i, row in enumerate(self.searchstore):
                                try:
                                        q, bold = dict_responses_coll[row[0]]
                                except KeyError:
                                        pass
                                else:
                                        if q == 0:
                                                rows_to_delete_search.append(i)
                                        else:
                                                if bold:
                                                        self.searchstore[i][12] = 700
                                                else:
                                                        self.searchstore[i][12] = 400
                                                self.searchstore[i][15] = q
                
                for nb_row in reversed(rows_to_delete):
                        del(self.mainstore[nb_row])
                for nb_row in reversed(rows_to_delete_search):
                        del(self.searchstore[nb_row])
                
                c_coll.execute("""SELECT COUNT(*) FROM collection""")
                count_nb = c_coll.fetchone()[0]
                if count_nb == 1:
                        self.label_nb_card_coll.set_text(defs.STRINGS["nb_card_coll"].replace("%%%", str(count_nb)))
                else:
                        self.label_nb_card_coll.set_text(defs.STRINGS["nb_card_coll_s"].replace("%%%", str(count_nb)))
                
                functions.collection.disconnect_db(conn_coll)
                functions.various.lock_db(False, None)
        
        def update_details(self, cards_to_update, new_id_db_to_bold, new_id_db_to_unbold):
                '''We update the details of the cards in 'cards_to_update'. 'new_id_db_to_bold' and 'new_id_db_to_unbold' can be lists of ids or "auto".'''
                conn_coll, c_coll = functions.collection.connect_db()
                functions.various.lock_db(True, None)
                
                #print(cards_to_update)
                for id_coll, new_data in cards_to_update.items():
                        condition, lang, foil, loaned, comment = new_data
                        c_coll.execute("""UPDATE collection SET condition = ?, lang = ?, foil = ?, loaned_to = ?, comment = ? WHERE id_coll = ?""", (condition, lang, foil, loaned, comment, id_coll,))
                
                functions.collection.disconnect_db(conn_coll)
                functions.various.lock_db(False, None)
                
                # we need to update the treeview of the collection and of the search
                if new_id_db_to_bold == "auto" and new_id_db_to_unbold == "auto":
                        new_id_db_to_bold = []
                        new_id_db_to_unbold = []
                        # we need to find the ids_db of all current ids_coll
                        ids_list = ""
                        for id_ in cards_to_update:
                                ids_list = ids_list + "\"" + id_ + "\", "
                        ids_list = ids_list[:-2]
                        conn, c = functions.collection.connect_db()
                        c.execute("""SELECT id_card, comment FROM collection WHERE id_coll IN (""" + ids_list + """)""")
                        reponses_coll = c.fetchall()
                        disconnect_db(conn)
                        
                        dict_responses_coll = {}
                        for card_coll in reponses_coll:
                                id_card, comment = card_coll
                                try:
                                        dict_responses_coll[id_card]
                                except KeyError:
                                        if comment != "":
                                                dict_responses_coll[id_card] = True
                                        else:
                                                dict_responses_coll[id_card] = False
                                else:
                                        if dict_responses_coll[id_card]:
                                                pass
                                        else:
                                                if comment != "":
                                                        dict_responses_coll[id_card] = True
                        for id_db, bold in dict_responses_coll.items():
                                if bold:
                                        new_id_db_to_bold.append(id_db)
                                else:
                                        new_id_db_to_unbold.append(id_db)
                
                if new_id_db_to_bold != [] or new_id_db_to_unbold != []:
                        for i, row in enumerate(self.mainstore):
                                if row[0] in new_id_db_to_bold:
                                        self.mainstore[i][12] = 700
                                if row[0] in new_id_db_to_unbold:
                                        self.mainstore[i][12] = 400
                        if self.tree_coll.get_model() == self.searchstore:
                                for i, row in enumerate(self.searchstore):
                                        if row[0] in new_id_db_to_bold:
                                                self.searchstore[i][12] = 700
                                        if row[0] in new_id_db_to_unbold:
                                                self.searchstore[i][12] = 400
        
        def show_details(self, treeview, treepath, column, selection, button_show_details):
                button_show_details.emit("clicked")
        
        def send_id_to_loader_with_selectinfo(self, selection, integer, TreeViewColumn, simple_search, selectinfo_button, button_show_details, button_change_quantity, button_add_deck):
                self.send_id_to_loader(selection, integer, TreeViewColumn, simple_search)
                model, pathlist = selection.get_selected_rows()
                label_selectinfo = selectinfo_button.get_child()
                if pathlist == []:
                        label_selectinfo.set_text(defs.STRINGS["info_select_none_coll"])
                        selectinfo_button.set_sensitive(False)
                        button_show_details.set_sensitive(False)
                        button_change_quantity.set_sensitive(False)
                        button_add_deck.set_sensitive(False)
                elif len(pathlist) == 1:
                        label_selectinfo.set_text(defs.STRINGS["info_select_coll"])
                        selectinfo_button.set_sensitive(True)
                        button_show_details.set_sensitive(True)
                        button_show_details.set_popover(functions.collection.gen_details_popover(button_show_details, selection))
                        button_change_quantity.set_sensitive(True)
                        button_change_quantity.set_popover(functions.collection.gen_quantity_popover(button_change_quantity, selection))
                        
                        cards_avail = {}
                        nb_avail = 0
                        details_store = functions.collection.gen_details_store(selection)
                        for card in details_store:
                                #id_coll, name, editionln, nameforeign, date, condition, lang, foil, loaned_to, comment, deck, bold, italic, id_db
                                if card[10] == "":
                                        try:
                                                cards_avail[card[13]]
                                        except KeyError:
                                                cards_avail[card[13]] = [card[0]]
                                        else:
                                                cards_avail[card[13]].append(card[0])
                                        nb_avail += 1
                                
                        if nb_avail > 0:
                                button_add_deck.set_sensitive(True)
                                button_add_deck.set_popover(functions.collection.gen_add_deck_popover(button_add_deck, selection))
                        else:
                                button_add_deck.set_sensitive(False)
                else:
                        label_selectinfo.set_text(defs.STRINGS["info_selects_coll"].replace("%%%", str(len(pathlist))))
                        #FIXME: generating and closing the popover when many many rows are selected is slow and can freeze MC (??!!), so we limit to 500
                        if len(pathlist) < 501:
                                selectinfo_button.set_sensitive(True)
                        else:
                                selectinfo_button.set_sensitive(False)
                        
                        button_show_details.set_sensitive(True)
                        button_show_details.set_popover(functions.collection.gen_details_popover(button_show_details, selection))
                        button_change_quantity.set_sensitive(False)
                        button_add_deck.set_sensitive(False)
                        #button_add_deck.set_popover(functions.collection.gen_add_deck_popover(button_add_deck, selection, details_store))
                
        def selectinfo_click(self, selectinfo_button, selection, popover):                
                def checkbutton_toggled(checkbutton, path, selection):
                        if checkbutton.get_active():
                                selection.select_path(path)
                        else:
                                selection.unselect_path(path)
                
                if selectinfo_button.get_active():
                        model, pathlist = selection.get_selected_rows()
                        if pathlist != []:
                                column_name = 1
                                if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                                        lang_foreign = functions.config.read_config("fr_language")
                                        if lang_foreign == defs.LANGUAGE:
                                                # we choose the foreign name
                                                column_name = 3
                                
                                for widget in popover.get_children():
                                        popover.remove(widget)
                                
                                popover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                                popover_box.set_margin_top(5)
                                popover_box.set_margin_bottom(5)
                                popover_box.set_margin_left(5)
                                popover_box.set_margin_right(5)
                                box_names = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                                
                                if len(pathlist) > 5:
                                        scrolledwindow = Gtk.ScrolledWindow()
                                        scrolledwindow.set_min_content_height(150)
                                        scrolledwindow.set_min_content_width(400)
                                        scrolledwindow.add_with_viewport(box_names)
                                
                                for path in pathlist:
                                        tree_iter = model.get_iter(path)
                                        name = model.get_value(tree_iter, column_name) + " (" + model.get_value(tree_iter, 2) + ")"
                                        
                                        if len(pathlist) > 1:
                                                checkbutton = Gtk.CheckButton("")
                                                checkbutton.set_active(True)
                                                checkbutton.connect("toggled", checkbutton_toggled, path, selection)
                                                for widget in checkbutton.get_children():
                                                        if widget.__class__.__name__ == "Label":
                                                                widget.set_markup("<b>" + name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</b>")
                                                                widget.set_max_width_chars(70)
                                                                widget.set_line_wrap(True)
                                                                widget.set_lines(3)
                                                                widget.set_ellipsize(Pango.EllipsizeMode.END)
                                                                widget.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                                                                widget.set_alignment(0.0, 0.5)
                                                                break
                                                
                                                box_names.pack_start(checkbutton, True, True, 0)
                                        
                                        else:
                                                label_name = Gtk.Label()
                                                label_name.set_markup("<b>" + name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</b>")
                                                label_name.set_max_width_chars(70)
                                                label_name.set_line_wrap(True)
                                                label_name.set_lines(3)
                                                label_name.set_ellipsize(Pango.EllipsizeMode.END)
                                                label_name.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                                                label_name.set_alignment(0.0, 0.5)
                                        
                                                box_names.pack_start(label_name, True, True, 0)
                                
                                if len(pathlist) > 5:
                                        popover_box.pack_start(scrolledwindow, True, True, 0)
                                else:
                                        popover_box.pack_start(box_names, True, True, 0)
                                popover.add(popover_box)
                                popover_box.show_all()
        
        def send_id_to_loader(self, selection, integer, TreeViewColumn, simple_search):
                model, pathlist = selection.get_selected_rows()
                if pathlist != []:
                        tree_iter = model.get_iter(pathlist[0])
                        id_ = model.get_value(tree_iter, 0)
                        self.load_card(id_, simple_search)
        
        def load_card(self, cardid, simple_search):
                '''Load a card in the card viewer'''
                #GLib.idle_add(functions.cardviewer.gen_card_viewer, cardid, self.card_viewer, self, simple_search)
                functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
        
        def load_card_from_outside(self, widget_orig, cardid, list_widgets_to_destroy, simple_search):
                #GLib.idle_add(functions.cardviewer.gen_card_viewer, cardid, self.card_viewer, self, simple_search)
                functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
