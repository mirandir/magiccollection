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

# Various functions

from gi.repository import Gtk, Gio, GdkPixbuf, Pango, GLib
from math import pi
import os
import urllib.request, urllib.parse, urllib.error
import socket
from socket import timeout
import webbrowser
import time
import tarfile
import sys

# imports def.py
import defs

if defs.OS == "mac":
        #FIXME: this is bad, bad, bad, bad, very BAD. How to simply solve the SSL: CERTIFICATE_VERIFY_FAILED error with Python on OS X ? (see http://stackoverflow.com/questions/27835619/ssl-certificate-verify-failed-error)
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context

# imports def.py
import defs
import functions.config

socket.setdefaulttimeout(5)

def check_internet():
        """Checks if we have access to the internet.
        
        """
        
        try:
                urllib.request.urlopen("http://perdu.com", timeout=2)
                return(True)
        except:
                try:
                        urllib.request.urlopen("http://www.google.com", timeout=2)
                        return(True)
                except:
                        return(False)

def download_symbols():
        """Downloads the symbols' editions.
        
        """
        
        if check_internet():               
                if os.path.isdir(os.path.join(defs.CACHEMCPIC, "icons")) == False:
                        os.mkdir(os.path.join(defs.CACHEMCPIC, "icons"))
                        GLib.idle_add(defs.MAINWINDOW.widget_overlay.get_child().set_markup, "<b><big>" + defs.STRINGS["downloading_symbols"] + "</big></b>")
                        GLib.idle_add(functions.various.force_update_gui, 0)
                        try:
                                urllib.request.urlretrieve("http://mirandir.mcollection.free.fr/images/mc/symboles_editions/all.tar", os.path.join(defs.CACHEMCPIC, "icons", "all.tar"))
                        except:
                                pass
                        else:
                                tar = tarfile.open(os.path.join(defs.CACHEMCPIC, "icons", "all.tar"))
                                for t_file_name in tar.getnames():
                                        try:
                                                tar.extract(t_file_name, os.path.join(defs.CACHEMCPIC, "icons"))
                                        except:
                                                pass
                                tar.close()
                                os.remove(os.path.join(defs.CACHEMCPIC, "icons", "all.tar"))
                
                conn, c = functions.db.connect_db()
                c.execute("""SELECT code, icon FROM editions WHERE icon = '1'""")
                reponses = c.fetchall()
                functions.db.disconnect_db(conn)
                nbicontotal = len(reponses)
                
                i = 0
                for edition in reponses:
                        if edition[1] == "1":
                                if os.path.isfile(os.path.join(defs.CACHEMCPIC, "icons", valid_filename_os(edition[0]) + ".png")) == False:
                                        GLib.idle_add(defs.MAINWINDOW.widget_overlay.get_child().set_markup, "<b><big>" + defs.STRINGS["downloading_symbols"] + " " + str(i) + "/" + str(nbicontotal) + "</big></b>")
                                        GLib.idle_add(functions.various.force_update_gui, 0)
                                        url_icon = "http://mirandir.mcollection.free.fr/images/mc/symboles_editions/" + edition[0] + ".png"
                                        try:
                                                urllib.request.urlretrieve(url_icon, os.path.join(defs.CACHEMCPIC, "icons", valid_filename_os(edition[0]) + ".png"))
                                        except:
                                                pass
                        i += 1

def valid_filename_os(name):
        """Checks if the filename is valid for the current OS, and corrects it if necessary.
        
        """
        
        if defs.OS == "windows":
                # the current OS is Windows
                # the last character must not be "." or " "
                if name[-1] == " " or name[-1] == ".":
                        name = name[:-1]
                # we replace forbiden characters
                carac_interdits = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"]
                for ci in carac_interdits:
                        name = name.replace(ci, "")
                # we change forbiden filenames
                names_forb = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]
                for ni in names_forb:
                        if name == ni:
                                name = name + "_"
                                break
                return(name)
        else:
                # the current OS is not Windows, we replace only "/"
                return(name.replace("/", ""))

def check_folders_config():
        """Checks if needed folders and config files are here.
        
        """
        
        folders = [defs.HOMEMC, defs.CONFIGMC, defs.CACHEMC, defs.CACHEMCPIC, defs.CACHEMCPR, defs.BACKUPMC]
        for folder in folders:
                if (os.path.isdir(folder)) == False:
                        os.mkdir(folder)
        
        if os.path.isfile(os.path.join(defs.CONFIGMC, "config")) == False:
                configfile = open(os.path.join(defs.CONFIGMC, "config"), "a", encoding="UTF-8")
                for param, value in defs.VARCONFIGDEFAULT.items():
                        configfile.write(param + " = " + value + "\n")
                configfile.close()
        
        if os.path.isfile(os.path.join(defs.CACHEMCPIC, "cardback.png")) ==  False:
                if check_internet():
                        try:
                                urllib.request.urlretrieve("http://mirandir.mcollection.free.fr/images/mc/cardback.png", os.path.join(defs.CACHEMCPIC, "cardback.png"))
                        except:
                                pass

def card_pic_size():
        """Returns the size wanted for a card picture.
        
        """
        
        if defs.DISPLAY_WIDTH < 1045 or defs.DISPLAY_HEIGHT < 768:
                return(200)
        else:
                return(311)

def message_dialog(message, typ):
        """Displays a message for the user. If "typ" is 1, the message is a notification about missing internet.
        
        """
        
        onaffiche = 1
        if typ == 1:
                if functions.config.read_config("not_internet_popup") == "1":
                        onaffiche = 0
        
        if onaffiche == 1:
                dialogdivers = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, message)
                if defs.MAINWINDOW != None:
                        dialogdivers.set_transient_for(defs.MAINWINDOW)
                dialogdivers.run()
                dialogdivers.destroy()

def message_exit(message):
        """Displays a message for the user, then exit MC.
        
        """
        
        message_dialog(message, 0)
        sys.exit()

