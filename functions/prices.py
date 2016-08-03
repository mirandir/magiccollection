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

# Some functions for dealing with the prices of the cards

import os
import urllib.request, urllib.parse, urllib.error
from socket import timeout
import tarfile
from distutils.version import StrictVersion
import sqlite3
from gi.repository import Gtk, GLib
import threading

import defs
import functions.various

def check_prices_presence():
        """Checks if the prices have been downloaded.
        
        """
        
        if os.path.isfile(os.path.join(defs.CACHEMCPR, "dateprices")):
                fileprices = open(os.path.join(defs.CACHEMCPR, "dateprices"), "r", encoding="UTF-8")
                date_prices = fileprices.read(8)
                fileprices.close()
                
                if os.path.isfile(os.path.join(defs.CACHEMCPR, "prices_" + date_prices + ".sqlite")):
                        if functions.various.isSQLite3(os.path.join(defs.CACHEMCPR, "prices_" + date_prices + ".sqlite")):
                                defs.PRICES_DATE = date_prices
                                return(True)
                        else:
                                defs.PRICES_DATE = None
                                return(False)
                else:
                        defs.PRICES_DATE = None
                        return(False)
        else:
                defs.PRICES_DATE = None
                return(False)

def connect_db():
        """ Returns the connection to the DB and the cursor.
        
        """
        
        filename = os.path.join(defs.CACHEMCPR, "prices_" + defs.PRICES_DATE + ".sqlite")
        if functions.various.isSQLite3(filename):
                conn = sqlite3.connect(filename)
                conn.create_function('py_lara', 1, functions.various.py_lara)
                conn.create_function('py_int', 1, functions.various.py_int)
                conn.create_function('py_lower', 1, functions.various.py_lower)
                conn.create_function('py_remove_hyphen', 1, functions.various.py_remove_hyphen)
                c = conn.cursor()
                return(conn, c)
        else:
                os.remove(filename)
                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["prices_db_damaged"], 0)

def disconnect_db(conn):
        conn.commit()
        conn.close()

def check_prices(orig):
        """Function which checks if the prices are here, up to date, and launches download if not.
        
        @orig is either "silent", "manual", "auto".
        
        """
        
        if os.path.isfile(os.path.join(defs.CACHEMCPR, "dateprices")) == False:
                download_prices(orig)
        else:
                fileprices = open(os.path.join(defs.CACHEMCPR, "dateprices"), "r", encoding="UTF-8")
                date_prices = fileprices.read(8)
                fileprices.close()
                if os.path.isfile(os.path.join(defs.CACHEMCPR, "prices_" + date_prices + ".sqlite")) == False:
                        download_prices(orig)
                else:
                        check_update_prices(orig)

