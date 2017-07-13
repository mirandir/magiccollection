#!/usr/bin/python
# -*-coding:Utf-8 -*
#

# Copyright 2013-2017 mirandir

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

from gi.repository import Gtk, Gio, GLib
import os
import threading
import shutil
import time

# import global values
import defs
import functions.prices

def read_config_file():
        """Reads the configuration file.
        
        """
        
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
        """Reads each item in the configuration file.
        
        """
        
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
        """Returns one param of config.
        
        """
        
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
        """Changes the configuration.
        
        """
        
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

def comboboxtext_prices_cur_changed(comboboxtext):
        if comboboxtext.get_active() == 0:
                change_config("price_cur", "0")
        elif comboboxtext.get_active() == 1:
                change_config("price_cur", "1")

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

def checkbutton_dv_condition_toggled(checkbutton, param, comboboxtext_dv_condition):
        if checkbutton.get_active():
                comboboxtext_dv_condition.set_sensitive(True)
                condition = ""
                for cond in defs.CONDITIONS.values():
                        if cond[1] == comboboxtext_dv_condition.get_active_text():
                                condition = cond[0]
                                break
                if condition != "":
                        change_config(param, condition)
        else:
                comboboxtext_dv_condition.set_sensitive(False)
                change_config(param, "0")

def checkbutton_dv_lang_toggled(checkbutton, param, entry_dv_lang):
        if checkbutton.get_active():
                entry_dv_lang.set_sensitive(True)
                cur_text = entry_dv_lang.get_text()
                if cur_text != "":
                        change_config(param, cur_text)
        else:
                entry_dv_lang.set_sensitive(False)
                change_config(param, "0")

def comboboxtext_dv_condition_changed(comboboxtext):
        condition = ""
        for cond in defs.CONDITIONS.values():
                if cond[1] == comboboxtext.get_active_text():
                        condition = cond[0]
                        break
        if condition != "":
                change_config("default_condition", condition)

def entry_dv_lang_changed(entry):
        def prepare_update_dvlang(text):
                def update_dvlang(text):
                        change_config("default_lang", text)
                
                if defs.CURRENT_SAVE_DV_LANG == None:
                        # we are the first thread, we need to note this
                        defs.CURRENT_SAVE_DV_LANG = 1
                else:
                        defs.CURRENT_SAVE_DV_LANG += 1
                my_number = int(defs.CURRENT_SAVE_DV_LANG)
                defs.SAVEDV_LANG_TIMER = 250 # 250 ms
                
                # now, we wait until the end of the timer (or until another thread take our turn)
                go = 1
                while defs.SAVEDV_LANG_TIMER > 0:
                        if my_number != defs.CURRENT_SAVE_DV_LANG:
                                # too bad, we have to stop now
                                go = 0
                                break
                        else:
                                time.sleep(1 / 1000)
                                defs.SAVEDV_LANG_TIMER -= 1
                
                if go == 1:
                        defs.CURRENT_SAVE_DV_LANG = None
                        GLib.idle_add(update_dvlang, text)
        
        if entry.get_sensitive():
                thread = threading.Thread(target = prepare_update_dvlang, args = ([entry.get_text()]))
                thread.daemon = True
                thread.start()