def reporthook(block_no, block_size, file_size):
        """Updates the % of download for the database.
        
        """
        
        defs.DB_DOWNLOAD_PROGRESS += block_size
        pourcentage = (defs.DB_DOWNLOAD_PROGRESS / file_size) * 100
        if pourcentage > 100:
                pourcentage = 100
        if pourcentage < 0:
                pourcentage = 0
        GLib.idle_add(defs.MAINWINDOW.widget_overlay.get_child().set_markup, "<b><big>" + defs.STRINGS["downloading_db"] + " " + str(round(pourcentage)) + "%</big></b>")

def downloadPicture(multiverseid, imageurl, name, edition_code):
        URL = ""
        if imageurl != "":
                URL = imageurl
        elif multiverseid != "":
                URL = "http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=" + multiverseid + "&type=card"
        if URL == "":
                return(False)
        else:
                name_f = valid_filename_os(name)
                edition_code_f = valid_filename_os(edition_code)
                
                # we check if the folder exists
                if os.path.isdir(os.path.join(defs.CACHEMCPIC, edition_code_f)) == False:
                        os.makedirs(os.path.join(defs.CACHEMCPIC, edition_code_f))
                
                path = os.path.join(defs.CACHEMCPIC, edition_code_f, name_f + ".full.jpg")
                
                try:
                        urllib.request.urlretrieve(URL, path)
                except:
                        pass
                
                if check_card_pic(edition_code, name):
                        try:
                                pixbuf = gdkpixbuf_new_from_file(path)
                                return(True)
                        except:
                                os.remove(path)
                                return(False)
                else:
                        return(False)

def force_update_gui(s):
        """Forces to update the GUI.
        
        """
        
        while Gtk.events_pending():
                Gtk.main_iteration()
        if s != 0:
                time.sleep(s)

def edition_longname_to_code(longname):
        for code, name in defs.DICT_EDITIONS.items():
                if name[0] == longname or name[1] == longname:
                        return(code)
                        break

def edition_code_to_longname(code):
        use_french_name = functions.config.read_config("ext_fr_name")
        if use_french_name == "1":
                return(defs.DICT_EDITIONS[code][0])
        else:
                return(defs.DICT_EDITIONS[code][1])

def edition_release_date(code):
        return(defs.DICT_EDITIONS[code][2])

def edition_tcgname(code):
        return(defs.DICT_EDITIONS[code][3])

def open_link_in_browser(widget, url, popover):
        if popover != None:
                popover.hide()
        webbrowser.open_new_tab(url)
        return(True)

def check_card_pic(code, name):
        """Checks if the card's picture is already downloaded.
        
        """
        
        if os.path.isfile(os.path.join(defs.CACHEMCPIC, valid_filename_os(code), valid_filename_os(name) + ".full.jpg")):
                return(True)
        else:
                return(False)

def py_int(text):
        if text.isnumeric():
                return(int(text))

def py_remove_hyphen(text):
        return(text.replace("-", ""))

def py_lower(text):
        return(text.lower())

def py_lara(text):
        """py_lower_and_remove_accents
        
        """
        
        if text == "":
                return(text)
        else:
                return(remove_accented_char(text.lower().replace("æ", "ae").replace("œ", "oe")))

def isSQLite3(filename):
        """Checks if the file is a SQLite3 db (from https://stackoverflow.com/questions/12932607/how-to-check-with-python-and-sqlite3-if-one-sqlite-database-file-exists).
        
        """
        
        if not os.path.isfile(filename):
                return(False)
        if os.path.getsize(filename) < 100: # SQLite database file header is 100 bytes
                return(False)

        with open(filename, 'rb') as fd:
                header = fd.read(100)

        return(header[:16] == b'SQLite format 3\x00')

def remove_accented_char(texte):
        accents = { 'a': ['à', 'ã', 'á', 'â', 'ä'],
                    'e': ['é', 'è', 'ê', 'ë'],
                    'i': ['î', 'ï', 'ì', 'í', 'ĩ'],
                    'u': ['ù', 'ú', 'ü', 'û', 'ũ'],
                    'o': ['ô', 'ö', 'ó', 'ò', 'õ'],
                    'n': ['ñ'],
                    'y': ['ý'],
                    'c': ['ç'],
                    'ss': ['ß'] }
        for (char, accented_chars) in accents.items():
            for accented_char in accented_chars:
                texte = texte.replace(accented_char, char)
        return(texte)

def gen_dict_editions():
        """Dict for editions' names.
        
        """
        
        use_french_name = functions.config.read_config("ext_fr_name")
                
        conn, c = functions.db.connect_db()
        c.execute("""SELECT code, name, name_french, releasedate, tcgname FROM editions""")
        reponses = c.fetchall()
        functions.db.disconnect_db(conn)
        for info_edition in reponses:
                nom_fr_ou_en = info_edition[1]
                if use_french_name == "1":
                        if info_edition[2] != "":
                                nom_fr_ou_en = info_edition[2]
                defs.DICT_EDITIONS[info_edition[0]] = [nom_fr_ou_en, info_edition[1], info_edition[3], info_edition[4]]

