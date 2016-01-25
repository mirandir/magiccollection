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

# Read & write the configuration file, generate the config window

from gi.repository import Gtk, Gio
import os

# import global values
import defs

def read_config_file():
        '''Read the configuration file.'''
        configfile = open(os.path.join(defs.CONFIGMC, "config"), "r", encoding="UTF-8")
        config = configfile.readlines()
        configfile.close()
        
        configuration = {}
        
        i = 0
        for ligne in config:
                ligne = ligne.rstrip("\n\r")
                ligneexplode = ligne.split(" ")
                configuration[ligneexplode[0]] = [ligneexplode[2], i]
                i = i + 1
        return(configuration)

def read_all_config():
        '''Read all the configuration.'''
        configuration = read_config_file()
        dict_config = {}
        for param in defs.VARCONFIGDEFAULT.keys():
                try:
                        value = configuration[param][0]
                except KeyError:
                        value = defs.VARCONFIGDEFAULT[param]
                dict_config[param] = value
        return(dict_config)

def read_config(param):
        '''Return one param of config.'''
        if param in defs.VARCONFIGDEFAULT.keys():
                configuration = read_config_file()
                try:
                        value = configuration[param][0]
                except KeyError:
                        value = defs.VARCONFIGDEFAULT[param]
                return(value)
        else:
                print("param is unknown !")

def change_config(param, value):
        '''Change the configuration.'''
        configuration = read_config_file()
        if param in defs.VARCONFIGDEFAULT.keys():
                try:
                        currentvalue = configuration[param][0]
                except KeyError:
                        currentvalue = defs.VARCONFIGDEFAULT[param]
                        # param not found in the config file, adding...
                        out = open(os.path.join(defs.CONFIGMC, "config"), 'a', encoding="UTF-8")
                        nouveautexte = param + " = " + currentvalue + "\n"
                        out.write(nouveautexte)
                        out.close()
                        configuration = read_config_file()
                if currentvalue != value:
                        # new value != current value, changing config file
                        lines = open(os.path.join(defs.CONFIGMC, "config"), 'r', encoding="UTF-8").readlines()
                        nbligne = configuration[param][1]
                        nouveautexte = param + " = " + value + "\n"
                        lines[nbligne] = nouveautexte
                        out = open(os.path.join(defs.CONFIGMC, "config"), 'w', encoding="UTF-8")
                        out.writelines(lines)
                        out.close()
        else:
                print("param is unknown !")

