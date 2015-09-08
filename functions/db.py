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

# Some functions for dealing with the database

from gi.repository import Gtk, Gio, GdkPixbuf, GLib
import os
import urllib.request, urllib.parse, urllib.error
from socket import timeout
from distutils.version import StrictVersion
import sqlite3
import tarfile

# imports def.py
import defs
import functions.various

def connect_db():
        '''Return the connection to the DB and the cursor'''
        filename = os.path.join(defs.CACHEMC, "dbmc_" + defs.DB_VERSION + ".sqlite")
        if functions.various.isSQLite3(filename):
                conn = sqlite3.connect(filename)
                conn.create_function('py_lara', 1, functions.various.py_lara)
                conn.create_function('py_int', 1, functions.various.py_int)
                conn.create_function('py_lower', 1, functions.various.py_lower)
                c = conn.cursor()
                return(conn, c)
        else:
                os.remove(filename)
                GLib.idle_add(functions.various.message_exit, defs.STRINGS["db_damaged"])

def disconnect_db(conn):
        conn.commit()
        conn.close()

def prepare_request(search_widgets_list, g_op):
        '''Prepares the request to the database'''
        py_lara = functions.various.py_lara
        
        request = "SELECT * FROM cards WHERE"
        where_requests = []
        go = 0
        
        for elm in search_widgets_list:
                entry = elm[0]
                try:
                        comboboxtext = elm[1].get_active_text()
                except AttributeError:
                        comboboxtext = elm[1]
                
                # needed for SQLite
                text = entry.get_text().replace('"', '')
                if text != "" and text != "!" and text != ":" + defs.STRINGS["operator_or"] + ":" and text != ":" + defs.STRINGS["operator_and"] + ":":
                        go = 1
                        search_type = ""
                        for infosearch in defs.SEARCH_ITEMS.values():
                                if infosearch[1] == comboboxtext:
                                        search_type = infosearch[0]
                                        break
                        
                        base_text = str(text)
                        search_list = [base_text]
                        if ":" + defs.STRINGS["operator_and"] + ":" in base_text:
                                search_list = base_text.split(":" + defs.STRINGS["operator_and"] + ":")
                                operator = "AND"
                        elif ":" + defs.STRINGS["operator_or"] + ":" in base_text:
                                search_list = base_text.split(":" + defs.STRINGS["operator_or"] + ":")
                                operator = "OR"
                        
                        tmp_enum_req = ""
                        tmp_request = ""
                        for text in search_list:
                                negate = 0
                                if text[0] == "!":
                                        text = text[1:]
                                        negate = 1
                                if text == "ø":
                                        text = ""
                                
                                tmp_request = ""
                                
                                if search_type == "edition":
                                        nb_args = 0
                                        list_codes = []
                                        list_text_to_find = py_lara(text).strip().split(" ")
                                        for code, info_ed in defs.DICT_EDITIONS.items():
                                                name_ed_fr = info_ed[0]
                                                name_ed_en = info_ed[1]
                                                count_fr = 0
                                                count_en = 0
                                                for word in list_text_to_find:
                                                        if word in py_lara(name_ed_fr):
                                                                count_fr += 1
                                                        if word in py_lara(name_ed_en):
                                                                count_en += 1
                                                if count_fr == len(list_text_to_find) or count_en == len(list_text_to_find):
                                                        if code not in list_codes:
                                                                list_codes.append(code)
                                        
                                        if len(list_codes) > 0:
                                                for ed_code in list_codes:
                                                        if nb_args == 0:
                                                                if negate == 0:
                                                                        tmp_request = """(edition = '""" + ed_code + """')"""
                                                                else:
                                                                        tmp_request = """(edition != '""" + ed_code + """')"""
                                                        else:
                                                                if negate == 0:
                                                                        tmp_request = tmp_request + """ OR (edition = '""" + ed_code + """')"""
                                                                else:
                                                                        tmp_request = tmp_request + """ AND (edition != '""" + ed_code + """')"""
                                                        nb_args += 1
                                                
                                                if tmp_enum_req == "":
                                                        tmp_enum_req = "(" + tmp_request + ")"
                                                else:
                                                        tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                        else:
                                                tmp_request = """edition = '""" + text + """'"""
                                                if tmp_enum_req == "":
                                                        tmp_enum_req = "(" + tmp_request + ")"
                                                else:
                                                        tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                
                                elif search_type == "rarity":
                                        text_to_find = py_lara(text.strip())
                                        if text_to_find == defs.STRINGS["h_mythic"]:
                                                text_to_find = "mythic rare"
                                        elif text_to_find == defs.STRINGS["h_rare"]:
                                                text_to_find = "rare"
                                        elif text_to_find == defs.STRINGS["h_uncommon"]:
                                                text_to_find = "uncommon"
                                        elif text_to_find == defs.STRINGS["h_common"]:
                                                text_to_find = "common"
                                        elif text_to_find == defs.STRINGS["h_basic_land"]:
                                                text_to_find = "basic land"
                                        elif text_to_find == defs.STRINGS["h_special"]:
                                                text_to_find = "special"
                                        
                                        if negate == 0:
                                                tmp_request = """py_lower(rarity) = \"""" + text_to_find + """\""""
                                        else:
                                                tmp_request = """py_lower(rarity) != \"""" + text_to_find + """\""""
                                        if tmp_enum_req == "":
                                                tmp_enum_req = "(" + tmp_request + ")"
                                        else:
                                                tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                
                                elif search_type == "flavor":
                                        text_to_find = text.strip().lower()
                                        if text_to_find == "":
                                                if negate == 0:
                                                        tmp_request = """flavor = \"\""""
                                                else:
                                                        tmp_request = """flavor != \"\""""
                                        else:
                                                if negate == 0:
                                                        tmp_request = """py_lower(flavor) LIKE \"%""" + text_to_find + """%\""""
                                                else:
                                                        tmp_request = """py_lower(flavor) NOT LIKE \"%""" + text_to_find + """%\""""
                                        if tmp_enum_req == "":
                                                tmp_enum_req = "(" + tmp_request + ")"
                                        else:
                                                tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                
                                elif search_type == "artist":
                                        text_to_find = text.strip().lower()
                                        if negate == 0:
                                                tmp_request = """py_lower(artist) LIKE \"%""" + text_to_find + """%\""""
                                        else:
                                                tmp_request = """py_lower(artist) NOT LIKE \"%""" + text_to_find + """%\""""
                                        if tmp_enum_req == "":
                                                tmp_enum_req = "(" + tmp_request + ")"
                                        else:
                                                tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                
                                elif search_type == "text":
                                        text_to_find = text.strip().lower()
                                        if text_to_find == "":
                                                if negate == 0:
                                                        tmp_request = """text = \"\""""
                                                else:
                                                        tmp_request = """text != \"\""""
                                        else:
                                                if negate == 0:
                                                        tmp_request = """py_lower(text) LIKE \"%""" + text_to_find + """%\""""
                                                else:
                                                        tmp_request = """py_lower(text) NOT LIKE \"%""" + text_to_find + """%\""""
                                        if tmp_enum_req == "":
                                                tmp_enum_req = "(" + tmp_request + ")"
                                        else:
                                                tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                
                                elif search_type == "loyalty":
                                        text_to_find = py_lara(text).strip()
                                        if text_to_find.isnumeric():
                                                tooltip_text = entry.get_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY)
                                                if tooltip_text == defs.STRINGS["entry_eq_ad"]:
                                                        math_operator = "="
                                                elif tooltip_text == defs.STRINGS["entry_inf_eq_ad"]:
                                                        math_operator = "<="
                                                elif tooltip_text == defs.STRINGS["entry_sup_eq_ad"]:
                                                        math_operator = ">="
                                                elif tooltip_text == defs.STRINGS["entry_diff"]:
                                                        math_operator = "!="
                                                tmp_request = """py_int(loyalty) """ + math_operator + """ """ + text_to_find
                                                if tmp_enum_req == "":
                                                        tmp_enum_req = "(" + tmp_request + ")"
                                                else:
                                                        tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                        else:
                                                functions.various.message_dialog(defs.STRINGS["loyalty_only_number"], 0)
                                                go = 0
                                
                                elif search_type == "toughness":
                                        text_to_find = py_lara(text).strip()
                                        if text_to_find.isnumeric():
                                                tooltip_text = entry.get_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY)
                                                if tooltip_text == defs.STRINGS["entry_eq_ad"]:
                                                        math_operator = "="
                                                elif tooltip_text == defs.STRINGS["entry_inf_eq_ad"]:
                                                        math_operator = "<="
                                                elif tooltip_text == defs.STRINGS["entry_sup_eq_ad"]:
                                                        math_operator = ">="
                                                elif tooltip_text == defs.STRINGS["entry_diff"]:
                                                        math_operator = "!="
                                                tmp_request = """py_int(toughness) """ + math_operator + """ """ + text_to_find
                                                if tmp_enum_req == "":
                                                        tmp_enum_req = "(" + tmp_request + ")"
                                                else:
                                                        tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                        else:
                                                functions.various.message_dialog(defs.STRINGS["toughness_only_number"], 0)
                                                go = 0
                                
                                elif search_type == "power":
                                        text_to_find = py_lara(text).strip()
                                        if text_to_find.isnumeric():
                                                tooltip_text = entry.get_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY)
                                                if tooltip_text == defs.STRINGS["entry_eq_ad"]:
                                                        math_operator = "="
                                                elif tooltip_text == defs.STRINGS["entry_inf_eq_ad"]:
                                                        math_operator = "<="
                                                elif tooltip_text == defs.STRINGS["entry_sup_eq_ad"]:
                                                        math_operator = ">="
                                                elif tooltip_text == defs.STRINGS["entry_diff"]:
                                                        math_operator = "!="
                                                tmp_request = """py_int(power) """ + math_operator + """ """ + text_to_find
                                                if tmp_enum_req == "":
                                                        tmp_enum_req = "(" + tmp_request + ")"
                                                else:
                                                        tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                        else:
                                                functions.various.message_dialog(defs.STRINGS["power_only_number"], 0)
                                                go = 0
                                
                                elif search_type == "cmc":
                                        text_to_find = py_lara(text).strip()
                                        if text_to_find.isnumeric():
                                                tooltip_text = entry.get_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY)
                                                if tooltip_text == defs.STRINGS["entry_eq_ad"]:
                                                        math_operator = "="
                                                elif tooltip_text == defs.STRINGS["entry_inf_eq_ad"]:
                                                        math_operator = "<="
                                                elif tooltip_text == defs.STRINGS["entry_sup_eq_ad"]:
                                                        math_operator = ">="
                                                elif tooltip_text == defs.STRINGS["entry_diff"]:
                                                        math_operator = "!="
                                                tmp_request = """py_int(cmc) """ + math_operator + """ """ + text_to_find
                                                if tmp_enum_req == "":
                                                        tmp_enum_req = "(" + tmp_request + ")"
                                                else:
                                                        tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                        else:
                                                functions.various.message_dialog(defs.STRINGS["cmc_only_number"], 0)
                                                go = 0
                                
                                elif search_type == "manacost":
                                        text_to_find = py_lara(text).strip().replace("{", "").replace("}", "").upper()
                                        finalcost = ""
                                        if text_to_find.isnumeric():
                                                finalcost = "{" + text_to_find + "}"
                                        else:
                                                dict_manacost = {}
                                                dict_key_del = []
                                                for i, char in enumerate(text_to_find):
                                                        dict_manacost[i] = char
                                                dict_tmp = dict(dict_manacost)
                                                
                                                for key, cost in dict_tmp.items():
                                                        if cost == "/":
                                                                dict_manacost[key] = "{" + dict_manacost[key - 1].replace("{", "").replace("}", "") + "/" + dict_manacost[key + 1].replace("{", "").replace("}", "") + "}"
                                                                dict_key_del.append(key - 1)
                                                                dict_key_del.append(key + 1)
                                                        elif cost == "0" and len(text_to_find) > 1:
                                                                dict_manacost[key] = "{" + dict_manacost[key - 1].replace("{", "").replace("}", "") + "0" + "}"
                                                                dict_key_del.append(key - 1)
                                                                dict_tmp[key] = "{" + dict_manacost[key - 1].replace("{", "").replace("}", "") + "0" + "}"
                                                        else:
                                                                dict_manacost[key] = "{" + cost + "}"
                                                
                                                for key in dict_key_del:
                                                        del(dict_manacost[key])
                                                
                                                for cost in dict_manacost.values():
                                                        finalcost = finalcost + cost
                                        if negate == 0:
                                                tmp_request = """manacost = \"""" + finalcost + """\""""
                                        else:
                                                tmp_request = """manacost != \"""" + finalcost + """\""""
                                        if tmp_enum_req == "":
                                                tmp_enum_req = "(" + tmp_request + ")"
                                        else:
                                                tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                
                                elif search_type == "colors":
                                        text_to_find = py_lara(text).strip()
                                        if text_to_find == defs.STRINGS["red"] or text_to_find == "red":
                                                text_to_find = "r"
                                        if text_to_find == defs.STRINGS["green"] or text_to_find == "green":
                                                text_to_find = "g"
                                        if text_to_find == defs.STRINGS["black"] or text_to_find == "black":
                                                text_to_find = "b"
                                        if text_to_find == defs.STRINGS["blue"] or text_to_find == "blue":
                                                text_to_find = "u"
                                        if text_to_find == defs.STRINGS["white"] or text_to_find == "white":
                                                text_to_find = "w"
                                        if text_to_find == defs.STRINGS["colorless"] or text_to_find == "colorless":
                                                text_to_find = ""
                                        if text_to_find == "":
                                                if negate == 0:
                                                        tmp_request = "colors = ''"
                                                else:
                                                        tmp_request = "colors != ''"
                                        else:
                                                nb_args = 0
                                                for color in text_to_find.upper():
                                                        if nb_args == 0:
                                                                if negate == 0:
                                                                        tmp_request = """(colors LIKE \"%""" + color + """%\")"""
                                                                else:
                                                                        tmp_request = """(colors NOT LIKE \"%""" + color + """%\")"""
                                                        else:
                                                                if negate == 0:
                                                                        tmp_request = tmp_request + """ AND (colors LIKE \"%""" + color + """%\")"""
                                                                else:
                                                                        tmp_request = tmp_request + """ AND (colors NOT LIKE \"%""" + color + """%\")"""
                                                        nb_args += 1
                                        if tmp_enum_req == "":
                                                tmp_enum_req = "(" + tmp_request + ")"
                                        else:
                                                tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                
                                elif search_type == "type":
                                        text_to_find = py_lara(text).replace("-", "—")
                                        if defs.LANGUAGE != "en":
                                                # non-english helpers
                                                if text_to_find == defs.STRINGS["artifact"] or text_to_find == defs.STRINGS["artifacts"]:
                                                        text_to_find = "artifact"
                                                elif text_to_find == defs.STRINGS["enchantment"] or text_to_find == defs.STRINGS["enchantments"]:
                                                        text_to_find = "enchantment"
                                                elif text_to_find == defs.STRINGS["instant"] or text_to_find == defs.STRINGS["instants"]:
                                                        text_to_find = "instant"
                                                elif text_to_find == defs.STRINGS["land"] or text_to_find == defs.STRINGS["lands"]:
                                                        text_to_find = "land"
                                                elif text_to_find == defs.STRINGS["planeswalker"] or text_to_find == defs.STRINGS["planeswalkers"]:
                                                        text_to_find = "planeswalker"
                                                elif text_to_find == defs.STRINGS["creature"] or text_to_find == defs.STRINGS["creatures"]:
                                                        text_to_find = "creature"
                                                elif text_to_find == defs.STRINGS["sorcery"] or text_to_find == defs.STRINGS["sorceries"]:
                                                        text_to_find = "sorcery"
                                                elif text_to_find == defs.STRINGS["token"] or text_to_find == defs.STRINGS["tokens"]:
                                                        text_to_find = "token"
                                                elif text_to_find == defs.STRINGS["emblem"] or text_to_find == defs.STRINGS["emblems"]:
                                                        text_to_find = "emblem"
                                                elif text_to_find == defs.STRINGS["counter"] or text_to_find == defs.STRINGS["counters"]:
                                                        text_to_find = "counter"
                                        if negate == 0:
                                                tmp_request = """type LIKE \"%""" + text_to_find + """%\""""
                                        else:
                                                tmp_request = """type NOT LIKE \"%""" + text_to_find + """%\""""
                                        if tmp_enum_req == "":
                                                tmp_enum_req = "(" + tmp_request + ")"
                                        else:
                                                tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                                
                                elif search_type == "name":
                                        if text == "//":
                                                if negate == 0:
                                                        tmp_request = "layout = 'split'"
                                                else:
                                                        tmp_request = "layout != 'split'"
                                                tmp_enum_req = "(" + tmp_request + ")"
                                        elif text == "<>":
                                                if negate == 0:
                                                        tmp_request = "layout = 'flip'"
                                                else:
                                                        tmp_request = "layout != 'flip'"
                                                tmp_enum_req = "(" + tmp_request + ")"
                                        elif text == "||":
                                                if negate == 0:
                                                        tmp_request = "layout = 'double-faced'"
                                                else:
                                                        tmp_request = "layout != 'double-faced'"
                                                tmp_enum_req = "(" + tmp_request + ")"
                                        else:
                                                nb_args = 0
                                                list_text_to_find = py_lara(text).strip().split(" ")
                                                tmp_request_lang = []
                                                request_name = ""
                                                
                                                # très précis mais LENT
                                                '''#for lang in ["name", "name_chinesetrad", "name_chinesesimp", "name_french", "name_german", "name_italian", "name_japanese", "name_korean", "name_portuguesebrazil", "name_portuguese", "name_russian", "name_spanish"]:
                                                for lang in ["name", "name_french"]:
                                                        nb_args_lang = 0
                                                        for word in list_text_to_find:
                                                                if nb_args_lang == 0:
                                                                        tmp = "py_lara(" + lang + ") LIKE '%" + word + "%'"
                                                                else:
                                                                        tmp = tmp + " AND py_lara(" + lang + ") LIKE '%" + word + "%'"
                                                                nb_args_lang += 1
                                                        tmp = "(" + tmp + ")"
                                                        tmp_request_lang.append(tmp)
                                                        
                                                for elm in tmp_request_lang:
                                                        if nb_args == 0:
                                                                request_name = "(" + elm + ")"
                                                        else:
                                                                request_name = request_name + " OR (" + elm + ")"
                                                        nb_args += 1
                                                if tmp_enum_req == "":
                                                        tmp_enum_req = "(" + tmp_request + ")"
                                                else:
                                                        tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"'''
                                                
                                                # plus rapide mais pas hyper précis, faux positifs
                                                for word in list_text_to_find:
                                                        if nb_args == 0:
                                                                if negate == 0:
                                                                        tmp_request = """(py_lara(name || name_chinesetrad || name_chinesesimp || name_french || name_german || name_italian || name_japanese || name_korean || name_portuguesebrazil || name_portuguese || name_russian || name_spanish) LIKE \"%""" + word + """%\")"""
                                                                else:
                                                                        tmp_request = """(py_lara(name || name_chinesetrad || name_chinesesimp || name_french || name_german || name_italian || name_japanese || name_korean || name_portuguesebrazil || name_portuguese || name_russian || name_spanish) NOT LIKE \"%""" + word + """%\")"""
                                                        else:
                                                                if negate == 0:
                                                                        tmp_request = tmp_request + """ AND (py_lara(name || name_chinesetrad || name_chinesesimp || name_french || name_german || name_italian || name_japanese || name_korean || name_portuguesebrazil || name_portuguese || name_russian || name_spanish) LIKE \"%""" + word + """%\")"""
                                                                else:
                                                                        tmp_request = tmp_request + """ AND (py_lara(name || name_chinesetrad || name_chinesesimp || name_french || name_german || name_italian || name_japanese || name_korean || name_portuguesebrazil || name_portuguese || name_russian || name_spanish) NOT LIKE \"%""" + word + """%\")"""
                                                        nb_args += 1
                                                if tmp_enum_req == "":
                                                        tmp_enum_req = "(" + tmp_request + ")"
                                                else:
                                                        tmp_enum_req = tmp_enum_req + " " + operator + " (" + tmp_request + ")"
                        where_requests.append(tmp_enum_req)
        
        if go == 1 and len(where_requests) > 0:              
                i = 0
                for tmp_request in where_requests:
                        if i == 0:
                                request = request + " (" + tmp_request + ")"
                        else:
                                request = request + " AND (" + tmp_request + ")"
                        i += 1
                
                #print(request)
                return(request)
        else:
                return(None)