def prepare_cards_data_for_treeview(cards):
        """Prepares the cards' data to be displayed in a treeview.
        
        """
        
        # we check if we must retrieve foreign names for flip / split cards
        # FIXME : chinese variants !
        foreign_name = defs.LOC_NAME_FOREIGN[functions.config.read_config("fr_language")]
        
        # we choose the foreign name
        if foreign_name == "name_chinesetrad":
                nb_foreign = 5
        elif foreign_name == "name_chinesesimp":
                nb_foreign = 6
        elif foreign_name == "name_french":
                nb_foreign = 7
        elif foreign_name == "name_german":
                nb_foreign = 8
        elif foreign_name == "name_italian":
                nb_foreign = 9
        elif foreign_name == "name_japanese":
                nb_foreign = 10
        elif foreign_name == "name_korean":
                nb_foreign = 11
        elif foreign_name == "name_portuguesebrazil":
                nb_foreign = 12
        elif foreign_name == "name_portuguese":
                nb_foreign = 13
        elif foreign_name == "name_russian":
                nb_foreign = 14
        elif foreign_name == "name_spanish":
                nb_foreign = 15
        else:
                nb_foreign = 8 # why not ?
        
        cards_ok = {}
        
        # we get the prices, if enable
        prices_downloaded = False
        if functions.prices.check_prices_presence():
                prices_downloaded = True
                ids_list_for_prices = []
                for card in cards:
                        if card[0] not in ids_list_for_prices:
                                ids_list_for_prices.append(card[0])
                dict_prices, currency = functions.prices.get_price(ids_list_for_prices)
        
        for card in cards:
                dict_card = {}
                
                id_ = card[0]
                
                real_name = card[1]
                name = card[1]
                # we choose the foreign name
                nameforeign = card[nb_foreign]
                
                nameforeign_r = str(nameforeign)
                names_r = card[3]
                colors = card[16]
                
                layout = card[29]
                if layout == "flip" or layout == "split":
                        if layout == "flip":
                                separator = " <> "
                        elif layout == "split":
                                separator = " // "
                        
                        names = card[3].split("|")
                        final_name = ""
                        final_colors = ""
                        if layout == "split":
                                for nn in names:
                                        final_name = final_name + separator + nn
                                name = final_name[4:]
                        elif layout == "flip":
                                final_name = real_name
                                for nn in names:
                                        if nn != real_name:
                                                final_name = final_name + separator + nn
                                name = final_name
                        
                        for nn in names:
                                for card_split_flip in defs.SPLIT_FLIP_DF_DATA:
                                        if card_split_flip[4] == card[4]:
                                                if nn == card_split_flip[1]:
                                                        for char in card_split_flip[16]:
                                                                if char not in final_colors:
                                                                        final_colors = final_colors + char
                        colors = "".join(sorted(final_colors))
                        
                        if nameforeign == "":
                                nameforeign = name
                        else:
                                final_nameforeign = ""
                                if layout == "split":
                                        for nn in names:
                                                for card_split_flip in defs.SPLIT_FLIP_DF_DATA:
                                                        if card_split_flip[4] == card[4]:
                                                                if nn == card_split_flip[1]:
                                                                        final_nameforeign = final_nameforeign + separator + card_split_flip[nb_foreign]
                                        nameforeign = final_nameforeign[4:]
                                elif layout == "flip":
                                        final_nameforeign = nameforeign_r
                                        for nn in names:
                                                for card_split_flip in defs.SPLIT_FLIP_DF_DATA:
                                                        if card_split_flip[4] == card[4]:
                                                                if nn == card_split_flip[1]:
                                                                        if card_split_flip[nb_foreign] != nameforeign_r:
                                                                                final_nameforeign = final_nameforeign + separator + card_split_flip[nb_foreign]
                                        nameforeign = final_nameforeign
                
                if nameforeign == "":
                        nameforeign = name
                if card[2] != "":
                        name = name + " (" + card[2] + ")"
                        nameforeign = nameforeign + " (" + card[2] + ")"
                
                edition_code = card[4]
                edition_ln = edition_code_to_longname(edition_code)
                if card[16] != "":
                        pix_colors = gdkpixbuf_new_from_file(os.path.join(defs.PATH_MC, "images", "color_indicators", colors.lower() + ".png"))
                else:
                        pix_colors = gdkpixbuf_new_from_file(os.path.join(defs.PATH_MC, "images", "nothing.png"))
                cmc = card[18]
                type_ = card[21]
                artist = card[22]
                text = card[23]
                power = card[25]
                toughness = card[26]
                rarity = card[28]
                if rarity == "Mythic Rare":
                        rarity = defs.STRINGS["mythic"]
                elif rarity == "Rare":
                        rarity = defs.STRINGS["rare"]
                elif rarity == "Uncommon":
                        rarity = defs.STRINGS["uncommon"]
                elif rarity == "Common":
                        rarity = defs.STRINGS["common"]
                elif rarity == "Basic Land":
                        rarity = defs.STRINGS["basic_land"]
                elif rarity == "Special":
                        rarity = defs.STRINGS["special"]
                
                coll_ed_nb = card[30]
                
                if prices_downloaded:
                        try:
                                price = float(dict_prices[id_])
                        except:
                                price = float(0)
                else:
                        price = float(0)
                
                dict_card["id_"] = id_
                dict_card["name"] = name
                dict_card["edition_ln"] = edition_ln
                dict_card["edition_code"] = edition_code
                dict_card["release_date"] = edition_release_date(edition_code).replace("-", "")
                dict_card["nameforeign"] = nameforeign
                dict_card["colors"] = colors
                dict_card["pix_colors"] = pix_colors
                dict_card["cmc"] = int(cmc.replace("0.5", "1"))
                dict_card["type_"] = type_
                dict_card["artist"] = artist
                dict_card["power"] = str(power)
                dict_card["toughness"] = str(toughness)
                dict_card["rarity"] = rarity
                dict_card["layout"] = layout
                dict_card["names"] = names_r
                dict_card["real_name"] = real_name
                dict_card["nb_variant"] = str(card[2])
                dict_card["names"] = names_r
                dict_card["text"] = text
                dict_card["coll_ed_nb"] = coll_ed_nb
                dict_card["price"] = price
                
                cards_ok[id_] = dict_card
                force_update_gui(0)
        
        return(cards_ok)