def download_prices(orig):
        """Downloads the prices of the cards.
        
        @orig is either "silent", "manual", "auto".
        
        """
        
        defs.DB_DOWNLOAD_PROGRESS = 0
        go = 1
        if functions.various.check_internet():
                if orig == "auto":
                        GLib.idle_add(defs.MAINWINDOW.widget_overlay.get_child().set_markup, "<b><big>" + defs.STRINGS["config_cardsprices_downloading"] + "</big></b>")
                
                if os.path.isfile(os.path.join(defs.CACHEMCPR, "dateprices_newtmp")) == False:
                        try:
                                urllib.request.urlretrieve(defs.SITEMC + "files/dateprices", os.path.join(defs.CACHEMCPR, "dateprices_newtmp"))
                        except:
                                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["error_download_db_prices"], 0)
                                go = 0
                if go == 1:
                        filepricesdb_tmp = open(os.path.join(defs.CACHEMCPR, "dateprices_newtmp"), "r", encoding="UTF-8")
                        datedbprices_new = filepricesdb_tmp.read(8)
                        filepricesdb_tmp.close()
                        if os.path.isfile(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_new + ".sqlite.tar.xz_newtmp")):
                                os.remove(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_new + ".sqlite.tar.xz_newtmp"))
                        
                        try:
                                urllib.request.urlretrieve(defs.SITEMC + "files/prices_" + datedbprices_new + ".sqlite.tar.xz", os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_new + ".sqlite.tar.xz_newtmp"))
                                #urllib.request.urlretrieve(defs.SITEMC + "files/prices_" + datedbprices_new + ".sqlite.tar.xz", os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_new + ".sqlite.tar.xz_newtmp"), functions.various.reporthook)# changer ça en fonction de orig
                                if os.path.isfile(os.path.join(defs.CACHEMCPR, "dateprices")):
                                        filepricesdb_old = open(os.path.join(defs.CACHEMCPR, "dateprices"), "r", encoding="UTF-8")
                                        datedbprices_old = filepricesdb_old.read(8)
                                        filepricesdb_old.close()
                                        os.remove(os.path.join(defs.CACHEMCPR, "dateprices"))
                                        if os.path.isfile(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_old + ".sqlite")):
                                                os.remove(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_old + ".sqlite"))
                                if os.path.isfile(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_new + ".sqlite.tar.xz")):
                                        os.remove(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_new + ".sqlite.tar.xz"))
                                os.rename(os.path.join(defs.CACHEMCPR, "dateprices_newtmp"), os.path.join(defs.CACHEMCPR, "dateprices"))
                                os.rename(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_new + ".sqlite.tar.xz_newtmp"), os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_new + ".sqlite.tar.xz"))
                                
                        except:
                                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["error_download_db_prices"], 0)
        else:
                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["no_internet_download_db_prices"], 1)
        
        check_prices2(orig)

def check_update_prices(orig):
        """Checks if a new db is available for the prices.
        
        @orig is either "silent", "manual", "auto".
        
        """
        
        filedateprices = open(os.path.join(defs.CACHEMCPR, "dateprices"), "r", encoding="UTF-8")
        datedbprices = filedateprices.read(8)
        filedateprices.close()
        
        if orig == "auto":
                GLib.idle_add(defs.MAINWINDOW.widget_overlay.get_child().set_markup, "<b><big>" + defs.STRINGS["config_cardsprices_checking_update"] + "</big></b>")
        
        if functions.various.check_internet():
                try:
                        urllib.request.urlretrieve(defs.SITEMC + "files/dateprices", os.path.join(defs.CACHEMCPR, "dateprices_newtmp"))
                except:
                        pass
                else:
                        filedateprices_tmp = open(os.path.join(defs.CACHEMCPR, "dateprices_newtmp"), "r", encoding="UTF-8")
                        datedbprices_new = filedateprices_tmp.read(8)
                        filedateprices_tmp.close()
                        
                        if (datedbprices_new > datedbprices):
                                download_prices(orig)
                        else:
                                check_prices2(orig)
        else:
                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["no_internet_download_db_prices"], 1)
                check_prices2(orig)

def check_prices2(orig):
        if os.path.isfile(os.path.join(defs.CACHEMCPR, "dateprices_newtmp")):
                os.remove(os.path.join(defs.CACHEMCPR, "dateprices_newtmp"))
        
        if os.path.isfile(os.path.join(defs.CACHEMCPR, "dateprices")):
                filepricesdb = open(os.path.join(defs.CACHEMCPR, "dateprices"), "r", encoding="UTF-8")
                datedbprices = filepricesdb.read(8)
                filepricesdb.close()
                if os.path.isfile(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices + ".sqlite.tar.xz")):
                        try:
                                tar = tarfile.open(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices + ".sqlite.tar.xz"))
                        except:
                                pass
                        else:
                                tar.extractall(defs.CACHEMCPR)
                                tar.close()
                        os.remove(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices + ".sqlite.tar.xz"))
        
        if check_prices_presence():
                try:
                        GLib.idle_add(defs.MAINWINDOW.collection.button_estimate.set_sensitive, True)
                except:
                        pass
                try:
                        GLib.idle_add(defs.MAINWINDOW.decks.button_estimate_deck.set_sensitive, True)
                except:
                        pass

