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
                
                self.mainbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
                self.mainbox.set_margin_top(5)
                self.mainbox.set_margin_bottom(5)
                self.mainbox.set_margin_left(5)
                self.mainbox.set_margin_right(5)
                
                mainwindow.main_stack.add_titled(self.mainbox, "collection", defs.STRINGS["collection"])
                
                self.card_viewer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
                self.right_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                self.mainbox.pack_start(self.card_viewer, False, False, 0)
                self.mainbox.pack_start(separator, False, False, 0)
                self.mainbox.pack_start(self.right_content, True, True, 0)
                
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
                        
                        po = 0
                        for nb_row in rows_to_select:
                                if po == 0:
                                        self.tree_coll.set_cursor(nb_row)
                                self.select.select_path(nb_row) # FIXME: this freezes GTK when selecting rows, why ??
                                po += 1
                
                try:
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
                
                cards_list2 = list(cards_list)
                
                for enum, card_to_add in enumerate(cards_list):
                        cardid, condition, lang, foil, loaned_to, comment, nb = card_to_add
                        # we need : name, nb_variante, edition
                        card_found = 0
                        for reponse in reponse_all:
                                if str(reponse[0]) == str(cardid):
                                        card_found = 1
                                        break
                        
                        if card_found == 0:
                                print("Something is wrong in the universe. In fact, only in the database but...")
                        else:
                                id_, name, nb_variante, names, edition_code, name_chinesetrad, name_chinesesimp, name_french, name_german, name_italian, name_japanese, name_korean, name_portuguesebrazil, name_portuguese, name_russian, name_spanish, colors, manacost, cmc, multiverseid, imageurl, type_, artist, text, flavor, power, toughness, loyalty, rarity, layout, number, variations = reponse
                                
                                current_unique_name = functions.various.get_unique_name(name, nb_variante, edition_code)
                                cards_list2[enum].append(current_unique_name)
                                
                                # the current date
                                today = date.today()
                                month = '%02d' % today.month
                                day = '%02d' % today.day
                                current_date = str(today.year) + "-" + str(month) + "-" + str(day)
                                
                                for z in range(nb):
                                        # we add the card to the collection DB
                                        c_coll.execute("""
                                        INSERT INTO collection VALUES(null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (name, nb_variante, edition_code, current_date, condition, lang, foil, loaned_to, comment, ""))
                                
                                # we update the collection store / treeview
                                i = 0
                                card_added = 0
                                if self.mainstore == None:
                                        conn_coll.commit()
                                        #GLib.idle_add(functions.collection.read_coll, self.right_content, self)
                                        functions.collection.read_coll(self.right_content, self)
                                        cards = functions.various.prepare_cards_data_for_treeview([reponse])
                                        for card in cards.values():
                                                cards_data_for_update_store_as.append([card["name"], card["edition_ln"]])
                                else:
                                        try:
                                                GLib.idle_add(self.label_nb_card_coll.set_text, defs.STRINGS["nb_card_coll_s"].replace("%%%", "--"))
                                        except:
                                                pass
                                        for row in self.mainstore:
                                                unique_name = row[16]
                                                if current_unique_name == unique_name:
                                                        # another card like us is in the collection => curent nb + nb
                                                        self.mainstore[i][15] = str(int(self.mainstore[i][15]) + int(nb))
                                                        if comment != "":
                                                                # we need to italic the row
                                                                self.mainstore[i][13] = Pango.Style.ITALIC
                                                        card_added = 1
                                                i += 1
                                        
                                        if card_added == 0:
                                                # we need to add a new row
                                                cards = functions.various.prepare_cards_data_for_treeview([reponse])
                                                for card in cards.values():
                                                        italic = Pango.Style.NORMAL
                                                        if comment != "":
                                                                italic = Pango.Style.ITALIC
                                                        bold = 400
                                                        unique_name = current_unique_name
                                                        self.mainstore.insert_with_valuesv(-1, range(17), [card["id_"], card["name"], card["edition_ln"], card["nameforeign"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold, italic, card["nb_variant"], nb, unique_name])
                                                        cards_data_for_update_store_as.append([card["name"], card["edition_ln"]])
                                
                if cards_data_for_update_store_as != []:
                        GLib.idle_add(defs.MAINWINDOW.advancedsearch.update_current_store_bold, cards_data_for_update_store_as)
                
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
                        for new_card in cards_list2:
                                if new_card[7] == row[16]:
                                        rows_to_select.append(nb_row)
                GLib.idle_add(select_rows, rows_to_select)
                
                functions.collection.disconnect_db(conn_coll)
                defs.COLL_LOCK = False
                if defs.BUTTON_COLL_LOCK != None:
                        GLib.idle_add(defs.BUTTON_COLL_LOCK.set_label, defs.STRINGS["add_button_validate"])
                        GLib.idle_add(defs.BUTTON_COLL_LOCK.set_sensitive, True)
                
                if spinner_labels != None:
                        GLib.idle_add(spinner_labels.destroy)
        
        def send_id_to_loader_with_selectinfo(self, selection, integer, TreeViewColumn, simple_search, selectinfo_button):
                self.send_id_to_loader(selection, integer, TreeViewColumn, simple_search)
                model, pathlist = selection.get_selected_rows()
                label_selectinfo = selectinfo_button.get_child()
                if pathlist == []:
                        label_selectinfo.set_text(defs.STRINGS["info_select_none_coll"])
                        selectinfo_button.set_sensitive(False)
                elif len(pathlist) == 1:
                        label_selectinfo.set_text(defs.STRINGS["info_select_coll"])
                        selectinfo_button.set_sensitive(True)
                else:
                        label_selectinfo.set_text(defs.STRINGS["info_selects_coll"].replace("%%%", str(len(pathlist))))
                        #FIXME: generating and closing the popover when many many rows are selected is slow and can freeze MC (??!!), so we limit to 500
                        if len(pathlist) < 501:
                                selectinfo_button.set_sensitive(True)
                        else:
                                selectinfo_button.set_sensitive(False)
                
        def selectinfo_click(self, selectinfo_button, selection, popover):                
                if selectinfo_button.get_active():
                        model, pathlist = selection.get_selected_rows()
                        if pathlist != []:
                                column_name = 1
                                if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                                        lang_foreign = functions.config.read_config("fr_language")
                                        if lang_foreign == defs.LANGUAGE:
                                                # we choose the foreign name
                                                column_name = 3
                                
                                '''popover = Gtk.Popover.new(selectinfo_button)
                                popover.set_position(Gtk.PositionType.BOTTOM)
                                selectinfo_button.set_popover(popover)'''
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
                                #popover.show_all()
        
        def send_id_to_loader(self, selection, integer, TreeViewColumn, simple_search):
                model, pathlist = selection.get_selected_rows()
                if pathlist != []:
                        tree_iter = model.get_iter(pathlist[0])
                        id_ = model.get_value(tree_iter, 0)
                        self.load_card(id_, simple_search)
        
        def load_card(self, cardid, simple_search):
                '''Load a card in the card viewer'''
                functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
        
        def load_card_from_outside(self, widget_orig, cardid, list_widgets_to_destroy, simple_search):
                for widget in list_widgets_to_destroy:
                        widget.destroy()
                functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