def draw_rounded(context, x, y, w, h, radius_x, radius_y):
        ARC_TO_BEZIER = 0.55228475
        if radius_x > w - radius_x:
                radius_x = w / 2
        if radius_y > h - radius_y:
                radius_y = h / 2

        #approximate (quite close) the arc using a bezier curve
        c1 = ARC_TO_BEZIER * radius_x
        c2 = ARC_TO_BEZIER * radius_y

        context.new_path();
        context.move_to ( x + radius_x, y)
        context.rel_line_to ( w - 2 * radius_x, 0.0)
        context.rel_curve_to ( c1, 0.0, radius_x, c2, radius_x, radius_y)
        context.rel_line_to ( 0, h - 2 * radius_y)
        context.rel_curve_to ( 0.0, c2, c1 - radius_x, radius_y, -radius_x, radius_y)
        context.rel_line_to ( -w + 2 * radius_x, 0)
        context.rel_curve_to ( -c1, 0, -radius_x, -c2, -radius_x, -radius_y)
        context.rel_line_to (0, -h + 2 * radius_y)
        context.rel_curve_to (0.0, -c2, radius_x - c1, -radius_y, radius_x, -radius_y)
        context.close_path()
        context.clip()

def rotate_card_pic(gtkimage):
        """90° clock rotation.
        
        """
        
        pixbuf = gtkimage.get_pixbuf()
        pixbuf = pixbuf.rotate_simple(GdkPixbuf.PixbufRotation.CLOCKWISE)
        gtkimage.set_from_pixbuf(pixbuf)

def vertical_flip_pic(gtkimage):
        """180° clock rotation.
        
        """
        
        pixbuf = gtkimage.get_pixbuf()
        pixbuf = pixbuf.rotate_simple(GdkPixbuf.PixbufRotation.UPSIDEDOWN)
        gtkimage.set_from_pixbuf(pixbuf)

def compare_str_osx(model, row1, row2, user_data):
        """This function compares two strings without accent. It's used only on macOS, where the default GTK sort functions seem bugus.
        
        """
        
        sort_column, _ = model.get_sort_column_id()
        value1 = py_lara(model.get_value(row1, sort_column))
        value2 = py_lara(model.get_value(row2, sort_column))
        
        if value1 < value2:
                return(-1)
        elif value1 == value2:
                return(0)
        else:
                return(1)

def compare_str_and_int(model, row1, row2, user_data):
        """This function compares a list of strings and int. int values are sorted first.
        
        """
        
        def isFloat(string):
                try:
                        float(string)
                        return(True)
                except ValueError:
                        return(False)
        
        sort_column, _ = model.get_sort_column_id()
        value1 = model.get_value(row1, sort_column)
        value2 = model.get_value(row2, sort_column)
        
        if value1 == "" and value2 != "":
                return(1)
        
        if value1 != "" and value2 == "":
                return(-1)
        
        if isFloat(value1) == True and isFloat(value2) == True:
                if float(value1) < float(value2):
                        return(1)
                elif float(value1) == float(value2):
                        return(0)
                else:
                        return(-1)
        
        if isFloat(value1) == False and isFloat(value2) == False:
                if value1 < value2:
                        return(-1)
                elif value1 == value2:
                        return(0)
                else:
                        return(1)
        
        if isFloat(value1) == True and isFloat(value2) == False:
                return(1)
        if isFloat(value1) == False and isFloat(value2) == True:
                return(-1)

def get_foreign_name_label():
        foreign_name = defs.LOC_NAME_FOREIGN[functions.config.read_config("fr_language")]
        # we choose the name of column_name_foreign 
        if foreign_name == "name_chinesetrad":
                foreign__name_label = defs.STRINGS["column_name_name_chinesetrad"]
        elif foreign_name == "name_chinesesimp":
                foreign__name_label = defs.STRINGS["column_name_name_chinesesimp"]
        elif foreign_name == "name_french":
                foreign__name_label = defs.STRINGS["column_name_name_french"]
        elif foreign_name == "name_german":
                foreign__name_label = defs.STRINGS["column_name_name_german"]
        elif foreign_name == "name_italian":
                foreign__name_label = defs.STRINGS["column_name_name_italian"]
        elif foreign_name == "name_japanese":
                foreign__name_label = defs.STRINGS["column_name_name_japanese"]
        elif foreign_name == "name_korean":
                foreign__name_label = defs.STRINGS["column_name_name_korean"]
        elif foreign_name == "name_portuguesebrazil":
                foreign__name_label = defs.STRINGS["column_name_name_portuguesebrazil"]
        elif foreign_name == "name_portuguese":
                foreign__name_label = defs.STRINGS["column_name_name_portuguese"]
        elif foreign_name == "name_russian":
                foreign__name_label = defs.STRINGS["column_name_name_russian"]
        elif foreign_name == "name_spanish":
                foreign__name_label = defs.STRINGS["column_name_name_spanish"]
        else:
                foreign__name_label = defs.STRINGS["column_name_name_german"] # why not ?

        return foreign__name_label