def check_db():
        '''Function which checks if the db is here, up to date, and updates it if not'''
        if os.path.isfile(os.path.join(defs.CACHEMC, "datedb")) == False:
                download_db()
        else:
                fichierdatedb = open(os.path.join(defs.CACHEMC, "datedb"), "r", encoding="UTF-8")
                datebddcartes = fichierdatedb.read(8)
                fichierdatedb.close()
                if os.path.isfile(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes + ".sqlite")) == False:
                        download_db()
                else:
                        check_update_db()

def check_db2():
        if os.path.isfile(os.path.join(defs.CACHEMC, "datedb_newtmp")):
                os.remove(os.path.join(defs.CACHEMC, "datedb_newtmp"))
        
        if os.path.isfile(os.path.join(defs.CACHEMC, "datedb")):
                fichierdatedb = open(os.path.join(defs.CACHEMC, "datedb"), "r", encoding="UTF-8")
                datebddcartes = fichierdatedb.read(8)
                fichierdatedb.close()
                if os.path.isfile(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes + ".sqlite.tar.xz")):
                        tar = tarfile.open(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes + ".sqlite.tar.xz"))
                        tar.extractall(defs.CACHEMC)
                        tar.close()
                        os.remove(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes + ".sqlite.tar.xz"))
                if os.path.isfile(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes + ".sqlite")):
                        defs.DB_VERSION = datebddcartes
                else:
                        defs.DB_VERSION = None
        else:
                defs.DB_VERSION = None
        
        # when downloading the new database is over, we download symbols editions
        functions.various.download_symbols()
        GLib.idle_add(defs.MAINWINDOW.app.load_mc)