def show_pref_dialog():
        """Generates and displays the configuration window.
        
        """
        
        if defs.PREF_WINDOW_OPEN == False:
                defs.PREF_WINDOW_OPEN = True
                
                pref_dialog = Gtk.Dialog()
                pref_dialog.set_title(defs.STRINGS["preferences_of_mc"])
                pref_dialog.set_icon_name("magic_collection")
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
                
                if defs.LANGUAGE != "en":
                        label_cardviewer = Gtk.Label()
                        label_cardviewer.set_markup("<b>" + defs.STRINGS["config_cardviewer"] + "</b>")
                        label_cardviewer.set_alignment(0.0, 0.5)
                        box_display.pack_start(label_cardviewer, False, True, 0)
                        
                        checkbutton_show_en_name_in_card_viewer = Gtk.CheckButton(defs.STRINGS["config_show_en_name_in_card_viewer"])
                        checkbutton_show_en_name_in_card_viewer.set_margin_left(12)
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
                
                if Gtk.Settings.get_default().get_property("gtk-theme-name") == "Adwaita":
                        label_general_aspect = Gtk.Label()
                        label_general_aspect.set_markup("<b>" + defs.STRINGS["config_general_aspect"] + "</b>")
                        box_display.pack_start(label_general_aspect, False, True, 0)
                        
                        checkbutton_dark_theme = Gtk.CheckButton(defs.STRINGS["config_dark_theme"])
                        if dict_config["dark_theme"] == "1":
                                        checkbutton_dark_theme.set_active(True)
                        checkbutton_dark_theme.connect("toggled", checkbutton_dark_theme_toggled, "dark_theme")
                        box_display.pack_start(checkbutton_dark_theme, False, True, 0)
                        label_general_aspect.set_alignment(0.0, 0.5)
                        checkbutton_dark_theme.set_margin_left(12)
                
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
                
                # default values
                box_defaultvalues = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                
                label_dv_add_to_collection = Gtk.Label()
                label_dv_add_to_collection.set_markup("<b>" + defs.STRINGS["config_defaultvalues_addcoll_details"] + "</b>")
                box_defaultvalues.pack_start(label_dv_add_to_collection, False, True, 0)
                
                box_dv_condition = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                checkbutton_dv_condition = Gtk.CheckButton(defs.STRINGS["config_defaultvalues_condition"])
                box_dv_condition.pack_start(checkbutton_dv_condition, False, False, 0)
                comboboxtext_dv_condition = Gtk.ComboBoxText()
                tmp_dict_cond = {}
                for number, list_ in defs.CONDITIONS.items():
                        comboboxtext_dv_condition.append(list_[0], list_[1])
                        tmp_dict_cond[list_[0]] = number
                if dict_config["default_condition"] != "0":
                        checkbutton_dv_condition.set_active(True)
                        comboboxtext_dv_condition.set_active(int(tmp_dict_cond[dict_config["default_condition"]]))
                else:
                        comboboxtext_dv_condition.set_sensitive(False)
                checkbutton_dv_condition.connect("toggled", checkbutton_dv_condition_toggled, "default_condition", comboboxtext_dv_condition)
                comboboxtext_dv_condition.connect("changed", comboboxtext_dv_condition_changed)
                box_dv_condition.pack_start(comboboxtext_dv_condition, False, False, 0)
                box_defaultvalues.pack_start(box_dv_condition, False, True, 0)
                
                box_dv_lang = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                checkbutton_dv_lang = Gtk.CheckButton(defs.STRINGS["config_defaultvalues_lang"])
                box_dv_lang.pack_start(checkbutton_dv_lang, False, False, 0)
                tmp_widgets = functions.various.gen_details_widgets()
                tmp_grid = tmp_widgets[0]
                entry_dv_lang = tmp_widgets[4]
                tmp_grid.remove(entry_dv_lang)
                if dict_config["default_lang"] != "0":
                        checkbutton_dv_lang.set_active(True)
                        entry_dv_lang.set_text(dict_config["default_lang"])
                else:
                        entry_dv_lang.set_sensitive(False)
                checkbutton_dv_lang.connect("toggled", checkbutton_dv_lang_toggled, "default_lang", entry_dv_lang)
                entry_dv_lang.connect("changed", entry_dv_lang_changed)
                box_dv_lang.pack_start(entry_dv_lang, False, False, 0)
                box_defaultvalues.pack_start(box_dv_lang, False, True, 0)
                
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
                gen_prices_box_content(box_prices, dict_config)
                
                # cards pictures
                box_pic_cards = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                
                label_pic_cards_downloaded = Gtk.Label()
                label_pic_cards_downloaded.set_markup("<b>" + defs.STRINGS["config_pic_cards_downloaded"] + "</b>")
                box_pic_cards.pack_start(label_pic_cards_downloaded, False, True, 0)
                
                box_pic_cards_downloaded_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                box_pic_cards.pack_start(box_pic_cards_downloaded_content, False, True, 0)
                gen_pic_cards_downloaded_content(box_pic_cards_downloaded_content)
                
                
                for grid in [box_display, box_columns, box_internet, box_defaultvalues, box_prices, box_pic_cards]:
                        grid.props.border_width = 12
                for label in [label_editions, label_ext_sort_as, label_searches, label_collection, label_pics_cards, label_connection, label_nonenglish_names, label_columns_order_disp, label_columns_order_disp_helper, label_dv_add_to_collection, label_pic_cards_downloaded]:
                        label.set_alignment(0.0, 0.5)
                for widget in [label_ext_sort_as, checkbutton_no_reprints, checkbutton_add_collection_show_details, checkbutton_download_pic_collection_decks, checkbutton_download_pic_as, checkbutton_not_internet_popup, label_fr_language, label_columns_order_disp_helper, box_columns_coll_decks, scrolledwindow_columns_as, box_pic_cards_downloaded_content, box_dv_condition, box_dv_lang]:
                        widget.set_margin_left(12)
                
                notebook.append_page(box_display, Gtk.Label(defs.STRINGS["config_display"]))
                notebook.append_page(box_columns, Gtk.Label(defs.STRINGS["config_columns"]))
                notebook.append_page(box_defaultvalues, Gtk.Label(defs.STRINGS["config_defaultvalues"]))
                notebook.append_page(box_internet, Gtk.Label(defs.STRINGS["config_internet"]))
                notebook.append_page(box_prices, Gtk.Label(defs.STRINGS["config_cardsprices"]))
                notebook.append_page(box_pic_cards, Gtk.Label(defs.STRINGS["config_pic_cards"]))
                
                content_area = pref_dialog.get_content_area()
                content_area.props.border_width = 0
                content_area.pack_start(notebook, True, True, 0)
                notebook.show_all()
                pref_dialog.run()
                pref_dialog.destroy()
                defs.PREF_WINDOW_OPEN = False

