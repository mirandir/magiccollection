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

# Some functions for dealing with the prices of the cards

import os
import urllib.request, urllib.parse, urllib.error
from socket import timeout
import tarfile
from distutils.version import StrictVersion
import sqlite3

import defs
import functions.various

def check_prices_presence():
        '''Checks if the prices have been downloaded.'''
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
        '''Return the connection to the DB and the cursor'''
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
        '''Function which checks if the prices are here, up to date, and launches download if not.
        @orig is either "silent", "manual", "auto".'''
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
        '''Downloads the prices of the cards.
        @orig is either "silent", "manual", "auto".'''
        defs.DB_DOWNLOAD_PROGRESS = 0
        go = 1
        if functions.various.check_internet():
                #GLib.idle_add(defs.MAINWINDOW.widget_overlay.get_child().set_markup, "<b><big>" + defs.STRINGS["downloading_db"] + "</big></b>")
                
                if os.path.isfile(os.path.join(defs.CACHEMCPR, "dateprices_newtmp")) == False:
                        try:
                                urllib.request.urlretrieve(defs.SITEMC + "files/dateprices", os.path.join(defs.CACHEMCPR, "dateprices_newtmp"))
                        except (urllib.error.HTTPError, urllib.request.URLError, timeout, UnicodeEncodeError):
                                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["error_download_db_prices"], 0)
                                go = 0
                if go == 1:
                        filepricesdb_tmp = open(os.path.join(defs.CACHEMCPR, "dateprices_newtmp"), "r", encoding="UTF-8")
                        datedbprices_new = filepricesdb_tmp.read(8)
                        filepricesdb_tmp.close()
                        if os.path.isfile(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_new + ".sqlite.tar.xz_newtmp")):
                                os.remove(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices_new + ".sqlite.tar.xz_newtmp"))
                        
                        try:
                                if orig == "manual":
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
                                
                        except (urllib.error.HTTPError, urllib.request.URLError, timeout, UnicodeEncodeError):
                                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["error_download_db_prices"], 0)
        else:
                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["no_internet_download_db_prices"], 1)
        
        check_prices2(orig)

def check_update_prices(orig):
        '''Checks if a new db is available for the prices.'''
        filedateprices = open(os.path.join(defs.CACHEMCPR, "dateprices"), "r", encoding="UTF-8")
        datedbprices = filedateprices.read(8)
        filedateprices.close()
        
        #GLib.idle_add(defs.MAINWINDOW.widget_overlay.get_child().set_markup, "<b><big>" + defs.STRINGS["checking_db_update"] + "</big></b>")
        
        if functions.various.check_internet():
                try:
                        urllib.request.urlretrieve(defs.SITEMC + "files/dateprices", os.path.join(defs.CACHEMCPR, "dateprices_newtmp"))
                except (urllib.error.HTTPError, urllib.request.URLError, timeout, UnicodeEncodeError):
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
                        tar = tarfile.open(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices + ".sqlite.tar.xz"))
                        tar.extractall(defs.CACHEMCPR)
                        tar.close()
                        os.remove(os.path.join(defs.CACHEMCPR, "prices_" + datedbprices + ".sqlite.tar.xz"))

def get_price(ids_card_list):
        '''Returns the average price of the card, if available. Else: min, high.'''
        conn, c = connect_db()
        
        # rates
        c.execute("""SELECT * FROM rate_euro WHERE dollar IS NOT NULL""")
        dollar2euros = float(c.fetchone()[0])
        
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
        
        dict_return = {}
        
        for data_prices in reponses_db:
                id_card = data_prices[0]
                phigh = data_prices[1]
                pmid = data_prices[2]
                pmin = data_prices[3]
        
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
                                price = round(price / dollar2euros, 2)
                                dict_return[id_card] = price
        return(dict_return, currency)