def download_db():
        '''Function which downloads the database.'''
        defs.DB_DOWNLOAD_PROGRESS = 0
        go = 1
        if functions.various.check_internet():
                GLib.idle_add(defs.MAINWINDOW.widget_overlay.get_child().set_markup, "<b><big>" + defs.STRINGS["downloading_db"] + "</big></b>")
                #GLib.idle_add(functions.various.update_gui, 0)
                
                if os.path.isfile(os.path.join(defs.CACHEMC, "datedb_newtmp")) == False:
                        try:
                                urllib.request.urlretrieve(defs.SITEMC + "files/datedb", os.path.join(defs.CACHEMC, "datedb_newtmp"))
                        except (urllib.error.HTTPError, urllib.request.URLError, timeout, UnicodeEncodeError):
                                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["error_download_db"], 0)
                                go = 0
                if go == 1:
                        fichierdatedb_tmp = open(os.path.join(defs.CACHEMC, "datedb_newtmp"), "r", encoding="UTF-8")
                        datebddcartes_new = fichierdatedb_tmp.read(8)
                        fichierdatedb_tmp.close()
                        if os.path.isfile(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes_new + ".sqlite.tar.xz_newtmp")):
                                os.remove(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes_new + ".sqlite.tar.xz_newtmp"))
                        
                        try:
                                urllib.request.urlretrieve(defs.SITEMC + "files/dbmc_" + datebddcartes_new + ".sqlite.tar.xz", os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes_new + ".sqlite.tar.xz_newtmp"), functions.various.reporthook)
                                #urllib.request.urlretrieve(defs.SITEMC + "files/dbmc_" + datebddcartes_new + ".sqlite.tar.xz", os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes_new + ".sqlite.tar.xz_newtmp"))
                                if os.path.isfile(os.path.join(defs.CACHEMC, "datedb")):
                                        fichierdatedb_old = open(os.path.join(defs.CACHEMC, "datedb"), "r", encoding="UTF-8")
                                        datebddcartes_old = fichierdatedb_old.read(8)
                                        fichierdatedb_old.close()
                                        os.remove(os.path.join(defs.CACHEMC, "datedb"))
                                        if os.path.isfile(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes_old + ".sqlite")):
                                                os.remove(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes_old + ".sqlite"))
                                if os.path.isfile(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes_new + ".sqlite.tar.xz")):
                                        os.remove(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes_new + ".sqlite.tar.xz"))
                                os.rename(os.path.join(defs.CACHEMC, "datedb_newtmp"), os.path.join(defs.CACHEMC, "datedb"))
                                os.rename(os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes_new + ".sqlite.tar.xz_newtmp"), os.path.join(defs.CACHEMC, "dbmc_" + datebddcartes_new + ".sqlite.tar.xz"))
                                
                        except (urllib.error.HTTPError, urllib.request.URLError, timeout, UnicodeEncodeError):
                                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["error_download_db"], 0)
                                #functions.various.message_dialog(defs.STRINGS["error_download_db"], 0)
        else:
                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["no_internet_download_db"], 1)
                #functions.various.message_dialog(defs.STRINGS["no_internet_download_db"], 1)
        
        check_db2()