def down_prices_manual(button, box_prices, box_button, label, dict_config):
        """Starts the download of the prices (in another thread).
        
        """
        
        def down_in_thread(box_prices, dict_config):
                functions.prices.check_prices("manual")
                GLib.idle_add(gen_prices_box_content, box_prices, dict_config)
                GLib.idle_add(box_prices.show_all)
        
        label.set_text(defs.STRINGS["config_cardsprices_downloading"])
        spinner = Gtk.Spinner()
        spinner.show()
        spinner.start()
        box_button.pack_start(spinner, True, True, 0)
        button.set_sensitive(False)
        thread = threading.Thread(target = down_in_thread, args = (box_prices, dict_config))
        thread.daemon = True
        thread.start()

def get_size(start_path):
        """Gets the size of a folder (from http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python)
        
        """
        
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                        fp = os.path.join(dirpath, f)
                        total_size += os.path.getsize(fp)
        return(total_size)

def GetHumanReadableSize(size,precision=2):
        """Adapted from http://stackoverflow.com/a/32009595
        
        """
        
        suffixes=[defs.STRINGS["config_pic_cards_size_b"], defs.STRINGS["config_pic_cards_size_ko"], defs.STRINGS["config_pic_cards_size_mo"], defs.STRINGS["config_pic_cards_size_go"], defs.STRINGS["config_pic_cards_size_to"]]
        suffixIndex = 0
        while size > 1000 and suffixIndex < 4:
                suffixIndex += 1 #increment the index of the suffix
                size = size/1000.0 #apply the division
        end_val = defs.STRINGS["config_pic_cards_size_unit"].replace("{VALUE}", "%.*f").replace("{SIZE}", "%s")
        return(end_val % (precision, size, suffixes[suffixIndex]))

def get_size_pic_cache(label_pic_cards_size):
        """Launches the calc. of the size of the cache.
        
        """
        
        def update_label(label_pic_cards_size, size):
                label_pic_cards_size.set_text(defs.STRINGS["config_pic_cards_size_all"] + size)
                label_pic_cards_size.show()
        size = GetHumanReadableSize(get_size(defs.CACHEMCPIC))
        GLib.idle_add(update_label, label_pic_cards_size, size)