def show_pref_dialog():
        def gen_warning_pic():
                pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="dialog-warning-symbolic"), Gtk.icon_size_from_name("12_config_warning"))
                pic.set_tooltip_text(defs.STRINGS["config_need_restart"])
                pic.set_margin_left(6)
                return(pic)
        def comboboxtext_ext_sort_as_changed(comboboxtext):
                if comboboxtext.get_active() == 0:
                        change_config("ext_sort_as", "0")
                elif comboboxtext.get_active() == 1:
                        change_config("ext_sort_as", "1")
        def comboboxtext_fr_language_changed(comboboxtext):
                nb_lang = comboboxtext.get_active()
                change_config("fr_language", defs.LOC_LANG_NAME[nb_lang][0])
        def checkbutton_toggled(checkbutton, param):
                if checkbutton.get_active():
                        change_config(param, "1")
                else:
                        change_config(param, "0")
        def checkbutton_dark_theme_toggled(checkbutton, param):
                settings = Gtk.Settings.get_default()
                if checkbutton.get_active():
                        change_config(param, "1")
                        settings.set_property("gtk-application-prefer-dark-theme", True)
                else:
                        change_config(param, "0")
                        settings.set_property("gtk-application-prefer-dark-theme", False)
        def checkbutton_not_internet_popup_toggled(checkbutton, param):
                if checkbutton.get_active():
                        change_config(param, "0")
                else:
                        change_config(param, "1")
        
        if defs.PREF_WINDOW_OPEN == False:
                defs.PREF_WINDOW_OPEN = True
                
                pref_dialog = Gtk.Dialog()
                pref_dialog.set_title(defs.STRINGS["preferences_of_mc"])
                if defs.MAINWINDOW != None:
                        pref_dialog.set_transient_for(defs.MAINWINDOW)
                        pref_dialog.set_modal(True)
                
                # we create the notebook and their children
                notebook = Gtk.Notebook()
                dict_config = read_all_config()
                
                # display
                box_display = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                label_editions = Gtk.Label()
                label_editions.set_markup("<b>" + defs.STRINGS["config_editions"] + "</b>")
                box_display.pack_start(label_editions, False, True, 0)
                
                if defs.LANGUAGE == "fr":
                        box_ext_fr_name = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                        checkbutton_ext_fr_name = Gtk.CheckButton(defs.STRINGS["config_ext_fr_name"])
                        box_ext_fr_name.set_margin_left(12)
                        box_ext_fr_name.pack_start(checkbutton_ext_fr_name, False, False, 0)
                        if dict_config["ext_fr_name"] == "1":
                                checkbutton_ext_fr_name.set_active(True)
                        checkbutton_ext_fr_name.connect("toggled", checkbutton_toggled, "ext_fr_name")
                        box_ext_fr_name.pack_start(gen_warning_pic(), False, False, 0)
                        box_display.pack_start(box_ext_fr_name, False, True, 0)
                
                box_ext_sort_as = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                label_ext_sort_as = Gtk.Label(defs.STRINGS["config_ext_sort_as"])
                comboboxtext_ext_sort_as = Gtk.ComboBoxText()
                comboboxtext_ext_sort_as.append("date", defs.STRINGS["config_ext_sort_as_date"])
                comboboxtext_ext_sort_as.append("name", defs.STRINGS["config_ext_sort_as_name"])
                if dict_config["ext_sort_as"] == "0":
                        comboboxtext_ext_sort_as.set_active(0)
                elif dict_config["ext_sort_as"] == "1":
                        comboboxtext_ext_sort_as.set_active(1)
                comboboxtext_ext_sort_as.connect("changed", comboboxtext_ext_sort_as_changed)
                box_ext_sort_as.pack_start(label_ext_sort_as, False, False, 0)
                box_ext_sort_as.pack_start(comboboxtext_ext_sort_as, False, False, 0)
                box_ext_sort_as.pack_start(gen_warning_pic(), False, False, 0)
                box_display.pack_start(box_ext_sort_as, False, True, 0)
                
                label_searches = Gtk.Label()
                label_searches.set_markup("<b>" + defs.STRINGS["config_searches"] + "</b>")
                box_display.pack_start(label_searches, False, True, 0)
                
                checkbutton_no_reprints = Gtk.CheckButton(defs.STRINGS["config_no_reprints"])
                if dict_config["no_reprints"] == "1":
                                checkbutton_no_reprints.set_active(True)
                checkbutton_no_reprints.connect("toggled", checkbutton_toggled, "no_reprints")
                box_display.pack_start(checkbutton_no_reprints, False, True, 0)
                
                label_cardviewer = Gtk.Label()
                label_cardviewer.set_markup("<b>" + defs.STRINGS["config_cardviewer"] + "</b>")
                box_display.pack_start(label_cardviewer, False, True, 0)
                
                checkbutton_show_en_name_in_card_viewer = Gtk.CheckButton(defs.STRINGS["config_show_en_name_in_card_viewer"])
                if dict_config["show_en_name_in_card_viewer"] == "1":
                                checkbutton_show_en_name_in_card_viewer.set_active(True)
                checkbutton_show_en_name_in_card_viewer.connect("toggled", checkbutton_toggled, "show_en_name_in_card_viewer")
                box_display.pack_start(checkbutton_show_en_name_in_card_viewer, False, True, 0)
                
                label_collection = Gtk.Label()
                label_collection.set_markup("<b>" + defs.STRINGS["config_collection"] + "</b>")
                box_display.pack_start(label_collection, False, True, 0)
                
                checkbutton_add_collection_show_details = Gtk.CheckButton(defs.STRINGS["config_add_collection_show_details"])
                if dict_config["add_collection_show_details"] == "1":
                                checkbutton_add_collection_show_details.set_active(True)
                checkbutton_add_collection_show_details.connect("toggled", checkbutton_toggled, "add_collection_show_details")
                box_display.pack_start(checkbutton_add_collection_show_details, False, True, 0)
                
                label_general_aspect = Gtk.Label()
                label_general_aspect.set_markup("<b>" + defs.STRINGS["config_general_aspect"] + "</b>")
                box_display.pack_start(label_general_aspect, False, True, 0)
                
                checkbutton_dark_theme = Gtk.CheckButton(defs.STRINGS["config_dark_theme"])
                if dict_config["dark_theme"] == "1":
                                checkbutton_dark_theme.set_active(True)
                checkbutton_dark_theme.connect("toggled", checkbutton_dark_theme_toggled, "dark_theme")
                box_display.pack_start(checkbutton_dark_theme, False, True, 0)
                
                # columns
                box_columns = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                
                label_nonenglish_names = Gtk.Label()
                label_nonenglish_names.set_markup("<b>" + defs.STRINGS["config_nonenglish_names"] + "</b>")
                box_columns.pack_start(label_nonenglish_names, False, True, 0)
                
                box_fr_language = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                label_fr_language = Gtk.Label(defs.STRINGS["config_fr_language"])
                comboboxtext_fr_language = Gtk.ComboBoxText()
                try:
                        fr_ln = dict_config["fr_language"]
                except KeyError:
                        fr_ln = "de"
                current_nb = None
                for nb, data in defs.LOC_LANG_NAME.items():
                        loc, lang_name = data
                        comboboxtext_fr_language.append(loc, lang_name)
                        if loc == fr_ln:
                                current_nb = nb
                comboboxtext_fr_language.set_active(current_nb)
                comboboxtext_fr_language.connect("changed", comboboxtext_fr_language_changed)
                box_fr_language.pack_start(label_fr_language, False, False, 0)
                box_fr_language.pack_start(comboboxtext_fr_language, False, False, 0)
                box_fr_language.pack_start(gen_warning_pic(), False, False, 0)
                box_columns.pack_start(box_fr_language, False, True, 0)
                
                box_columns_order_disp = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                label_columns_order_disp = Gtk.Label()
                label_columns_order_disp.set_markup("<b>" + defs.STRINGS["config_columns_order_disp"] + "</b>")
                box_columns_order_disp.pack_start(label_columns_order_disp, False, False, 0)
                box_columns_order_disp.pack_start(gen_warning_pic(), False, False, 0)
                box_columns.pack_start(box_columns_order_disp, False, True, 0)
                
                label_columns_order_disp_helper = Gtk.Label()
                label_columns_order_disp_helper.set_markup("<i><small>" + defs.STRINGS["config_columns_helper"] + "</small></i>")
                box_columns.pack_start(label_columns_order_disp_helper, False, True, 0)
                
                box_columns_coll_decks = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                scrolledwindow_columns_collection = gen_columns_choice(dict_config["coll_columns"].split(";"), defs.COLL_COLUMNS_CHOICE, "coll_columns", defs.STRINGS["config_columns_collection"])
                box_columns_coll_decks.pack_start(scrolledwindow_columns_collection, True, True, 0)
                scrolledwindow_columns_decks = gen_columns_choice(dict_config["decks_columns"].split(";"), defs.DECKS_COLUMNS_CHOICE, "decks_columns", defs.STRINGS["config_columns_decks"])
                box_columns_coll_decks.pack_start(scrolledwindow_columns_decks, True, True, 0)
                box_columns.pack_start(box_columns_coll_decks, False, True, 0)
                
                scrolledwindow_columns_as = gen_columns_choice(dict_config["as_columns"].split(";"), defs.AS_COLUMNS_CHOICE, "as_columns", defs.STRINGS["config_columns_as"])
                box_columns.pack_start(scrolledwindow_columns_as, False, True, 0)
                
                # internet
                box_internet = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                
                label_pics_cards = Gtk.Label()
                label_pics_cards.set_markup("<b>" + defs.STRINGS["config_pics_cards"] + "</b>")
                box_internet.pack_start(label_pics_cards, False, True, 0)
                
                checkbutton_download_pic_collection_decks = Gtk.CheckButton(defs.STRINGS["config_download_pic_collection_decks"])
                if dict_config["download_pic_collection_decks"] == "1":
                                checkbutton_download_pic_collection_decks.set_active(True)
                checkbutton_download_pic_collection_decks.connect("toggled", checkbutton_toggled, "download_pic_collection_decks")
                box_internet.pack_start(checkbutton_download_pic_collection_decks, False, True, 0)
                
                checkbutton_download_pic_as = Gtk.CheckButton(defs.STRINGS["config_download_pic_as"])
                if dict_config["download_pic_as"] == "1":
                                checkbutton_download_pic_as.set_active(True)
                checkbutton_download_pic_as.connect("toggled", checkbutton_toggled, "download_pic_as")
                box_internet.pack_start(checkbutton_download_pic_as, False, True, 0)
                
                label_connection = Gtk.Label()
                label_connection.set_markup("<b>" + defs.STRINGS["config_connection"] + "</b>")
                box_internet.pack_start(label_connection, False, True, 0)
                
                checkbutton_not_internet_popup = Gtk.CheckButton(defs.STRINGS["config_not_internet_popup"])
                if dict_config["not_internet_popup"] == "0":
                                checkbutton_not_internet_popup.set_active(True)
                checkbutton_not_internet_popup.connect("toggled", checkbutton_not_internet_popup_toggled, "not_internet_popup")
                box_internet.pack_start(checkbutton_not_internet_popup, False, True, 0)
                
                # prices
                box_prices = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                
                for grid in [box_display, box_columns, box_internet, box_prices]:
                        grid.props.border_width = 12
                for label in [label_editions, label_ext_sort_as, label_searches, label_cardviewer, label_collection, label_general_aspect, label_pics_cards, label_connection, label_nonenglish_names, label_columns_order_disp, label_columns_order_disp_helper]:
                        label.set_alignment(0.0, 0.5)
                for widget in [label_ext_sort_as, checkbutton_no_reprints, checkbutton_show_en_name_in_card_viewer, checkbutton_add_collection_show_details, checkbutton_dark_theme, checkbutton_download_pic_collection_decks, checkbutton_download_pic_as, checkbutton_not_internet_popup, label_fr_language, label_columns_order_disp_helper, box_columns_coll_decks, scrolledwindow_columns_as]:
                        widget.set_margin_left(12)
                
                notebook.append_page(box_display, Gtk.Label(defs.STRINGS["config_display"]))
                notebook.append_page(box_columns, Gtk.Label(defs.STRINGS["config_columns"]))
                notebook.append_page(box_internet, Gtk.Label(defs.STRINGS["config_internet"]))
                notebook.append_page(box_prices, Gtk.Label(defs.STRINGS["config_cardsprices"]))
                
                content_area = pref_dialog.get_content_area()
                content_area.props.border_width = 0
                content_area.pack_start(notebook, True, True, 0)
                notebook.show_all()
                pref_dialog.run()
                pref_dialog.destroy()
                defs.PREF_WINDOW_OPEN = False

