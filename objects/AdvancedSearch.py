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

# AdvancedSearch class for Magic Collection

from gi.repository import Gtk, Gio, GdkPixbuf, GLib, Pango
import sys
import os
import threading
import time

# imports def.py
import defs
# imports objects
import objects.mc
# imports functions
import functions.cardviewer
import functions.config
import functions.db
import functions.collection

class AdvancedSearch:
        '''The AdvancedSearch class. Manages the AdvancedSearch part of MC.'''
        def __init__(self, mainwindow):
                self.mainstore = None
                self.mainselect = None
                
                self.mainbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
                self.mainbox.set_margin_top(5)
                self.mainbox.set_margin_bottom(5)
                self.mainbox.set_margin_left(5)
                self.mainbox.set_margin_right(5)
                
                self.list_entrycompletion_editions = []
                
                mainwindow.main_stack.add_titled(self.mainbox, "advancedsearch", defs.STRINGS["advancedsearch"])
                
                self.card_viewer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
                right_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                self.mainbox.pack_start(self.card_viewer, False, False, 0)
                self.mainbox.pack_start(separator, False, False, 0)
                self.mainbox.pack_start(right_content, True, True, 0)
                
                right_content_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                right_content_mid = Gtk.ButtonBox(Gtk.Orientation.HORIZONTAL)
                right_content_mid.set_layout(Gtk.ButtonBoxStyle.START)
                right_content_mid.set_spacing(4)
                
                overlay_right_content_bot = Gtk.Overlay()
                right_content_bot = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                overlay_right_content_bot.add(right_content_bot)
                right_content_bot.set_size_request(560, 200)
                self.box_results = right_content_bot
                
                right_content.pack_start(right_content_top, False, True, 0)
                right_content.pack_start(right_content_mid, False, False, 0)
                right_content.pack_start(overlay_right_content_bot, True, True, 0)
                
                right_content_top_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                right_content_top_right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                
                right_content_top.pack_start(right_content_top_left, True, True, 0)
                right_content_top.pack_start(right_content_top_right, False, False, 0)
                
                # we list each edition in this treeview
                scrolledwindow = Gtk.ScrolledWindow()
                scrolledwindow.set_min_content_width(300)
                scrolledwindow.set_min_content_height(150)
                scrolledwindow.set_hexpand(True)
                scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
                store_editions = Gtk.ListStore(str, str, str, str, str, str)
                tree_editions = Gtk.TreeView(store_editions)
                tree_editions.set_enable_search(False)
                renderer_editions = Gtk.CellRendererText()
                
                ordretrie = functions.config.read_config("ext_sort_as")
                
                if ordretrie == "0":
                        nb_column = 3
                        sort = Gtk.SortType.DESCENDING
                else:
                        nb_column = 0
                        sort = Gtk.SortType.ASCENDING
                column_name_editions = Gtk.TreeViewColumn(defs.STRINGS["list_editions"], renderer_editions, text=0)
                column_name_editions.set_sort_column_id(nb_column)
                store_editions.set_sort_column_id(nb_column, sort)
                tree_editions.append_column(column_name_editions)
                
                select = tree_editions.get_selection()
                
                self.label_nb_cards = Gtk.Label()
                self.icon_edition = Gtk.Image()
                
                self.button_show_details = Gtk.MenuButton()
                self.button_show_details.set_tooltip_text(defs.STRINGS["show_details_tooltip"])
                image_button_show_details = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="text-editor-symbolic"), Gtk.IconSize.BUTTON)
                image_button_show_details.show()
                self.button_show_details.add(image_button_show_details)
                self.button_show_details.set_sensitive(False)
                
                select.connect("changed", self.edition_selected, "blip", "blop", tree_editions, self.button_show_details)
                scrolledwindow.add(tree_editions)
                self.store_editions = store_editions
                self.gen_list_editions()
                
                tree_editions.show_all()
                scrolledwindow.show_all()
                
                right_content_top_left.pack_start(scrolledwindow, False, True, 0)
                
                right_content_top_left_bot = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                right_content_top_left.pack_start(right_content_top_left_bot, False, False, 0)
                
                # for the advanced search
                grid = Gtk.Grid()
                grid.set_row_spacing(6)
                grid.set_column_spacing(4)
                
                comboboxtext1 = Gtk.ComboBoxText()
                self.comboboxtext1 = comboboxtext1
                comboboxtext2 = Gtk.ComboBoxText()
                comboboxtext3 = Gtk.ComboBoxText()
                comboboxtext4 = Gtk.ComboBoxText()
                for comboboxtext in [comboboxtext1, comboboxtext2, comboboxtext3, comboboxtext4]:
                        for i in range(len(defs.SEARCH_ITEMS)):
                                if i < 13:
                                        comboboxtext.append(defs.SEARCH_ITEMS[i][0], defs.SEARCH_ITEMS[i][1])
                
                entry1 = Gtk.Entry()
                self.entry1 = entry1
                entry2 = Gtk.Entry()
                entry3 = Gtk.Entry()
                entry4 = Gtk.Entry()
                
                # name
                comboboxtext1.set_active(0)
                comboboxtext1.connect("changed", self.comboboxtext_changed, entry1)
                # type
                comboboxtext2.set_active(2)
                comboboxtext2.connect("changed", self.comboboxtext_changed, entry2)
                # edition
                comboboxtext3.set_active(1)
                comboboxtext3.connect("changed", self.comboboxtext_changed, entry3)
                entry3.set_completion(functions.various.gen_entrycompletion_editions(self))
                # color
                comboboxtext4.set_active(3)
                comboboxtext4.connect("changed", self.comboboxtext_changed, entry4)
                
                self.button_reset_search = Gtk.Button()
                self.button_search = Gtk.Button(defs.STRINGS["search_ad"])
                
                for entry in [entry1, entry2, entry3, entry4]:
                        icon_search = Gio.ThemedIcon(name="edit-find-symbolic")
                        entry.set_icon_from_gicon(Gtk.EntryIconPosition.SECONDARY, icon_search)
                        entry.set_icon_sensitive(Gtk.EntryIconPosition.SECONDARY, False)
                        entry.set_size_request(230, -1)
                        entry.connect("icon-press", self.entry_operator_choice)
                        entry.connect("activate", self.prepare_request, [[entry1, comboboxtext1], [entry2, comboboxtext2], [entry3, comboboxtext3], [entry4, comboboxtext4]], overlay_right_content_bot, select)
                        entry.connect("changed", self.update_button_search_and_reset, entry1, entry2, entry3, entry4)
                
                grid.attach(comboboxtext1, 1, 1, 1, 1)
                grid.attach_next_to(comboboxtext2, comboboxtext1, Gtk.PositionType.BOTTOM, 1, 1)
                grid.attach_next_to(comboboxtext3, comboboxtext2, Gtk.PositionType.BOTTOM, 1, 1)
                grid.attach_next_to(comboboxtext4, comboboxtext3, Gtk.PositionType.BOTTOM, 1, 1)
                grid.attach_next_to(entry1, comboboxtext1, Gtk.PositionType.RIGHT, 1, 1)
                grid.attach_next_to(entry2, comboboxtext2, Gtk.PositionType.RIGHT, 1, 1)
                grid.attach_next_to(entry3, comboboxtext3, Gtk.PositionType.RIGHT, 1, 1)
                grid.attach_next_to(entry4, comboboxtext4, Gtk.PositionType.RIGHT, 1, 1)
                grid.show_all()
                right_content_top_right.pack_start(grid, False, False, 0)
                
                # the label for the number of cards found
                right_content_mid.add(self.icon_edition)
                right_content_mid.add(self.label_nb_cards)
                right_content_mid.set_child_non_homogeneous(self.icon_edition, True)
                right_content_mid.set_child_non_homogeneous(self.label_nb_cards, True)
                
                right_content_mid.add(self.button_show_details)
                
                self.button_reset_search.set_sensitive(False)
                button_reset_search_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="edit-clear-all-symbolic"), Gtk.IconSize.BUTTON)
                self.button_reset_search.add(button_reset_search_pic)
                self.button_reset_search.connect("clicked", self.reset_search, entry1, entry2, entry3, entry4)
                right_content_mid.add(self.button_reset_search)
                right_content_mid.set_child_non_homogeneous(self.button_reset_search, True)
                
                self.button_search.set_sensitive(False)
                self.button_search.connect("clicked", self.prepare_request, [[entry1, comboboxtext1], [entry2, comboboxtext2], [entry3, comboboxtext3], [entry4, comboboxtext4]], overlay_right_content_bot, select)
                right_content_mid.add(self.button_search)
                
                right_content_mid.set_child_secondary(self.button_show_details, True)
                right_content_mid.set_child_secondary(self.button_reset_search, True)
                right_content_mid.set_child_secondary(self.button_search, True)
                
                self.sens_widgets = [entry1, entry2, entry3, entry4, scrolledwindow, self.button_search]
                
                conn, c = functions.db.connect_db()
                c.execute("""SELECT Count(*) FROM cards""")
                reponse = c.fetchone()
                functions.db.disconnect_db(conn)
                label_cards_in_db = Gtk.Label()
                label_cards_in_db.set_markup("<big>" + defs.STRINGS["nb_cards_in_db"].replace("%%%", str(reponse[0])) + "</big>")
                label_cards_in_db.props.halign = Gtk.Align.CENTER
                right_content_bot.pack_start(label_cards_in_db, True, True, 0)
                
                # we load nothing in the card viewer
                self.load_card(None, 0)
                
                self.mainbox.show_all()
        
        def update_button_search_and_reset(self, entry, entry1, entry2, entry3, entry4):
                """Resets the entries.
                
                """
                
                text_in_entry = 0
                for widget in [entry1, entry2, entry3, entry4]:
                        if widget.get_text() != "":
                                text_in_entry = 1
                
                if text_in_entry == 0:
                        sensitive = False
                else:
                        sensitive = True
                self.button_search.set_sensitive(sensitive)
                self.button_reset_search.set_sensitive(sensitive)
        
        def update_current_store_bold(self, cards_data_for_update_store_as):
                """Updates the mainstore about cards in the collection.
                
                """
                
                if self.mainstore != None:
                        i = 0
                        for row in self.mainstore:
                                for card in cards_data_for_update_store_as:
                                        if row[1] == card[0] and row[2] == card[1]:
                                                self.mainstore[i][12] = 700
                                i += 1
                        self.mainselect.emit("changed")
        
        def empty_box_results(self):
                """Empties the results' box.
                
                """
                
                for widget in self.box_results.get_children():
                        self.box_results.remove(widget)
        
        def launch_ad_search(self, request, type_s, wait_button):
                """Launches an advanced search with 'request'.
                
                """
                
                conn, c = functions.db.connect_db()
                c.execute(request)
                reponses = c.fetchall()
                functions.db.disconnect_db(conn)
                defs.MEM_SEARCHS[request] = reponses
                self.disp_result(reponses, type_s, wait_button)
        
        def disp_result(self, reponses, type_s, wait_button):
                """Displays the result with GLib.idle_add.
                
                """
                
                GLib.idle_add(self.disp_result2, reponses, type_s, wait_button)
        
        def disp_result2(self, reponses, type_s, wait_button):
                """Displays the result.
                
                """
                
                def insert_data(store_results, cards_added, card, bold, italic):
                        store_results.insert_with_valuesv(-1, range(15), [card["id_"], card["name"], card["edition_ln"], card["nameforeign"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold, italic])
                        cards_added.append(card["name"] + "-" + card["nb_variant"] + "-" + card["edition_ln"])
                        functions.various.force_update_gui(0)
                
                def _start(AS_object, store_results, scrolledwindow):
                        AS_object.label_nb_cards.set_text("")
                        AS_object.button_show_details.set_sensitive(False)
                        # we create the treeview for displaying results
                        scrolledwindow.set_min_content_width(560)
                        scrolledwindow.set_min_content_height(180)
                        scrolledwindow.set_hexpand(True)
                        scrolledwindow.set_vexpand(True)
                        scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
                        tree_results = Gtk.TreeView(store_results)
                        tree_results.set_enable_search(False)
                        
                        # some work with columns
                        columns_to_display = functions.config.read_config("as_columns").split(";")
                        
                        AS_object.as_columns_list = functions.various.gen_treeview_columns(columns_to_display, tree_results)[0]
                        
                        select = tree_results.get_selection()
                        select.set_mode(Gtk.SelectionMode.MULTIPLE)
                        select.connect("changed", AS_object.send_id_to_loader, "blip", "blop", 0)
                        AS_object.mainselect = select
                        scrolledwindow.add(tree_results)
                        AS_object.mainstore = store_results
                        if defs.OS == "mac":
                                AS_object.mainstore.set_sort_func(3, functions.various.compare_str_osx, None)
                        AS_object.mainstore.set_sort_func(9, functions.various.compare_str_and_int, None)
                        AS_object.mainstore.set_sort_func(10, functions.various.compare_str_and_int, None)
                        
                        tree_results.connect("row-activated", self.show_details, select, self.button_show_details)
                        
                        AS_object.box_results.pack_start(scrolledwindow, True, True, 0)
                
                def _end(store_results, wait_button):
                        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                                store_results.set_sort_column_id(3, Gtk.SortType.ASCENDING)
                        else:
                                store_results.set_sort_column_id(1, Gtk.SortType.ASCENDING)
                        
                        if wait_button != None:
                                wait_button.destroy()
                
                def _no_result(AS_object, wait_button):
                        if wait_button != None:
                                wait_button.destroy()
                        
                        AS_object.label_nb_cards.set_text("")
                        label_result = Gtk.Label()
                        label_result.set_markup("<big>" + defs.STRINGS["no_result"] + "</big>")
                        label_result.set_line_wrap(True)
                        label_result.set_ellipsize(Pango.EllipsizeMode.END)
                        label_result.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                        label_result.show()
                        AS_object.box_results.pack_start(label_result, True, True, 0)
                
                self.empty_box_results()
                if len(reponses) > 0:                
                        if len(reponses) > 5000: 
                                label_wait = Gtk.Label()
                                label_wait.set_markup("<big>" + defs.STRINGS["please_wait"] + "</big>")
                                wait_button.pack_start(label_wait, True, True, 0)
                                time.sleep(4)
                                label_wait.show()
                                functions.various.force_update_gui(0)
                                       
                        scrolledwindow = Gtk.ScrolledWindow()
                        # "id", "name", "edition", "name_foreign", "colors", colors_pixbuf, "cmc", "type", "artist", "power", "toughness", "rarity", "bold", "italic"
                        store_results = Gtk.ListStore(str, str, str, str, str, GdkPixbuf.Pixbuf, int, str, str, str, str, str, int, Pango.Style)
                        _start(self, store_results, scrolledwindow)
                        cards_added = []
                        
                        cards = functions.various.prepare_cards_data_for_treeview(reponses)
                        
                        # we get a list of ids of cards in the collection
                        conn, c = functions.collection.connect_tmp_coll_with_sdf()
                        c.execute("""SELECT id_card FROM collection""")
                        reponses_coll = c.fetchall()
                        functions.collection.disconnect_db(conn)
                        
                        no_reprints = functions.config.read_config("no_reprints")
                        # if the user doesn't want reprints, we delete every reprint but the most recent
                        if no_reprints == "1":
                                if type_s != "edition":
                                        cards_added_reprints = {}
                                        
                                        for card in dict(cards).values():
                                                unique_name = card["name"] + "-" + card["nb_variant"] + "-" + card["type_"] + "-" + card["text"] + "-" + card["power"] + "-" + card["toughness"] + "-" + card["colors"]
                                                try:
                                                        cards_added_reprints[unique_name]
                                                except KeyError:
                                                        # first print of this card
                                                        cards_added_reprints[unique_name] = card["id_"]
                                                else:
                                                        # it's not the first print of this card
                                                        try:
                                                                current_release_date = int(card["release_date"])
                                                        except ValueError:
                                                                current_release_date = 0
                                                        try:
                                                                print_in_cards_added_reprints_release_date = int(cards[cards_added_reprints[unique_name]]["release_date"])
                                                        except ValueError:
                                                                print_in_cards_added_reprints_release_date = 0
                                                        
                                                        if current_release_date > print_in_cards_added_reprints_release_date:
                                                                # current print is more recent
                                                                del(cards[cards_added_reprints[unique_name]])
                                                                cards_added_reprints[unique_name] = card["id_"]
                                                        else:
                                                                # current print is older
                                                                del(cards[card["id_"]])
                        
                        nb_lines_added = 0
                        
                        for card in cards.values():
                                # if this card is in the collection, we bolding it
                                bold = 400
                                for row_id_card in reponses_coll:
                                        id_card = row_id_card[0]
                                        if id_card == card["id_"]:
                                                bold = 700
                                                break
                                
                                italic = Pango.Style.NORMAL
                                
                                add = True
                                
                                if type_s == "edition":
                                        if card["layout"] == "flip" or card["layout"] == "double-faced" or card["layout"] == "meld":
                                                names = card["names"].split("|")
                                                if card["layout"] == "meld":
                                                        if card["real_name"] == names[2]:
                                                                add = False
                                                if card["layout"] != "meld":
                                                        if card["real_name"] != names[0]:
                                                                add = False
                                
                                '''if card["layout"] == "split":
                                        names = card["names"].split("|")
                                        if card["real_name"] != names[0]:
                                                add = False'''
                                
                                if card["name"] + "-" + card["nb_variant"] + "-" + card["edition_ln"] in cards_added:
                                        add = False
                                
                                if add:
                                        nb_lines_added += 1
                                        insert_data(store_results, cards_added, card, bold, italic)
                        
                        _end(store_results, wait_button)
                        
                        if type_s == "edition":
                                if nb_lines_added > 1:
                                        self.label_nb_cards.set_text(str(nb_lines_added) + " " + defs.STRINGS["cards"])
                                else:
                                        self.label_nb_cards.set_text(str(nb_lines_added) + " " + defs.STRINGS["card"])
                        else:
                                if nb_lines_added > 1:
                                        self.label_nb_cards.set_text(str(nb_lines_added) + " " + defs.STRINGS["cards_result"])
                                else:
                                        self.label_nb_cards.set_text(str(nb_lines_added) + " " + defs.STRINGS["card_result"])
                        
                        scrolledwindow.show_all()
                else:
                        _no_result(self, wait_button)
                functions.various.lock_db(None, False)
        
        def prepare_request(self, widget, search_widgets_list, overlay_right_content_bot, select):
                """Prepares the request to the database.
                
                """
                
                if defs.AS_LOCK == False:
                        request = functions.db.prepare_request(search_widgets_list, "db")[0]
                        if request != None:
                                select.unselect_all()
                                functions.various.lock_db(None, True)
                                GLib.idle_add(self.icon_edition.set_from_gicon, Gio.ThemedIcon(name="edit-find-symbolic"), Gtk.IconSize.BUTTON)
                                GLib.idle_add(self.empty_box_results)
                                
                                wait_button = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                                wait_button.props.valign = Gtk.Align.CENTER
                                as_spinner = Gtk.Spinner()
                                as_spinner.set_size_request(30, 30)
                                wait_button.pack_start(as_spinner, True, True, 0)
                                as_spinner.start()
                                GLib.idle_add(wait_button.show_all)
                                GLib.idle_add(overlay_right_content_bot.add_overlay, wait_button)
                                
                                '''thread_time = threading.Thread(target = self.launch_thread_time, args = [wait_button])
                                thread_time.daemon = True
                                thread_time.start()'''
                                
                                try:
                                        prev_search = defs.MEM_SEARCHS[request]
                                except KeyError:
                                        thread = threading.Thread(target = self.launch_ad_search, args = (request, "", wait_button))
                                        thread.daemon = True
                                        thread.start()
                                else:
                                        self.empty_box_results()
                                        thread = threading.Thread(target = self.disp_result, args = (prev_search, "", wait_button))
                                        thread.daemon = True
                                        thread.start()
        
        def launch_thread_time(self, wait_button_box):
                label_wait = Gtk.Label()
                label_wait.set_markup("<big>" + defs.STRINGS["please_wait"] + "</big>")
                GLib.idle_add(wait_button_box.pack_start, label_wait, True, True, 0)
                time.sleep(4)
                GLib.idle_add(label_wait.show, priority=GLib.PRIORITY_HIGH_IDLE)
        
        def edition_selected(self, selection, integer, TreeViewColumn, tree_editions, button_show_details):
                """Displays the cards of the selected edition.
                
                """
                
                if defs.AS_LOCK == False:
                        model, treeiter = selection.get_selected()
                        if treeiter != None:
                                button_show_details.set_sensitive(False)
                                functions.various.lock_db(None, True)
                                ed_name = model[treeiter][0].replace('"', '""')
                                conn, c = functions.db.connect_db()
                                c.execute("""SELECT code FROM editions WHERE name = \"""" + ed_name + """\" OR name_french = \"""" + ed_name + """\"""")
                                reponse = c.fetchone()
                                functions.db.disconnect_db(conn)
                                request = """SELECT * FROM cards WHERE edition = \"""" + reponse[0] + """\""""
                                
                                if os.path.isfile(os.path.join(defs.CACHEMCPIC, "icons", functions.various.valid_filename_os(reponse[0]) + ".png")):
                                        GLib.idle_add(self.icon_edition.set_from_file, os.path.join(defs.CACHEMCPIC, "icons", functions.various.valid_filename_os(reponse[0]) + ".png"))
                                        GLib.idle_add(self.icon_edition.show)
                                else:
                                        GLib.idle_add(self.icon_edition.hide)
                                
                                try:
                                        prev_search = defs.MEM_SEARCHS[request]
                                except KeyError:
                                        thread = threading.Thread(target = self.launch_ad_search, args = (request, "edition", None))
                                        thread.daemon = True
                                        thread.start()
                                else:
                                        self.empty_box_results()
                                        thread = threading.Thread(target = self.disp_result, args = (prev_search, "edition", None))
                                        thread.daemon = True
                                        thread.start()
        
        def reset_search(self, button, entry1, entry2, entry3, entry4):
                """Resets the entries.
                
                """
                
                for entry in [entry1, entry2, entry3, entry4]:
                        entry.set_text("")
        
        def entry_operator_choice(self, entry, icon, void):
                """Displays data to the user when he selects a specific criteria.
                
                """
                
                popover = Gtk.Popover.new(entry)
                tooltip_text = entry.get_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY)
                
                button1 = Gtk.RadioButton.new_with_label_from_widget(None, defs.STRINGS["entry_eq_ad"])
                button1.connect("toggled", self.on_button_radio_op, "1", entry, popover)
                if tooltip_text == defs.STRINGS["entry_eq_ad"]:
                        button1.set_active(True)
                
                button2 = Gtk.RadioButton.new_from_widget(button1)
                button2.set_label(defs.STRINGS["entry_inf_eq_ad"])
                button2.connect("toggled", self.on_button_radio_op, "2", entry, popover)
                if tooltip_text == defs.STRINGS["entry_inf_eq_ad"]:
                        button2.set_active(True)
                
                button3 = Gtk.RadioButton.new_from_widget(button1)
                button3.set_label(defs.STRINGS["entry_sup_eq_ad"])
                button3.connect("toggled", self.on_button_radio_op, "3", entry, popover)
                if tooltip_text == defs.STRINGS["entry_sup_eq_ad"]:
                        button3.set_active(True)
                
                button4 = Gtk.RadioButton.new_from_widget(button1)
                button4.set_label(defs.STRINGS["entry_diff"])
                button4.connect("toggled", self.on_button_radio_op, "4", entry, popover)
                if tooltip_text == defs.STRINGS["entry_diff"]:
                        button4.set_active(True)
                
                box_popover = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                box_popover.pack_start(button1, False, False, 0)
                box_popover.pack_start(button2, False, False, 0)
                box_popover.pack_start(button3, False, False, 0)
                box_popover.pack_start(button4, False, False, 0)
                popover.add(box_popover)
                
                popover.show_all()
        
        def on_button_radio_op(self, button, name, entry, popover):
                """Changes the icons and the tooltip of the entry when the user selects a specific filter.
                
                """
                
                if button.get_active():
                        if name == "1":
                                entry.set_icon_from_gicon(Gtk.EntryIconPosition.PRIMARY, Gio.ThemedIcon(name="equal-symbolic"))
                                entry.set_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY, defs.STRINGS["entry_eq_ad"])
                        elif name == "2":
                                entry.set_icon_from_gicon(Gtk.EntryIconPosition.PRIMARY, Gio.ThemedIcon(name="inf_or_eq-symbolic"))
                                entry.set_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY, defs.STRINGS["entry_inf_eq_ad"])
                        elif name == "3":
                                entry.set_icon_from_gicon(Gtk.EntryIconPosition.PRIMARY, Gio.ThemedIcon(name="sup_or_eq-symbolic"))
                                entry.set_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY, defs.STRINGS["entry_sup_eq_ad"])
                        elif name == "4":
                                entry.set_icon_from_gicon(Gtk.EntryIconPosition.PRIMARY, Gio.ThemedIcon(name="different-symbolic"))
                                entry.set_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY, defs.STRINGS["entry_diff"])
        
        def comboboxtext_changed(self, comboboxtext, entry):
                """Displays data to the user when he selects a specific criteria.
                
                """
                
                search = ""
                for infosearch in defs.SEARCH_ITEMS.values():
                        if infosearch[1] == comboboxtext.get_active_text():
                                search = infosearch[0]
                                break
                if search == "cmc" or search == "power" or search == "toughness" or search == "loyalty" or search == "date" or search == "quantity_card" or search == "date":
                        entry.set_icon_from_gicon(Gtk.EntryIconPosition.PRIMARY, Gio.ThemedIcon(name="equal-symbolic"))
                        entry.set_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY, defs.STRINGS["entry_eq_ad"])
                else:
                        entry.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, None)
                
                # we add a placeholder for the date
                if search == "date":
                        entry.set_placeholder_text(defs.STRINGS["placeholder_date"])
                else:
                        entry.set_placeholder_text("")
                
                # we add a completion for the editions
                if search == "edition":
                        entry.set_completion(functions.various.gen_entrycompletion_editions(self))
                else:
                        entry.set_completion(None)
                
        def gen_list_editions(self):
                """Generates the list of the editions.
                
                """
                
                self.store_editions.clear()
                use_french_name = functions.config.read_config("ext_fr_name")
                
                conn, c = functions.db.connect_db()
                c.execute("""SELECT * FROM editions""")
                reponses = c.fetchall()
                for info_edition in reponses:
                        nom_fr_ou_en = info_edition[2]
                        if use_french_name == "1":
                                if info_edition[4] != "":
                                        nom_fr_ou_en = info_edition[4]
                        self.list_entrycompletion_editions.append(nom_fr_ou_en)
                        self.store_editions.append([nom_fr_ou_en, info_edition[1], info_edition[2], info_edition[3].replace("-", ""), info_edition[4], info_edition[5]])
                
                functions.db.disconnect_db(conn)
                self.list_entrycompletion_editions.sort()
        
        def show_details(self, treeview, treepath, column, selection, button_show_details):
                """Emulates a click on the button_show_details when the user double-clicks on the treeview.
                
                """
                
                if button_show_details.get_sensitive():
                        button_show_details.emit("clicked")
        
        def send_id_to_loader(self, selection, integer, TreeViewColumn, simple_search):
                """Loads a selection of cards. The first one is displayed in the card viewer.
                
                """
                
                model, pathlist = selection.get_selected_rows()
                if pathlist != []:
                        tree_iter = model.get_iter(pathlist[0])
                        id_ = model.get_value(tree_iter, 0)
                        self.load_card(id_, simple_search)
                        
                        nb_row_in_coll = 0
                        for row in pathlist:
                                if model[row][12] == 700:
                                        nb_row_in_coll += 1
                        if len(pathlist) == nb_row_in_coll:
                                self.button_show_details.set_sensitive(True)
                                self.button_show_details.set_popover(functions.collection.gen_details_popover(self.button_show_details, selection))
                        else:
                                self.button_show_details.set_sensitive(False)
                else:
                        self.button_show_details.set_sensitive(False)
        
        def load_card(self, cardid, simple_search):
                """Loads a card in the card viewer.
                
                """
                
                GLib.idle_add(functions.cardviewer.gen_card_viewer, cardid, self.card_viewer, self, simple_search)
        
        def load_card_from_outside(self, widget, cardid, list_widgets_to_destroy, simple_search):
                """Loads a card in the card viewer, from another mode.
                
                """
                
                GLib.idle_add(functions.cardviewer.gen_card_viewer, cardid, self.card_viewer, self, simple_search)