def get_price(ids_card_list):
        """Returns the average price of the cards in ids_card_list, if available. Else: min, else: high.
        
        """
        
        conn, c = connect_db()
        
        # rates
        c.execute("""SELECT * FROM rate_euro WHERE dollar IS NOT NULL""")
        dollars2euros = float(c.fetchone()[0])
        
        # currency
        price_cur = functions.config.read_config("price_cur")
        if price_cur == "0":
                currency = "$"
        elif price_cur == "1":
                currency = "€"
        
        tmp_req = ""
        for tmp in ids_card_list:
                tmp_req = tmp_req + "\"" + str(tmp) + "\", "
        tmp_req = tmp_req[:-2]
        request = """SELECT * FROM prices WHERE id_card IN (""" + tmp_req + """)"""
        
        c.execute(request)
        reponses_db = c.fetchall()
        disconnect_db(conn)
        
        dict_return = {}
        
        for id_ in ids_card_list:
                dict_return[id_] = ""
        
        for data_prices in reponses_db:
                id_card = data_prices[0]
                phigh = data_prices[1].replace(",", "")
                pmid = data_prices[2].replace(",", "")
                pmin = data_prices[3].replace(",", "")
        
                if pmid != "" and pmid != None:
                        price = float(pmid)
                elif pmin != "" and pmin != None:
                        price = float(pmid)
                elif phigh != "" and phigh != None:
                        price = float(phigh)
                else:
                        price = ""
                
                if price == "":
                        dict_return[id_card] = price
                else:
                        if price_cur == "0":
                                dict_return[id_card] = price
                        elif price_cur == "1":
                                # we need to change $ to €
                                price = round(price / dollars2euros, 2)
                                dict_return[id_card] = price
        return(dict_return, currency)

def estimate_ids_list(list_ids_db_to_estimate, dict_coll_to_estimate):
        """Estimates each card in list_ids_db_to_estimate, and returns the sum.
        
        """
        
        dict_prices, currency_to_disp = get_price(list_ids_db_to_estimate)
        est_sum = float(0)
        dict_price_not_found = {}
        
        for card_id, card_price in dict_prices.items():
                if card_price == "":
                        dict_price_not_found[card_id] = dict_coll_to_estimate[card_id]
                else:
                        est_sum = est_sum + (card_price * float(dict_coll_to_estimate[card_id]))
        
        return(round(est_sum, 2), currency_to_disp, dict_price_not_found)

def get_data_for_estimate(ids_db_list, deckname):
        # we get data in the collection for this list
        conn, c = functions.collection.connect_db()
        if deckname == None:
                c.execute("""SELECT id_coll, id_card FROM collection WHERE id_card IN (""" + ids_db_list + """)""")
        else:
                c.execute("""SELECT id_coll, id_card FROM collection WHERE id_card IN (""" + ids_db_list + """) AND (deck = \"""" + deckname + """\" OR deck_side = \"""" + deckname + """\")""")
        reponses_coll = c.fetchall()
        functions.collection.disconnect_db(conn)
        cards_to_estimate = {}
        list_ids_db_to_estimate = []
        for card in reponses_coll:
                try:
                        cards_to_estimate[card[1]]
                except KeyError:
                        cards_to_estimate[card[1]] = 1
                else:
                        cards_to_estimate[card[1]] += 1
                if card[1] not in list_ids_db_to_estimate:
                        list_ids_db_to_estimate.append(card[1])
        
        value, currency_to_disp, dict_price_not_found = functions.prices.estimate_ids_list(list_ids_db_to_estimate, cards_to_estimate)
        return(value, currency_to_disp, dict_price_not_found)