def gen_treeview_columns(columns_to_display, treeview):
        """Generates the columns for a treeview which displays cards' data.

        """

        dict_columns_list = {}
        dict_renderers_list = {}
        w = 12
        s = 13

        def display_column(x, y, name, label, text, expand):
                renderer_text = Gtk.CellRendererText()
                renderer_text.set_fixed_size(x, y)
                column_name = Gtk.TreeViewColumn(label, renderer_text, text=text, weight=w, style = s)
                dict_columns_list[name] = column_name
                dict_renderers_list[name] = renderer_text
                column_name.set_sort_column_id(text)
                column_name.set_expand(expand)

                return column_name

        if "id_coll" in columns_to_display:
                w = 11
                s = 12
                renderer_text_id = Gtk.CellRendererText()
                renderer_text_id.set_fixed_size(20, 25)
                column_id = Gtk.TreeViewColumn(defs.STRINGS["column_internal_id"], renderer_text_id, text=0, weight=w, style=s)
                dict_columns_list["id_coll"] = column_id
                dict_renderers_list["id_coll"] = renderer_text_id
                #column_id.set_expand(True)

        if "name" in columns_to_display:
                display_column(145, 25, "name", defs.STRINGS["column_english_name"], 1, True)

        if "edition" in columns_to_display:
                display_column(80, 25, "edition", defs.STRINGS["column_edition"], 2, True)

        if "name_foreign" in columns_to_display:
                foreign__name_label = get_foreign_name_label()
                display_column(195, 25, "name_foreign", foreign__name_label, 3, True)

        if "colors" in columns_to_display:
                renderer_pixbuf_colors = Gtk.CellRendererPixbuf()
                renderer_pixbuf_colors.set_fixed_size(10, 25)
                column_colors = Gtk.TreeViewColumn(defs.STRINGS["column_colors"], renderer_pixbuf_colors, pixbuf=5)
                dict_columns_list["colors"] = column_colors
                dict_renderers_list["colors"] = renderer_pixbuf_colors
                column_colors.set_sort_column_id(4)

        if "cmc" in columns_to_display:
                display_column(20, 25, "cmc", defs.STRINGS["column_cmc"], 6, True)

        if "type" in columns_to_display:
                display_column(100, 25, "type", defs.STRINGS["column_type"], 7, True)

        if "artist" in columns_to_display:
                display_column(50, 25, "artist", defs.STRINGS["column_artist"], 8, True)

        if "power" in columns_to_display:
                pic_power = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="power-symbolic"), Gtk.IconSize.MENU)
                pic_power.show()
                column_power = display_column(10, 25, "power", defs.STRINGS["column_power"], 9, False)
                column_power.set_widget(pic_power)

        if "toughness" in columns_to_display:
                pic_toughness = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="toughness-symbolic"), Gtk.IconSize.MENU)
                pic_toughness.show()
                column_toughness = display_column(10, 25, "toughness", defs.STRINGS["column_toughness"], 10, False)
                column_toughness.set_widget(pic_toughness)

        if "rarity" in columns_to_display:
                display_column(30, 25, "rarity", defs.STRINGS["column_rarity"], 11, False)

        if "nb" in columns_to_display:
                display_column(10, 25, "nb", defs.STRINGS["column_nb"], 15, False)

        if "coll_ed_nb" in columns_to_display:
                display_column(30, 25, "coll_ed_nb", defs.STRINGS["column_coll_ed_nb"], 18, False)

        if "price" in columns_to_display:
                renderer_text_price = Gtk.CellRendererText()
                renderer_text_price.set_fixed_size(30, 25)
                label_col = defs.STRINGS["column_prices"]
                if functions.prices.check_prices_presence():
                        price_cur = functions.config.read_config("price_cur")
                        if price_cur == "0":
                                label_col = "$"
                        elif price_cur == "1":
                                label_col = "€"
                column_price = Gtk.TreeViewColumn(label_col, renderer_text_price, text=19, weight=w, style=s)
                dict_columns_list["price"] = column_price
                dict_renderers_list["price"] = renderer_text_price
                column_price.set_sort_column_id(19)
                column_price.set_cell_data_func(renderer_text_price, \
                lambda col, cell, model, iter, unused:
                cell.set_property("text",
                "{0}".format(truncate(model.get(iter, 19)[0]))))

        for column in columns_to_display:
                treeview.append_column(dict_columns_list[column])

        for name, column in dict_columns_list.items():
                column.set_resizable(True)

        return([dict_columns_list, dict_renderers_list])

def truncate(number):
        """Rounds and truncates a number to one decimal place. Used for all float numbers in the data-view. The numbers are saved with full float precision (from http://stackoverflow.com/questions/27675919/how-to-limit-number-of-decimal-places-to-be-displayed-in-gtk-cellrenderertext/28413823#28413823).
        
        """
        
        number = round(number, 3)
        return(number)

def create_window_search_name(request_response, current_object_view):
        """Generates the window for diplaying the results of a simple search.
        
        """
        
        def select_choice_card(selection, integer, TreeViewColumn, button_choose):
                button_choose.set_sensitive(True)
        
        def button_choose_click(button, select, current_object_view, window):
                model, treeiter = select.get_selected()
                if treeiter != None:
                        id_ = model[treeiter][0]
                        current_object_view.load_card(id_, 1)
                        window.destroy()
        
        def row_activated(a, b, c, select, current_object_view, window):
                button_choose_click(None, select, current_object_view, window)
        
        window = Gtk.Dialog()
        if defs.DISPLAY_WIDTH > 1279:
                window.set_default_size(800, 400)
        else:
                window.set_default_size(620, 250)
        window.set_title(defs.STRINGS["search_card"])
        content = window.get_content_area()
        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content.add(mainbox)
        
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_min_content_width(560)
        scrolledwindow.set_min_content_height(180)
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
        # "id", "name", "edition", "name_nonenglish", "colors", colors_pixbuf, "cmc", "type", "artist", "power", "toughness", "rarity", "bold", "italic", unused1, unused2, unused3, unused4, "coll_ed_nb", "price"
        store_results = Gtk.ListStore(str, str, str, str, str, GdkPixbuf.Pixbuf, int, str, str, str, str, str, int, Pango.Style, str, int, str, str, str, float)
        tree_results = Gtk.TreeView(store_results)
        tree_results.set_enable_search(True)
        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                tree_results.set_search_column(3)
        else:
                tree_results.set_search_column(1)
        
        # some work with columns
        columns_to_display = defs.as_columns.split(";")
        
        as_columns_list = gen_treeview_columns(columns_to_display, tree_results)[0]
        
        select = tree_results.get_selection()
        scrolledwindow.add(tree_results)
        tree_results.connect("row-activated", row_activated, select, current_object_view, window)
        
        tree_results.show_all()
        scrolledwindow.show_all()
        
        nb = 0
        cards_added = []
        cards_added_reprints = []
        cards = prepare_cards_data_for_treeview(request_response)
        
        no_reprints = functions.config.read_config("no_reprints")
        # if the user doesn't want reprints, we delete every reprint but the most recent
        if no_reprints == "1":
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
        
        # we get a list of ids of cards in the collection
        conn, c = functions.collection.connect_db()
        c.execute("""SELECT id_card FROM collection""")
        reponses_coll = c.fetchall()
        functions.collection.disconnect_db(conn)
        
        for card in cards.values():
                bold = 400
                for row_id_card in reponses_coll:
                        id_card = row_id_card[0]
                        if id_card == card["id_"]:
                                bold = 700
                                break
                italic = Pango.Style.NORMAL
                
                add = True
                
                if card["name"] + "-" + card["nb_variant"] + "-" + card["edition_ln"] in cards_added:
                        add = False
                
                if add:
                        store_results.insert_with_valuesv(-1, range(21), [card["id_"], card["name"], card["edition_ln"], card["nameforeign"], card["colors"], card["pix_colors"], card["cmc"], card["type_"], card["artist"], card["power"], card["toughness"], card["rarity"], bold, italic, "", 0, "", "", card["coll_ed_nb"], 0])
                        cards_added.append(card["name"] + "-" + card["nb_variant"] + "-" + card["edition_ln"])
                        nb += 1
        
        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                store_results.set_sort_column_id(3, Gtk.SortType.ASCENDING)
        else:
                store_results.set_sort_column_id(1, Gtk.SortType.ASCENDING)
        
        if defs.OS == "mac":
                store_results.set_sort_func(3, compare_str_osx, None)
        
        label_nb_cards = Gtk.Label(defs.STRINGS["results"].replace("%%%", str(nb)))
        mainbox.pack_start(label_nb_cards, False, False, 0)
        
        mainbox.pack_start(scrolledwindow, True, True, 0)
        
        button_choose = Gtk.Button(defs.STRINGS["choose_card"])
        button_choose.set_sensitive(False)
        
        select.connect("changed", select_choice_card, "blip", "blop", button_choose)
        button_choose.connect("clicked", button_choose_click, select, current_object_view, window)
        mainbox.pack_start(button_choose, False, False, 0)
        mainbox.show_all()
        
        if defs.MAINWINDOW != None:
                window.set_transient_for(defs.MAINWINDOW)
        return(window, nb, store_results)