def gen_columns_choice(list_current_columns, list_all_columns, param_config, column_name):
        def cell_toggled(cellrenderertoggle, path, liststore):
                liststore[path][1] = not liststore[path][1]
                gen_columns_config(liststore)
        def select_changed(selection, liststore):
                gen_columns_config(liststore)
        def gen_columns_config(liststore):
                current_columns_config = read_config(param_config)
                
                new_columns_config_list = []
                for row in liststore:
                        if row[1]:
                                new_columns_config_list.append(row[0])
                new_columns_config = ""
                for column in new_columns_config_list:
                        new_columns_config = new_columns_config + column + ";"
                new_columns_config = new_columns_config[:-1]
                if new_columns_config != current_columns_config:
                        change_config(param_config, new_columns_config)
        
        liststore = Gtk.ListStore(str, bool, str)
        for col in list_current_columns:
                liststore.append([col, True, defs.COLUMN_NAME_TRANSLATED[col]])
        for col in list_all_columns:
                if col not in list_current_columns:
                        liststore.append([col, False, defs.COLUMN_NAME_TRANSLATED[col]])
        
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_min_content_width(100)
        scrolledwindow.set_min_content_height(120)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
        
        treeview = Gtk.TreeView(liststore)
        treeview.set_enable_search(False)
        treeview.set_reorderable(True)
        
        select = treeview.get_selection()
        select.connect("changed", select_changed, liststore)
        
        renderer_checkbutton = Gtk.CellRendererToggle()
        renderer_checkbutton.connect("toggled", cell_toggled, liststore)
        renderer_column_name = Gtk.CellRendererText()
        
        column_checkbutton = Gtk.TreeViewColumn(defs.STRINGS["config_column_enabled"], renderer_checkbutton, active=1)
        column_column_name = Gtk.TreeViewColumn(column_name, renderer_column_name, text=2)
        
        treeview.append_column(column_checkbutton)
        treeview.append_column(column_column_name)
        
        scrolledwindow.add(treeview)
        scrolledwindow.show_all()
        return(scrolledwindow)