def show_estimate_dialog(orig, ids_db_list, deckname):
        """Shows the estimation result to the user.
        
        @orig can be "select", "collection", or "deck". If "orig" is not "deck", "deckname" must be None.
        
        """
        
        def _get_data(orig, ids_db_list, box_display, deckname):
                value, currency_to_disp, dict_price_not_found = get_data_for_estimate(ids_db_list, deckname)
                
                # we need to get data about cards in dict_price_not_found
                text_cards_price_not_found = ""
                if len(dict_price_not_found) > 0:
                        tmp_req = ""
                        for tmp in dict_price_not_found.keys():
                                tmp_req = tmp_req + "\"" + tmp + "\", "
                        tmp_req = tmp_req[:-2]
                        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                                foreign_name = defs.LOC_NAME_FOREIGN[functions.config.read_config("fr_language")]
                                request = """SELECT id, """ + foreign_name + """, edition FROM cards WHERE id IN (""" + tmp_req + """)"""
                        else:
                                request = """SELECT id, name, edition FROM cards WHERE id IN (""" + tmp_req + """)"""
                        
                        conn, c = functions.db.connect_db()
                        c.execute(request)
                        reponses_db = c.fetchall()
                        functions.db.disconnect_db(conn)
                        
                        tmp_list = []
                        for card in reponses_db:
                                tmp_list.append(card[1] + " - " + functions.various.edition_code_to_longname(card[2]) + " (x" + str(dict_price_not_found[card[0]]) + ")\n")
                        tmp_list = sorted(tmp_list)
                        for elm in tmp_list:
                                text_cards_price_not_found = text_cards_price_not_found + elm
                        text_cards_price_not_found = text_cards_price_not_found[:-1]
                
                GLib.idle_add(_update_dialog, orig, ids_db_list, box_display, value, currency_to_disp, dict_price_not_found, text_cards_price_not_found, deckname)
        def _update_dialog(orig, ids_db_list, box_display, value, currency_to_disp, dict_price_not_found, text_cards_price_not_found, deckname):
                for widget in box_display.get_children():
                        box_display.remove(widget)
                if orig == "select":
                        label_esti = Gtk.Label(defs.STRINGS["estimate_dialog_select"].replace("%%%", str(value) + currency_to_disp))
                elif orig == "collection":
                        label_esti = Gtk.Label(defs.STRINGS["estimate_dialog_collection"].replace("%%%", str(value) + currency_to_disp))
                elif orig == "deck":
                        label_esti = Gtk.Label(defs.STRINGS["estimate_dialog_deck"].replace(";;;", deckname).replace("%%%", str(value) + currency_to_disp))
                box_display.pack_start(label_esti, False, True, 0)
                
                if len(dict_price_not_found) > 0:
                        if len(dict_price_not_found) == 1:
                                expander = Gtk.Expander(label=defs.STRINGS["estimate_x_cards_without_price"])
                        else:
                                expander = Gtk.Expander(label=defs.STRINGS["estimate_x_cards_without_price_s"].replace("%%%", str(len(dict_price_not_found))))
                        expander.set_resize_toplevel(True)
                        prices_not_found_label = Gtk.Label(text_cards_price_not_found)
                        prices_not_found_label.set_selectable(True)
                        prices_not_found_label.set_alignment(0.0, 0.5)
                        scrolledwindow = Gtk.ScrolledWindow()
                        scrolledwindow.set_min_content_height(250)
                        scrolledwindow.set_min_content_width(140)
                        scrolledwindow.add_with_viewport(prices_not_found_label)
                        expander.add(scrolledwindow)
                        box_display.pack_start(expander, True, True, 0)
                
                box_display.show_all()
        
        est_dialog = Gtk.Dialog(title=defs.STRINGS["estimate_dialog_title"], buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK))
        est_dialog.set_default_size(350, 150)
        if defs.MAINWINDOW != None:
                est_dialog.set_transient_for(defs.MAINWINDOW)
                est_dialog.set_modal(True)
        
        box_display = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_display.set_margin_top(5)
        box_display.set_margin_bottom(5)
        box_display.set_margin_left(5)
        box_display.set_margin_right(5)
        
        spinner = Gtk.Spinner()
        box_display.pack_start(spinner, True, True, 0)
        spinner.start()
        
        content_area = est_dialog.get_content_area()
        content_area.props.border_width = 0
        content_area.pack_start(box_display, True, True, 0)
        
        box_display.show_all()
        
        thread = threading.Thread(target = _get_data, args = (orig, ids_db_list, box_display, deckname))
        thread.daemon = True
        thread.start()
        
        est_dialog.run()
        est_dialog.destroy()