def gen_details_widgets():
        """Generates and returns a Gtk.Grid with all the widget for the details of a card.
        
        """
        
        def checkbutton_loaned_toggled(cb, entry_loaned):
                if cb.get_active():
                        entry_loaned.set_sensitive(True)
                else:
                        entry_loaned.set_sensitive(False)
        
        grid_details = Gtk.Grid()
        grid_details.set_row_spacing(6)
        grid_details.set_column_spacing(12)
        
        label_add_condition = Gtk.Label(defs.STRINGS["add_condition"])
        grid_details.attach(label_add_condition, 0, 0, 1, 1)
        
        comboboxtext_condition = Gtk.ComboBoxText()
        for i in range(len(defs.CONDITIONS)):
                comboboxtext_condition.append(defs.CONDITIONS[i][0], defs.CONDITIONS[i][1])
        grid_details.attach_next_to(comboboxtext_condition, label_add_condition, Gtk.PositionType.RIGHT, 1, 1)
        
        label_add_lang = Gtk.Label(defs.STRINGS["add_lang"])
        label_add_lang.props.halign = Gtk.Align.END
        grid_details.attach_next_to(label_add_lang, comboboxtext_condition, Gtk.PositionType.RIGHT, 1, 1)
        
        entry_lang = Gtk.Entry()
        grid_details.attach_next_to(entry_lang, label_add_lang, Gtk.PositionType.RIGHT, 1, 1)
        
        checkbutton_foil = Gtk.CheckButton(label=defs.STRINGS["add_foil"])
        grid_details.attach_next_to(checkbutton_foil, label_add_condition, Gtk.PositionType.BOTTOM, 2, 1)
        
        checkbutton_loaned = Gtk.CheckButton(label=defs.STRINGS["add_loaned"])
        checkbutton_loaned.props.halign = Gtk.Align.END
        grid_details.attach_next_to(checkbutton_loaned, checkbutton_foil, Gtk.PositionType.RIGHT, 1, 1)
        
        entry_loaned = Gtk.Entry()
        checkbutton_loaned.connect("toggled", checkbutton_loaned_toggled, entry_loaned)
        entry_loaned.set_sensitive(False)
        grid_details.attach_next_to(entry_loaned, checkbutton_loaned, Gtk.PositionType.RIGHT, 1, 1)
        
        update_entrycompletions(entry_lang, entry_loaned)
        
        label_add_comment = Gtk.Label(defs.STRINGS["add_comment"])
        grid_details.attach_next_to(label_add_comment, checkbutton_foil, Gtk.PositionType.BOTTOM, 4, 1)
        
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_min_content_height(75)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
        textview = Gtk.TextView()
        textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        scrolledwindow.add(textview)
        grid_details.attach_next_to(scrolledwindow, label_add_comment, Gtk.PositionType.BOTTOM, 4, 1)
        
        return(grid_details, label_add_condition, comboboxtext_condition, label_add_lang, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, label_add_comment, scrolledwindow, textview)

def lock_db(lock_coll, lock_cards):
        """This function locks the database of the collection and/or the database of cards.
        
        @lock_coll and @lock_cards can be: True (we lock the db), False (we unlock the db), None (we do nothing).
        
        """
        
        if lock_cards == True:
                defs.AS_LOCK = True
        elif lock_cards == False:
                defs.AS_LOCK = False
        
        if lock_coll == True:
                defs.COLL_LOCK = True
        elif lock_coll == False:
                defs.COLL_LOCK = False
                if defs.BUTTON_COLL_LOCK != None:
                        GLib.idle_add(defs.BUTTON_COLL_LOCK.set_label, defs.STRINGS["add_button_validate"])
                        GLib.idle_add(defs.BUTTON_COLL_LOCK.set_sensitive, True)