def check_update_db():
        '''Checks if a new db is available'''
        fichierdatedb = open(os.path.join(defs.CACHEMC, "datedb"), "r", encoding="UTF-8")
        datebddcartes = fichierdatedb.read(8)
        fichierdatedb.close()
        
        if functions.various.check_internet():
                try:
                        urllib.request.urlretrieve(defs.SITEMC + "files/datedb", os.path.join(defs.CACHEMC, "datedb_newtmp"))
                except (urllib.error.HTTPError, urllib.request.URLError, timeout, UnicodeEncodeError):
                        pass
                else:
                        fichierdatedb_tmp = open(os.path.join(defs.CACHEMC, "datedb_newtmp"), "r", encoding="UTF-8")
                        datebddcartes_new = fichierdatedb_tmp.read(8)
                        changelog_new = fichierdatedb_tmp.readlines()
                        minversionbdd_new = changelog_new[0].split("|")[1].rstrip("\n\r")
                        fichierdatedb_tmp.close()
                        
                        del changelog_new[0]
                        changelog_new = "".join(changelog_new)
                        infoversion = ""
                        mcversion = defs.VERSION
                        if StrictVersion(mcversion) < StrictVersion(minversionbdd_new):
                                infoversion = "\n" + defs.STRINGS["warning_ver_db"].replace("%%%", minversionbdd_new) + "\n"
                        
                        if (datebddcartes_new > datebddcartes):
                                if changelog_new == "":
                                        infochangelog = ""
                                else:
                                        infochangelog = "\n\n" + defs.STRINGS["changelog_db"] + "\n" + changelog_new
                                dialogconfirm = Gtk.MessageDialog(defs.MAINWINDOW, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, defs.STRINGS["new_update_db"].replace("%%%", infoversion) + infochangelog)
                                GLib.idle_add(dialog_confimr_db, dialogconfirm)
                        else:
                                check_db2()
        else:
                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["no_internet_update_db"], 1)
                #functions.various.message_dialog(defs.STRINGS["no_internet_update_db"], 1)
                check_db2()

def dialog_confimr_db(dialogconfirm):
        responseconfirm = dialogconfirm.run()
        dialogconfirm.destroy()
        # -8 yes, -9 no
        if responseconfirm == -8:
                GLib.idle_add(defs.MAINWINDOW.widget_overlay.get_child().set_markup, "<b><big>" + defs.STRINGS["downloading_db"] + "</big></b>")
                GLib.idle_add(download_db)
        else:
                check_db2()