def gen_pic_cards_downloaded_content(box_pic_cards_downloaded_content):
        """Generates the content for the Manager of downloaded pictures.
        
        """
        
        for widget in box_pic_cards_downloaded_content.get_children():
                box_pic_cards_downloaded_content.remove(widget)
        
        edition_with_pics_list = os.listdir(defs.CACHEMCPIC)
        if len(edition_with_pics_list) < 3:
                label_pic_cards_downloaded_editions_intro = Gtk.Label(defs.STRINGS["config_pic_cards_downloaded_editions_intro_none"])
                box_pic_cards_downloaded_content.pack_start(label_pic_cards_downloaded_editions_intro, False, True, 0)
                label_pic_cards_downloaded_editions_intro.set_alignment(0.0, 0.5)
                label_pic_cards_downloaded_editions_intro.show()
        else:
                def select_changed(selection, liststore, del_pics_ed_button):
                        model, treeiter = selection.get_selected()
                        if treeiter == None:
                                del_pics_ed_button.set_sensitive(False)
                        else:
                                del_pics_ed_button.set_sensitive(True)
                
                def del_pics_ed_button_clicked(button, selection):
                        model, treeiter = selection.get_selected()
                        if treeiter != None:
                                try:
                                        shutil.rmtree(os.path.join(defs.CACHEMCPIC, model[treeiter][0]))
                                except:
                                        pass
                                else:
                                        gen_pic_cards_downloaded_content(box_pic_cards_downloaded_content)
                
                def del_all_pics_ed_button_clicked(button, liststore):
                        for data in liststore:
                                code, longname = data
                                try:
                                        shutil.rmtree(os.path.join(defs.CACHEMCPIC, code))
                                except:
                                        pass
                        gen_pic_cards_downloaded_content(box_pic_cards_downloaded_content)
                                
                
                label_pic_cards_size = Gtk.Label()
                label_pic_cards_size.set_alignment(0.0, 0.5)
                thread = threading.Thread(target = get_size_pic_cache, args = [label_pic_cards_size])
                thread.daemon = True
                thread.start()
                
                liststore = Gtk.ListStore(str, str)
                
                for edition_code in edition_with_pics_list:
                        try:
                                edition_name = functions.various.edition_code_to_longname(edition_code)
                        except:
                                pass
                        else:
                                liststore.append([edition_code, edition_name])
                
                del_pics_ed_button = Gtk.Button(defs.STRINGS["config_pic_cards_delete"])
                del_pics_ed_button.set_sensitive(False)
                
                del_all_pics_ed_button = Gtk.Button(defs.STRINGS["config_pic_cards_delete_all"])
                
                scrolledwindow = Gtk.ScrolledWindow()
                scrolledwindow.set_min_content_width(100)
                scrolledwindow.set_min_content_height(120)
                scrolledwindow.set_vexpand(True)
                scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
                
                treeview = Gtk.TreeView(liststore)
                treeview.set_enable_search(False)
                
                select = treeview.get_selection()
                select.connect("changed", select_changed, liststore, del_pics_ed_button)
                del_pics_ed_button.connect("clicked", del_pics_ed_button_clicked, select)
                del_all_pics_ed_button.connect("clicked", del_all_pics_ed_button_clicked, liststore)
                
                renderer_column_ed_name = Gtk.CellRendererText()
                column_column_ed_name = Gtk.TreeViewColumn(defs.STRINGS["config_pic_cards_downloaded_editions_intro"], renderer_column_ed_name, text=1)
                
                treeview.append_column(column_column_ed_name)
                liststore.set_sort_column_id(1, Gtk.SortType.ASCENDING)
                if defs.OS == "mac":
                        liststore.set_sort_func(1, functions.various.compare_str_osx, None)
                
                scrolledwindow.add(treeview)
                scrolledwindow.show_all()
                del_pics_ed_button.show()
                del_all_pics_ed_button.show()
                
                '''for label in [label_pic_cards_downloaded_editions_intro]:
                        label.set_alignment(0.0, 0.5)'''
                
                box_pic_cards_downloaded_content.pack_start(scrolledwindow, False, True, 0)
                box_pic_cards_downloaded_content.pack_start(label_pic_cards_size, False, True, 0)
                box_pic_cards_downloaded_content.pack_start(del_pics_ed_button, False, True, 0)
                box_pic_cards_downloaded_content.pack_start(del_all_pics_ed_button, False, True, 0)
        
