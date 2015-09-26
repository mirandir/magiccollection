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
                
                mainwindow.main_stack.add_titled(self.mainbox, "advancedsearch", defs.STRINGS["advancedsearch"])
                
                self.card_viewer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
                right_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                self.mainbox.pack_start(self.card_viewer, False, False, 0)
                self.mainbox.pack_start(separator, False, False, 0)
                self.mainbox.pack_start(right_content, True, True, 0)
                
                right_content_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                right_content_mid = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
                right_content_mid.set_homogeneous(True)
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
                
                # we list each edition in a treeview
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
                #column_name_editions.set_expand(False)
                column_name_editions.set_sort_column_id(nb_column)
                store_editions.set_sort_column_id(nb_column, sort)
                tree_editions.append_column(column_name_editions)
                
                select = tree_editions.get_selection()
                
                edition_nb_cards_symbol = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.label_nb_cards = Gtk.Label()
                self.icon_edition = Gtk.Image()
                edition_nb_cards_symbol.pack_start(self.label_nb_cards, False, False, 0)
                edition_nb_cards_symbol.pack_start(self.icon_edition, False, False, 0)
                
                select.connect("changed", self.edition_selected, "blip", "blop", tree_editions)
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
                                comboboxtext.append(defs.SEARCH_ITEMS[i][0], defs.SEARCH_ITEMS[i][1])
                
                entry1 = Gtk.Entry()
                self.entry1 = entry1
                entry2 = Gtk.Entry()
                entry3 = Gtk.Entry()
                entry4 = Gtk.Entry()
                
                comboboxtext1.set_active(0)
                comboboxtext1.connect("changed", self.comboboxtext_changed, entry1)
                comboboxtext2.set_active(2)
                comboboxtext2.connect("changed", self.comboboxtext_changed, entry2)
                comboboxtext3.set_active(1)
                comboboxtext3.connect("changed", self.comboboxtext_changed, entry3)
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
                        entry.connect("activate", self.prepare_request, [[entry1, comboboxtext1], [entry2, comboboxtext2], [entry3, comboboxtext3], [entry4, comboboxtext4]], overlay_right_content_bot)
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
                right_content_mid.pack_start(edition_nb_cards_symbol, False, False, 0)
                
                right_content_mid_right = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                right_content_mid.pack_start(right_content_mid_right, False, False, 0)
                
                self.button_reset_search.set_sensitive(False)
                button_reset_search_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="edit-clear-all-symbolic"), Gtk.IconSize.BUTTON)
                self.button_reset_search.add(button_reset_search_pic)
                self.button_reset_search.connect("clicked", self.reset_search, entry1, entry2, entry3, entry4)
                right_content_mid_right.pack_start(self.button_reset_search, False, False, 0)
                
                self.button_search.set_sensitive(False)
                self.button_search.connect("clicked", self.prepare_request, [[entry1, comboboxtext1], [entry2, comboboxtext2], [entry3, comboboxtext3], [entry4, comboboxtext4]], overlay_right_content_bot)
                right_content_mid_right.pack_start(self.button_search, False, False, 0)
                
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
        
        def sensitive_widgets(self, sensitive):
                text_in_entry = 0
                for widget in self.sens_widgets:
                        widget.set_sensitive(sensitive)
                        if widget.__class__.__name__ == "Entry":
                                if widget.get_text() != "":
                                        text_in_entry = 1
                if sensitive:
                        if text_in_entry == 0:
                                self.button_search.set_sensitive(False)
        
        def update_current_store_bold(self, cards_data_for_update_store_as):
                if self.mainstore != None:
                        i = 0
                        for row in self.mainstore:
                                for card in cards_data_for_update_store_as:
                                        if row[1] == card[0] and row[2] == card[1]:
                                                self.mainstore[i][12] = 700
                                i += 1
        
        def launch_ad_search(self, request, type_s, wait_button):
                '''Launches an advanced search with request'''
                conn, c = functions.db.connect_db()
                c.execute(request)
                reponses = c.fetchall()
                functions.db.disconnect_db(conn)
                defs.MEM_SEARCHS[request] = reponses
                #GLib.idle_add(self.disp_result, reponses, type_s, wait_button)
                self.disp_result(reponses, type_s, wait_button)
                
        def disp_result(self, reponses, type_s, wait_button):
                '''Display the result'''
                for widget in self.box_results.get_children():
                        GLib.idle_add(self.box_results.remove, widget)
                if len(reponses) > 0:                
                        GLib.idle_add(self.label_nb_cards.set_text, "")
                        # we create the treeview for displaying results                        
                        scrolledwindow = Gtk.ScrolledWindow()
                        scrolledwindow.set_min_content_width(560)
                        scrolledwindow.set_min_content_height(180)
                        scrolledwindow.set_hexpand(True)
                        scrolledwindow.set_vexpand(True)
                        scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
                        # "id", "name", "edition", "name_french", "colors", colors_pixbuf, "cmc", "type", "artist", "power", "toughness", "rarity", "bold", "italic", "unique_name"
                        store_results = Gtk.ListStore(str, str, str, str, str, GdkPixbuf.Pixbuf, str, str, str, str, str, str, int, Pango.Style, str)
                        tree_results = Gtk.TreeView(store_results)
                        tree_results.set_enable_search(False)
                        
                        # some work with columns
                        columns_to_display = functions.config.read_config("as_columns").split(";")
                        
                        self.as_columns_list = functions.various.gen_treeview_columns(columns_to_display, tree_results)
                        
                        select = tree_results.get_selection()
                        select.set_mode(Gtk.SelectionMode.MULTIPLE)
                        select.connect("changed", self.send_id_to_loader, "blip", "blop", 0)
                        self.mainselect = select
                        scrolledwindow.add(tree_results)
                        self.mainstore = store_results
                        
                        GLib.idle_add(self.box_results.pack_start, scrolledwindow, True, True, 0)
                        
                        nb = 0
                        cards_added = []
                        cards = functions.various.prepare_cards_data_for_treeview(reponses)
                        
                        # we get a list of cards in the collection
                        conn, c = functions.collection.connect_db()
                        c.execute("""SELECT id, name, nb_variant, edition FROM collection""")
                        reponses_coll = c.fetchall()
                        functions.collection.disconnect_db(conn)
                        
                        for card in cards.values():
                                # if this card is in the collection, we bolding it
                                bold = 400
                                for card_coll in reponses_coll:
                                        id_, name, nb_variant, edition_code = card_coll
                                        if name == card["real_name"] and nb_variant == card["nb_variant"] and edition_code == card["edition_code"]:
                                                bold = 700
                                                break
                                italic = Pango.Style.NORMAL
                                
                                add = True
                                
                                if card["layout"] == "flip" or card["layout"] == "double-faced" or card["layout"] == "split":
                                        names = card["names"].split("|")
                                        if card["real_name"] != names[0] and type_s == "edition":
                                                add = False
                                
                                if card["name"] + "-" + card["edition_ln"] in cards_added:
                                        add = False
                                
                                if add:
                                        unique_name = functions.various.get_unique_name(card["real_name"], card["nb_variant"], card["edition_code"])
                                        store_results.insert_with_valuesv(-1, range(15), [card["id_"], card["name"], card["edition_ln"], card["nameforeign"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold, italic, unique_name])
                                        #store_results.append([card["id_"], card["name"], card["edition_ln"], card["namefr"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], backgroundcolor])
                                        cards_added.append(card["name"] + "-" + card["edition_ln"])
                                        nb += 1
                        
                        GLib.idle_add(store_results.set_sort_column_id, 7, Gtk.SortType.ASCENDING)
                        GLib.idle_add(store_results.set_sort_column_id, 2, Gtk.SortType.ASCENDING)
                        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                                GLib.idle_add(store_results.set_sort_column_id, 3, Gtk.SortType.ASCENDING)
                        else:
                                GLib.idle_add(store_results.set_sort_column_id, 1, Gtk.SortType.ASCENDING)
                        
                        if wait_button != None:
                                GLib.idle_add(wait_button.destroy)
                        
                        if nb > 1:
                                GLib.idle_add(self.label_nb_cards.set_text, str(nb) + " " + defs.STRINGS["cards"])
                        else:
                                GLib.idle_add(self.label_nb_cards.set_text, str(nb) + " " + defs.STRINGS["card"])
                        
                        GLib.idle_add(scrolledwindow.show_all)
                else:
                        if wait_button != None:
                                GLib.idle_add(wait_button.destroy)
                        
                        GLib.idle_add(self.label_nb_cards.set_text, "")
                        label_result = Gtk.Label()
                        label_result.set_markup("<big>" + defs.STRINGS["no_result"] + "</big>")
                        label_result.set_line_wrap(True)
                        label_result.set_ellipsize(Pango.EllipsizeMode.END)
                        label_result.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                        GLib.idle_add(label_result.show)
                        GLib.idle_add(self.box_results.pack_start, label_result, True, True, 0)
                GLib.idle_add(self.sensitive_widgets, True)
        
        def prepare_request(self, widget, search_widgets_list, overlay_right_content_bot):
                '''Prepares the request to the database'''
                try:
                        g_op = self.g_operator.get_text()
                except:
                        g_op = None
                request = functions.db.prepare_request(search_widgets_list, g_op)
                if request != None:
                        self.sensitive_widgets(False)
                        self.icon_edition.hide()
                        for widget in self.box_results.get_children():
                                self.box_results.remove(widget)
                        
                        wait_button = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                        wait_button.props.valign = Gtk.Align.CENTER
                        as_spinner = Gtk.Spinner()
                        as_spinner.set_size_request(30, 30)
                        wait_button.pack_start(as_spinner, True, True, 0)
                        as_spinner.start()
                        wait_button.show_all()
                        overlay_right_content_bot.add_overlay(wait_button)
                        
                        thread_time = threading.Thread(target = self.launch_thread_time, args = [wait_button])
                        thread_time.daemon = True
                        thread_time.start()
                        
                        try:
                                prev_search = defs.MEM_SEARCHS[request]
                        except KeyError:
                                thread = threading.Thread(target = self.launch_ad_search, args = (request, "", wait_button))
                                thread.daemon = True
                                thread.start()
                        else:
                                thread = threading.Thread(target = self.disp_result, args = (prev_search, "", wait_button))
                                thread.daemon = True
                                thread.start()
        
        def launch_thread_time(self, wait_button_box):
                time.sleep(5)
                label_wait = Gtk.Label()
                label_wait.set_markup("<big>" + defs.STRINGS["please_wait"] + "</big>")
                GLib.idle_add(label_wait.show)
                GLib.idle_add(wait_button_box.pack_start, label_wait, True, True, 0)
        
        def edition_selected(self, selection, integer, TreeViewColumn, tree_editions):
                self.sensitive_widgets(False)
                model, treeiter = selection.get_selected()
                if treeiter != None:
                        ed_name = model[treeiter][0].replace('"', '""')
                        conn, c = functions.db.connect_db()
                        c.execute("""SELECT code FROM editions WHERE name = \"""" + ed_name + """\" OR name_french = \"""" + ed_name + """\"""")
                        reponse = c.fetchone()
                        functions.db.disconnect_db(conn)
                        request = """SELECT * FROM cards WHERE edition = \"""" + reponse[0] + """\""""
                        
                        if os.path.isfile(os.path.join(defs.CACHEMCPIC, "icons", functions.various.valid_filename_os(reponse[0]) + ".png")):
                                self.icon_edition.set_from_file(os.path.join(defs.CACHEMCPIC, "icons", functions.various.valid_filename_os(reponse[0]) + ".png"))
                                self.icon_edition.show()
                        else:
                                self.icon_edition.hide()
                        
                        try:
                                prev_search = defs.MEM_SEARCHS[request]
                        except KeyError:
                                #self.launch_ad_search(request, "edition", None)
                                thread = threading.Thread(target = self.launch_ad_search, args = (request, "edition", None))
                                thread.daemon = True
                                thread.start()
                        else:
                                #self.disp_result(prev_search, "edition", None)
                                thread = threading.Thread(target = self.disp_result, args = (prev_search, "edition", None))
                                thread.daemon = True
                                thread.start()
        
        def reset_search(self, button, entry1, entry2, entry3, entry4):
                for entry in [entry1, entry2, entry3, entry4]:
                        entry.set_text("")
        
        def entry_operator_choice(self, entry, icon, void):
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
                if button.get_active():
                        if name == "1":
                                if functions.config.read_config("dark_theme") == "0":
                                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(defs.PATH_MC, "images", "math", "equal.svg"))
                                else:
                                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(defs.PATH_MC, "images", "math", "equal_white.svg"))
                                entry.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, pixbuf)
                                entry.set_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY, defs.STRINGS["entry_eq_ad"])
                        elif name == "2":
                                if functions.config.read_config("dark_theme") == "0":
                                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(defs.PATH_MC, "images", "math", "inf_or_eq.svg"))
                                else:
                                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(defs.PATH_MC, "images", "math", "inf_or_eq_white.svg"))
                                entry.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, pixbuf)
                                entry.set_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY, defs.STRINGS["entry_inf_eq_ad"])
                        elif name == "3":
                                if functions.config.read_config("dark_theme") == "0":
                                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(defs.PATH_MC, "images", "math", "sup_or_eq.svg"))
                                else:
                                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(defs.PATH_MC, "images", "math", "sup_or_eq_white.svg"))
                                entry.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, pixbuf)
                                entry.set_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY, defs.STRINGS["entry_sup_eq_ad"])
                        elif name == "4":
                                if functions.config.read_config("dark_theme") == "0":
                                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(defs.PATH_MC, "images", "math", "different.svg"))
                                else:
                                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(defs.PATH_MC, "images", "math", "different_white.svg"))
                                entry.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, pixbuf)
                                entry.set_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY, defs.STRINGS["entry_diff"])
        
        def comboboxtext_changed(self, comboboxtext, entry):
                search = ""
                for infosearch in defs.SEARCH_ITEMS.values():
                        if infosearch[1] == comboboxtext.get_active_text():
                                search = infosearch[0]
                                break
                if search == "cmc" or search == "power" or search == "toughness" or search == "loyalty":
                        if functions.config.read_config("dark_theme") == "0":
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(defs.PATH_MC, "images", "math", "equal.svg"))
                        else:
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(defs.PATH_MC, "images", "math", "equal_white.svg"))
                        entry.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, pixbuf)
                        entry.set_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY, defs.STRINGS["entry_eq_ad"])
                else:
                        entry.set_icon_from_pixbuf(Gtk.EntryIconPosition.PRIMARY, None)
                
        def gen_list_editions(self):
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
                        self.store_editions.append([nom_fr_ou_en, info_edition[1], info_edition[2], info_edition[3].replace("-", ""), info_edition[4], info_edition[5]])
                
                functions.db.disconnect_db(conn)
        
        def send_id_to_loader(self, selection, integer, TreeViewColumn, simple_search):
                model, pathlist = selection.get_selected_rows()
                if pathlist != []:
                        tree_iter = model.get_iter(pathlist[0])
                        id_ = model.get_value(tree_iter, 0)
                        self.load_card(id_, simple_search)
        
        def load_card(self, cardid, simple_search):
                '''Load a card in the card viewer'''
                functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
        
        def load_card_from_outside(self, widget, cardid, list_widgets_to_destroy, simple_search):
                for widget in list_widgets_to_destroy:
                        widget.destroy()
                functions.cardviewer.gen_card_viewer(cardid, self.card_viewer, self, simple_search)