def update_entrycompletions(entry_lang, entry_loaned):
        """Retrieves a list of each language and each "loaned to" already writed in the collection, and add it to the entries.
        
        """
        
        conn, c = functions.collection.connect_db()
        c.execute("""SELECT lang, loaned_to FROM collection WHERE lang != \"\"""")
        reponses_lang = c.fetchall()
        c.execute("""SELECT loaned_to FROM collection WHERE loaned_to != \"\"""")
        reponses_loaned = c.fetchall()
        functions.collection.disconnect_db(conn)
        
        list_entrycompletion_lang = [defs.STRINGS["l_english"], defs.STRINGS["l_chinese"], defs.STRINGS["l_french"], defs.STRINGS["l_german"], defs.STRINGS["l_italian"], defs.STRINGS["l_japanese"], defs.STRINGS["l_korean"], defs.STRINGS["l_portuguese"], defs.STRINGS["l_russian"], defs.STRINGS["l_spanish"]]
        for data in reponses_lang:
                if data[0] not in list_entrycompletion_lang:
                        list_entrycompletion_lang.append(data[0])
        list_entrycompletion_loaned = []
        for data in reponses_loaned:
                if data[0] not in list_entrycompletion_loaned:
                        list_entrycompletion_loaned.append(data[0])
        
        liststore_lang = Gtk.ListStore(str)
        entrycompletion_lang = Gtk.EntryCompletion()
        entrycompletion_lang.set_model(liststore_lang)
        entrycompletion_lang.set_text_column(0)
        for elm in list_entrycompletion_lang:
                liststore_lang.append([elm])
        entry_lang.set_completion(entrycompletion_lang)
        
        liststore_loaned = Gtk.ListStore(str)
        entrycompletion_loaned = Gtk.EntryCompletion()
        entrycompletion_loaned.set_model(liststore_loaned)
        entrycompletion_loaned.set_text_column(0)
        for elm in list_entrycompletion_loaned:
                liststore_loaned.append([elm])
        entry_loaned.set_completion(entrycompletion_loaned)

def gen_entrycompletion_editions(adsearch_item):
        """We generate the completion for the GtkEntry 'editions'.
        
        """
        
        liststore_edition = Gtk.ListStore(str)
        entrycompletion_edition = Gtk.EntryCompletion()
        entrycompletion_edition.set_match_func(matchfunc_custom, 0)
        entrycompletion_edition.set_minimum_key_length(3)
        entrycompletion_edition.set_model(liststore_edition)
        entrycompletion_edition.set_text_column(0)
        for elm in adsearch_item.list_entrycompletion_editions:
                liststore_edition.append([elm])
        return(entrycompletion_edition)

def matchfunc_custom(completion, key, iter, column):
        """We check when we have to pop one or more edition's name.
        
        """
        
        model = completion.get_model()
        ed_name = model.get_value(iter, column)
        if py_lara(key) in py_lara(ed_name):
                return(True)
        else:
                return(False)

def gdkpixbuf_new_from_file(path):
        """We wrap GdkPixbuf.Pixbuf.new_from_file, because it's not the same function on Windows. We return a GdkPixbuf.Pixbuf.
        
        """
        
        if defs.OS == "windows":
                return(GdkPixbuf.Pixbuf.new_from_file_utf8(path))
        else:
                return(GdkPixbuf.Pixbuf.new_from_file(path))

def gdkpixbuf_new_from_file_at_size(path, width, height):
        """We wrap GdkPixbuf.Pixbuf.new_from_file_at_size, because it's not the same function on Windows. We return a GdkPixbuf.Pixbuf.
        
        """
        
        if defs.OS == "windows":
                return(GdkPixbuf.Pixbuf.new_from_file_at_size_utf8(path, width, height))
        else:
                return(GdkPixbuf.Pixbuf.new_from_file_at_size(path, width, height))

def clear_gui_del():
        """Erase many elements of the interface.
        
        """
        
        if defs.MAINWINDOW.advancedsearch.mainstore != None:
                for line in defs.MAINWINDOW.advancedsearch.mainstore:
                        if line[12] == 700:
                                line[12] = 400
                if defs.MAINWINDOW.advancedsearch.mainselect != None:
                        defs.MAINWINDOW.advancedsearch.mainselect.emit("changed")
        
        if defs.MAINWINDOW.decks.mainstore != None:
                defs.MAINWINDOW.decks.label_nb_cards.set_text(defs.STRINGS["nb_cards_in_deck"].replace("%%%", "0"))
                defs.MAINWINDOW.decks.mainstore.clear()
        defs.MAINWINDOW.decks.gen_list_decks(None)
        
        try:
                defs.MAINWINDOW.collection.label_nb_card_coll.set_text(defs.STRINGS["nb_card_coll"].replace("%%%", "0"))
        except:
                pass
        try:
                if defs.MAINWINDOW.collection.tree_coll.get_model() == defs.MAINWINDOW.collection.searchstore:
                        defs.MAINWINDOW.collection.button_back_coll.emit("clicked")
        except:
                pass
        if defs.MAINWINDOW.collection.mainstore != None:
                defs.MAINWINDOW.collection.mainselect.set_mode(Gtk.SelectionMode.NONE)
                defs.MAINWINDOW.collection.mainstore.clear()
                defs.MAINWINDOW.collection.mainselect.set_mode(Gtk.SelectionMode.MULTIPLE)