def gen_prices_box_content(box_prices, dict_config):
        """Generates the content for the Manager of prices.
        
        """
        
        for widget in box_prices.get_children():
                box_prices.remove(widget)
        prices_here = functions.prices.check_prices_presence()
        if prices_here == False:
                download_prices_button = Gtk.Button()
                box_button = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                box_button.set_halign(Gtk.Align.CENTER)
                download_prices_button.add(box_button)
                label = Gtk.Label(defs.STRINGS["config_cardsprices_download_first"])
                box_button.pack_start(label, True, True, 0)
                download_prices_button.connect("clicked", down_prices_manual, box_prices, box_button, label, dict_config)
                box_prices.pack_start(download_prices_button, False, True, 0)
        else:
                label_prices_show = Gtk.Label()
                label_prices_show.set_markup("<b>" + defs.STRINGS["config_prices_show"] + "</b>")
                box_prices.pack_start(label_prices_show, False, True, 0)
                
                checkbutton_show_cards_prices = Gtk.CheckButton(defs.STRINGS["config_cardsprices_show"])
                if dict_config["cards_price"] == "1":
                                checkbutton_show_cards_prices.set_active(True)
                checkbutton_show_cards_prices.connect("toggled", checkbutton_toggled, "cards_price")
                box_prices.pack_start(checkbutton_show_cards_prices, False, True, 0)
                
                box_prices_cur = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                label_prices_cur = Gtk.Label(defs.STRINGS["config_price_cur"])
                comboboxtext_prices_cur = Gtk.ComboBoxText()
                comboboxtext_prices_cur.append("dollar", defs.STRINGS["config_price_dollars"])
                comboboxtext_prices_cur.append("euro", defs.STRINGS["config_price_euros"])
                if dict_config["price_cur"] == "0":
                        comboboxtext_prices_cur.set_active(0)
                elif dict_config["price_cur"] == "1":
                        comboboxtext_prices_cur.set_active(1)
                comboboxtext_prices_cur.connect("changed", comboboxtext_prices_cur_changed)
                box_prices_cur.pack_start(label_prices_cur, False, False, 0)
                box_prices_cur.pack_start(comboboxtext_prices_cur, False, False, 0)
                box_prices.pack_start(box_prices_cur, False, True, 0)
                
                label_prices_update = Gtk.Label()
                label_prices_update.set_markup("<b>" + defs.STRINGS["config_prices_update"] + "</b>")
                box_prices.pack_start(label_prices_update, False, True, 0)
                
                checkbutton_prices_autoupdate = Gtk.CheckButton(defs.STRINGS["config_prices_autoupdate"])
                if dict_config["price_autodownload"] == "1":
                                checkbutton_prices_autoupdate.set_active(True)
                checkbutton_prices_autoupdate.connect("toggled", checkbutton_toggled, "price_autodownload")
                box_prices.pack_start(checkbutton_prices_autoupdate, False, True, 0)
                
                label_prices_last_update = Gtk.Label()
                label_prices_last_update.set_markup(defs.STRINGS["config_prices_version"].replace("%%%", defs.PRICES_DATE))
                label_prices_last_update.set_margin_top(20)
                box_prices.pack_start(label_prices_last_update, False, True, 0)
                
                download_prices_button = Gtk.Button()
                box_button = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                box_button.set_halign(Gtk.Align.CENTER)
                download_prices_button.add(box_button)
                label = Gtk.Label(defs.STRINGS["config_cardsprices_update"])
                box_button.pack_start(label, True, True, 0)
                download_prices_button.connect("clicked", down_prices_manual, box_prices, box_button, label, dict_config)
                box_prices.pack_start(download_prices_button, False, True, 0)
                
                for label in [label_prices_show, label_prices_update]:
                        label.set_alignment(0.0, 0.5)
                
                for widget in [checkbutton_show_cards_prices, box_prices_cur, checkbutton_prices_autoupdate]:
                        widget.set_margin_left(12)

def gen_columns_choice(list_current_columns, list_all_columns, param_config, column_name):
        """Generates a treeview which allows the user to change the configuration of the columns.
        
        """
        
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