def show_tips_window(mc):
        """Generates and displays the tips' window.
        
        """
        
        if mc.tips == None:
                tips_dialog = Gtk.Dialog()
                mc.tips = tips_dialog
                tips_dialog.set_default_size(200, -1)
                tips_dialog.set_title(defs.STRINGS["tips"])
                tips_dialog.set_icon_name("magic_collection")
                if defs.MAINWINDOW != None:
                        tips_dialog.set_transient_for(defs.MAINWINDOW)
                        tips_dialog.set_modal(True)
                notebook = Gtk.Notebook()
                
                scrolledwindow_general = Gtk.ScrolledWindow()
                scrolledwindow_general.set_min_content_width(650)
                scrolledwindow_general.set_min_content_height(300)
                scrolledwindow_general.set_hexpand(False)
                scrolledwindow_general.set_vexpand(True)
                scrolledwindow_general.set_shadow_type(Gtk.ShadowType.IN)
                box_general = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                label_general = Gtk.Label(defs.STRINGS["tips_general_text"])
                box_general.pack_start(label_general, False, True, 0)
                scrolledwindow_general.add(box_general)
                notebook.append_page(scrolledwindow_general, Gtk.Label(defs.STRINGS["tips_general"]))
                
                scrolledwindow_search = Gtk.ScrolledWindow()
                scrolledwindow_search.set_min_content_width(650)
                scrolledwindow_search.set_min_content_height(300)
                scrolledwindow_search.set_hexpand(False)
                scrolledwindow_search.set_vexpand(True)
                scrolledwindow_search.set_shadow_type(Gtk.ShadowType.IN)
                box_search = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                tmp_text_for_label_search = ""
                for text in [defs.STRINGS["tips_search_text_partname"], defs.STRINGS["tips_search_text_nonenglishname"], defs.STRINGS["tips_search_text_logicop"], defs.STRINGS["tips_search_text_op"], defs.STRINGS["tips_search_text_null"], defs.STRINGS["tips_search_text_spetext"], defs.STRINGS["tips_search_text_rarity"], defs.STRINGS["tips_search_text_manacost"], defs.STRINGS["tips_search_text_colors"], defs.STRINGS["tips_search_text_condition"]]:
                        if text != "":
                                tmp_text_for_label_search = tmp_text_for_label_search + "\n\n" + text
                tmp_text_for_label_search = tmp_text_for_label_search[2:]
                label_search = Gtk.Label(tmp_text_for_label_search)
                box_search.pack_start(label_search, False, True, 0)
                scrolledwindow_search.add(box_search)
                notebook.append_page(scrolledwindow_search, Gtk.Label(defs.STRINGS["tips_search"]))
                
                scrolledwindow_proxies = Gtk.ScrolledWindow()
                scrolledwindow_proxies.set_min_content_width(650)
                scrolledwindow_proxies.set_min_content_height(300)
                scrolledwindow_proxies.set_hexpand(False)
                scrolledwindow_proxies.set_vexpand(True)
                scrolledwindow_proxies.set_shadow_type(Gtk.ShadowType.IN)
                box_proxies = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                label_proxies = Gtk.Label(defs.STRINGS["tips_proxies_text"])
                box_proxies.pack_start(label_proxies, False, True, 0)
                scrolledwindow_proxies.add(box_proxies)
                notebook.append_page(scrolledwindow_proxies, Gtk.Label(defs.STRINGS["tips_proxies"]))
                
                for label in [label_general, label_search, label_proxies]:
                        label.set_line_wrap(True)
                        label.set_width_chars(75)
                        label.set_selectable(True)
                
                for box in [box_general, box_search, box_proxies]:
                        box.props.border_width = 12
                
                content_area = tips_dialog.get_content_area()
                content_area.props.border_width = 0
                content_area.pack_start(notebook, True, True, 0)
                
                notebook.show_all()
                tips_dialog.run()
                tips_dialog.destroy()
                mc.tips = None
        else:
                mc.tips.present()

def show_shortcuts_window(mc):
        """Generates and displays the window with shortcuts.
        
        """
        
        def delete_shortwin(shortwin, event, mc, *args):
                mc.shortcutswindow = None
                shortwin.destroy()
                return(False)
        
        if mc.shortcutswindow == None:
                shortwin = Gtk.ShortcutsWindow()
                mc.shortcutswindow = shortwin
                shortwin.set_icon_name("magic_collection")
                if defs.MAINWINDOW != None:
                        shortwin.set_transient_for(defs.MAINWINDOW)
                        shortwin.set_modal(True)
                shortwin.connect("delete-event", delete_shortwin, mc)
                
                section = Gtk.ShortcutsSection()
                group = Gtk.ShortcutsGroup()
                group.props.title = defs.STRINGS["shortcuts_globals"]
                section.add(group)
                
                shortkey_simple_search = Gtk.ShortcutsShortcut(Gtk.ShortcutType.ACCELERATOR)
                shortkey_simple_search.props.accelerator = "<Control>f"
                shortkey_simple_search.props.title = defs.STRINGS["shortcuts_simple_search"]
                
                shortkey_collection_mode = Gtk.ShortcutsShortcut(Gtk.ShortcutType.ACCELERATOR)
                shortkey_collection_mode.props.accelerator = "<Alt>c"
                shortkey_collection_mode.props.title = defs.STRINGS["shortcuts_switch_collection"]
                
                shortkey_decks_mode = Gtk.ShortcutsShortcut(Gtk.ShortcutType.ACCELERATOR)
                shortkey_decks_mode.props.accelerator = "<Alt>d"
                shortkey_decks_mode.props.title = defs.STRINGS["shortcuts_switch_decks"]
                
                shortkey_as_mode = Gtk.ShortcutsShortcut(Gtk.ShortcutType.ACCELERATOR)
                shortkey_as_mode.props.accelerator = "<Alt>s"
                shortkey_as_mode.props.title = defs.STRINGS["shortcuts_switch_adsearch"]
                
                for widget in [section, group, shortkey_simple_search, shortkey_collection_mode, shortkey_decks_mode, shortkey_as_mode]:
                        widget.show()
                
                for shortkey in [shortkey_simple_search, shortkey_collection_mode, shortkey_decks_mode, shortkey_as_mode]:
                        group.add(shortkey)
                        
                shortwin.add(section)
                
                shortwin.show()
        else:
                mc.shortcutswindow.present()
