#!/usr/bin/env python3
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

# Functions related to import/export the collection and the decks

from gi.repository import Gtk, GLib, Pango
import os
from datetime import date
import shutil
import sys

# imports def.py
import defs

# imports functions
import functions.various
import functions.collection
import functions.decks
import functions.db

def export_collection_text():
        """This function exports the collection as a human readable plain text file.
        
        """
        
        if defs.COLL_LOCK:
                functions.various.message_dialog(defs.STRINGS["export_collection_busy"], 0) #Add a new STRINGS message to explicitly mention text export?
        else:
                functions.various.lock_db(True, None)
                # we get the current date
                today = date.today()
                month = '%02d' % today.month
                day = '%02d' % today.day
                rtoday = str(today.year) + str(month) + str(day)
                #Add a new STRINGS message to explicitly mention text export?
                dialog = Gtk.FileChooserDialog(defs.STRINGS["export"], defs.MAINWINDOW, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
                dialog.set_do_overwrite_confirmation(True)
                filefilter = Gtk.FileFilter()
                filefilter.set_name(defs.STRINGS["text_filetype"])
                filefilter.add_pattern("*.txt")
                dialog.add_filter(filefilter)
                
                if defs.OS == "windows":
                        user = functions.various.valid_filename_os(os.environ["USERNAME"])
                else:
                        user = functions.various.valid_filename_os(os.environ["USER"])
                
                dialog.set_current_name(defs.STRINGS["export_filename"].replace("%user%", user).replace("%date%", rtoday) + ".txt")
                
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                        filename = dialog.get_filename()
                        # we test if we can write here
                        try:
                                out_txt = open(filename, 'w')
                        except:
                                functions.various.message_dialog(defs.STRINGS["export_write_impossible"], 0)
                        else:
                                #os.remove(filename)
                                #shutil.copy(os.path.join(defs.HOMEMC, "collection.sqlite"), filename)
                                out_txt.write(collection_text_string())
                                out_txt.close()

                dialog.destroy()
                functions.various.lock_db(False, None)

#TODO: Should be moved to functions.collection
def collection_text_string():
        """This function builds a string from current cards collection. For now the format is hard coded:
        {name} - {extension} ({lang}) - {condition}
        
        """
        res = ""
        conn, cur = functions.collection.connect_db()

        cur.execute("""ATTACH DATABASE ? AS dbmc""", (os.path.join(defs.CACHEMC, "dbmc_" + defs.DB_VERSION + ".sqlite"),))
        cur.execute("""SELECT name, edition, lang, condition FROM collection AS col JOIN dbmc.cards AS car ON col.id_card=car.id""")
        rows = cur.fetchall()

        for row in rows:
                res += "%s - %s (%s) - %s\n" % (row[0], row[1], row[2], row[3])

        conn.close()

        return res

def import_data():
        """This function imports the collection and the decks from a SQLite file.
        
        """
        
        if defs.COLL_LOCK:
                functions.various.message_dialog(defs.STRINGS["import_collection_busy"], 0)
        else:
                # dear user, are you sure ?
                dialogconfirm = Gtk.MessageDialog(defs.MAINWINDOW, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, defs.STRINGS["import_areyousure"])
                responseconfirm = dialogconfirm.run()
                dialogconfirm.destroy()
                if responseconfirm == -8:
                        lastsave = functions.collection.backup_coll("forced")
                        dialog = Gtk.FileChooserDialog(defs.STRINGS["import"], defs.MAINWINDOW, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
                        filefilter = Gtk.FileFilter()
                        filefilter.set_name(defs.STRINGS["exportimport_filetype"])
                        filefilter.add_pattern("*.mcollection")
                        dialog.add_filter(filefilter)
                        go = 0
                        response = dialog.run()
                        if response == Gtk.ResponseType.OK:
                                filename = dialog.get_filename()
                                try:
                                        shutil.copy(filename, os.path.join(defs.HOMEMC, "collection.sqlite"))
                                except:
                                        functions.various.message_dialog(defs.STRINGS["import_error"], 0)
                                        functions.collection.restore_backup(lastsave)
                                else:
                                        go = 1
                        dialog.destroy()
                        if go == 1:
                                functions.various.clear_gui_del()
                                functions.collection.read_coll(defs.MAINWINDOW.collection.right_content, defs.MAINWINDOW.collection)
                                functions.decks.gen_decks_display(defs.MAINWINDOW.decks, defs.MAINWINDOW.decks.right_content)
                                if defs.MAINWINDOW.advancedsearch.mainstore != None:
                                        defs.MAINWINDOW.advancedsearch.mainstore.clear()
                                functions.various.message_dialog(defs.STRINGS["import_success"], 0)

def export_data():
        """This function exports the collection and the decks to a SQLite file.
        
        """
        
        if defs.COLL_LOCK:
                functions.various.message_dialog(defs.STRINGS["export_collection_busy"], 0)
        else:
                functions.various.lock_db(True, None)
                # we get the current date
                today = date.today()
                month = '%02d' % today.month
                day = '%02d' % today.day
                rtoday = str(today.year) + str(month) + str(day)
                dialog = Gtk.FileChooserDialog(defs.STRINGS["export"], defs.MAINWINDOW, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
                dialog.set_do_overwrite_confirmation(True)
                filefilter = Gtk.FileFilter()
                filefilter.set_name(defs.STRINGS["exportimport_filetype"])
                filefilter.add_pattern("*.mcollection")
                dialog.add_filter(filefilter)
                
                if defs.OS == "windows":
                        user = functions.various.valid_filename_os(os.environ["USERNAME"])
                else:
                        user = functions.various.valid_filename_os(os.environ["USER"])
                
                dialog.set_current_name(defs.STRINGS["export_filename"].replace("%user%", user).replace("%date%", rtoday) + ".mcollection")
                
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                        filename = dialog.get_filename()
                        # we test if we can write here
                        try:
                                open(filename, 'w')
                        except:
                                functions.various.message_dialog(defs.STRINGS["export_write_impossible"], 0)
                        else:
                                os.remove(filename)
                                shutil.copy(os.path.join(defs.HOMEMC, "collection.sqlite"), filename)
                dialog.destroy()
                functions.various.lock_db(False, None)

def test_oldformat():
        """Checks if we are in an old profil of MC.
        
        """
        
        if os.path.isfile(os.path.join(defs.HOMEMC, "collection.txt")) or os.path.isdir(os.path.join(defs.HOMEMC, "decks")):
                return(True)
        else:
                return(False)

def import_oldformat():
        """This function converts the old format of the collection & decks to the new one. Should take some time.
        
        """
        
        defs.CONVERTING = True
        
        if os.path.isfile(os.path.join(defs.HOMEMC, "collection.sqlite")):
                # bad bad bad, we cannot convert the old format if a collection with the new format is present (too risky)
                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["import_oldformat_error_sqlite_is_here"], 0)
        else:
                # we delete the old prices data
                if os.path.isdir(os.path.join(defs.CACHEMCPR)):
                        shutil.rmtree(os.path.join(defs.CACHEMCPR))
                        os.mkdir(os.path.join(defs.CACHEMCPR))
                
                # we delete old HD pictures in CACHEMCPIC
                for folder in os.listdir(os.path.join(defs.CACHEMCPIC)):
                        if os.path.isdir(os.path.join(defs.CACHEMCPIC, folder)):
                                for pic in os.listdir(os.path.join(defs.CACHEMCPIC, folder)):
                                        if ".full.hd" in pic:
                                                try:
                                                        os.remove(os.path.join(defs.CACHEMCPIC, folder, pic))
                                                except:
                                                        pass
                
                # we create the database
                functions.collection.create_db_coll()
                
                # we start by moving old data to another, clean folder, 'oldmc'
                if os.path.isdir(os.path.join(defs.HOMEMC, "oldmc")):
                        shutil.rmtree(os.path.join(defs.HOMEMC, "oldmc"))
                os.mkdir(os.path.join(defs.HOMEMC, "oldmc"))
                
                # work with the decks
                Decks = {}
                if os.path.isdir(os.path.join(defs.HOMEMC, "decks")):
                        shutil.move(os.path.join(defs.HOMEMC, "decks"), os.path.join(defs.HOMEMC, "oldmc"))
                        
                        decks_list = os.listdir(os.path.join(defs.HOMEMC, "oldmc", "decks"))
                        for deck in decks_list:
                                if deck[-5:] == ".deck":
                                        Decks[deck[:-5]] = read_olddeck(os.path.join(defs.HOMEMC, "oldmc", "decks", deck))
                                        functions.decks.write_new_deck_to_db(deck[:-5])
                                        if Decks[deck[:-5]]["comm"] != "":
                                                functions.decks.update_comment_deck_to_db(None, deck[:-5], Decks[deck[:-5]]["comm"])
                
                if os.path.isfile(os.path.join(defs.HOMEMC, "collection.txt")):
                        shutil.move(os.path.join(defs.HOMEMC, "collection.txt"), os.path.join(defs.HOMEMC, "oldmc"))
                        Collection = read_oldcollection(os.path.join(defs.HOMEMC, "oldmc", "collection.txt"), Decks)
                        try:
                                Collection = read_oldcollection(os.path.join(defs.HOMEMC, "oldmc", "collection.txt"), Decks)
                        except:
                                GLib.idle_add(functions.various.message_dialog, defs.STRINGS["import_oldformat_error_collection0810"], 0)
                        else:
                                #print(Collection)
                                cards_finder_oldcollection(Collection)
        
        defs.CONVERTING = False

def cards_finder_oldcollection(Collection):
        """This function try to found the old cards in the new database.
        
        """
        
        def show_dialog(final_text_cards_not_found):
                if final_text_cards_not_found != "":
                        dialog = Gtk.Dialog(title=defs.STRINGS["import_conver"], buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK))
                        dialog.set_default_size(600, 400)
                        if defs.MAINWINDOW != None:
                                dialog.set_transient_for(defs.MAINWINDOW)
                                dialog.set_modal(True)
                        label_1 = Gtk.Label(defs.STRINGS["import_oldformat_finish"])
                        label_1.show()
                        label_1.set_max_width_chars(20)
                        label_1.set_line_wrap(True)
                        label_1.set_ellipsize(Pango.EllipsizeMode.END)
                        label_1.set_lines(10)
                        label_1.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                        label = Gtk.Label(final_text_cards_not_found)
                        label.set_selectable(True)
                        label.set_alignment(0.0, 0.5)
                        scrolledwindow = Gtk.ScrolledWindow()
                        scrolledwindow.set_min_content_height(250)
                        scrolledwindow.set_min_content_width(250)
                        scrolledwindow.add_with_viewport(label)
                        scrolledwindow.show_all()
                        
                        content_area = dialog.get_content_area()
                        content_area.props.border_width = 6
                        content_area.pack_start(label_1, True, True, 0)
                        content_area.pack_start(scrolledwindow, True, True, 0)
                        
                        dialog.run()
                        dialog.destroy()
                else:
                        functions.various.message_dialog(defs.STRINGS["import_oldformat_finish_ok"], 0)
        
        cards_found = {}
        cards_not_found = []
        
        conn_db, c_db = functions.db.connect_db()
        conn_coll, c_coll = functions.collection.connect_db()
        
        for card_name, ex_data in Collection.items():
                for ex_code, ids_data in ex_data.items():
                        for old_nb_id, id_data in ids_data.items():
                                tmp_key = card_name + "_" + id_data["nbvariant"] + "_" + ex_code
                                try:
                                        id_card = cards_found[tmp_key]
                                except KeyError:
                                        # we need to search in the database
                                        r_card_name = card_name
                                        tmp_nbvariant = ""
                                        if card_name[-1] == ")" and "/" not in card_name:
                                                if card_name[-2].isdigit():
                                                        tmp_nbvariant = card_name[-2]
                                                        if tmp_nbvariant == "0":
                                                                tmp_nbvariant = "10"
                                        if tmp_nbvariant != "":
                                                r_card_name = r_card_name.replace(" (" + tmp_nbvariant + ")", "")
                                        r_card_name = r_card_name.replace(" (White)", "").replace(" (Blue)", "").replace(" (Black)", "").replace(" (Red)", "").replace(" (Green)", "")
                                        
                                        r_card_name = r_card_name.replace('"', '""')
                                        c_db.execute("""SELECT id FROM cards WHERE name = \"""" + r_card_name + """\" AND nb_variante = \"""" + tmp_nbvariant + """\" AND edition = \"""" + ex_code + """\"""")
                                        responses = c_db.fetchall()
                                        if len(responses) == 0 or len(responses) > 1:
                                                id_card = None
                                        else:
                                                # we found the card !
                                                id_card = responses[0][0]
                                        cards_found[tmp_key] = id_card
                                if id_card == None:
                                        cards_not_found.append([card_name, ex_code, id_data])
                                else:
                                        # we can write this card to the collection
                                        c_coll.execute("""INSERT INTO collection VALUES(null, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (id_card, id_data["date"], id_data["condition"].lower(), id_data["lang"], id_data["foil"], id_data["loaned"], id_data["comment"], id_data["deck"], ""))
        functions.db.disconnect_db(conn_db)
        functions.collection.disconnect_db(conn_coll)
        
        final_text_cards_not_found = ""
        for card in cards_not_found:
                tmp_condition = ""
                if card[2]["condition"] != "":
                        tmp_condition = card[2]["condition"] + ", "
                tmp_lang = ""
                if card[2]["lang"] != "":
                        tmp_lang = card[2]["lang"] + ", "
                tmp_foil = ""
                if card[2]["foil"] == "1":
                        tmp_foil = defs.STRINGS["foil_coll"] + ", "
                tmp_loaned = ""
                if card[2]["loaned"] != "":
                        tmp_loaned = defs.STRINGS["loaned_coll"] + " " + card[2]["loaned"] + ", "
                tmp_comment = ""
                if card[2]["comment"] != "":
                        tmp_comment = card[2]["comment"] + ", "
                tmp_deck = ""
                if card[2]["deck"] != "":
                        tmp_deck = defs.STRINGS["import_useindeck"] + " " + card[2]["deck"] + ", "
                tmp_text = tmp_condition + tmp_lang + tmp_foil + tmp_loaned + tmp_comment + tmp_deck
                try:
                        tmp_text = tmp_text[:-2]
                except:
                        pass
                if tmp_text == "":
                        final_text_cards_not_found = final_text_cards_not_found + card[0] + " - " + functions.various.edition_code_to_longname(card[1]) + "\n"
                else:
                        final_text_cards_not_found = final_text_cards_not_found + card[0] + " - " + functions.various.edition_code_to_longname(card[1]) + " - " + tmp_text + "\n"
        
        if len(final_text_cards_not_found) > 0:
                final_text_cards_not_found = final_text_cards_not_found[:-1]
        
        # we create the dialog
        GLib.idle_add(show_dialog, final_text_cards_not_found)

def read_oldcollection(filepath, Decks):
        """Reads the data in the collection located in filepath (old format).
        
        """
        
        if os.path.isfile(filepath):
                Collection = {}
                
                collection_file = open(filepath, "r", encoding="UTF-8")
                collectiondata = collection_file.readlines()
                collection_file.close()
                
                # the current date
                today = date.today()
                month = '%02d' % today.month
                day = '%02d' % today.day
                current_date = str(today.year) + "-" + str(month) + "-" + str(day)
                
                for z, line in enumerate(collectiondata):
                        if z != 0:
                                line_collection = line.rstrip("\n\r").split(";;;")
                                del(line_collection[-1])
                                
                                nb_ex = int(line_collection[2])
                                card_name = line_collection[0]
                                card_ex = line_collection[1]
                                card_name, card_ex = card_validator_oldformat(card_name, card_ex)
                                if card_name == None:
                                        pass
                                else:
                                        # variant ?
                                        nbvariant = ""
                                        if card_name[-1] == ")" and "/" not in card_name:
                                                if card_name[-2].isdigit():
                                                        nbvariant = card_name[-2]
                                                        if nbvariant == "0":
                                                                nbvariant = "10"
                                        '''if nbvariant != "":
                                                card_name = card_name.replace(" (" + nbvariant + ")", "")'''
                                        
                                        data_card_ids = line_collection[3].replace("{", "}").split("}")
                                        
                                        try:
                                                Collection[card_name]
                                        except KeyError:
                                                Collection[card_name] = {}
                                        Collection[card_name][card_ex] = {}
                                        
                                        for data_id in data_card_ids:
                                                if data_id:
                                                        data_id = data_id.split("|||")
                                                        
                                                        idvar_old = 0
                                                        
                                                        id_card = ""
                                                        condition = ""
                                                        lang = ""
                                                        foil = "0"
                                                        loaned = ""
                                                        comment = ""
                                                        deck = ""
                                                        
                                                        for info in data_id:
                                                                if "id__" in info:
                                                                        idvar_old = info.replace("id__", "")
                                                                elif "etat__" in info:
                                                                        condition = info.replace("etat__", "")
                                                                elif "langue__" in info:
                                                                        lang = info.replace("langue__", "")
                                                                elif "foil__" in info:
                                                                        foil = info.replace("foil__", "")
                                                                elif "pret__" in info:
                                                                        tmploa = info.replace("pret__", "")
                                                                        loaned = tmploa[4:]
                                                                elif "comm__" in info:
                                                                        comment = info.replace("comm__", "")
                                                        
                                                        for tmp_deck_name, tmp_deck_data in Decks.items():
                                                                tmp_list_ids = None
                                                                try:
                                                                        tmp_list_ids = tmp_deck_data["cards"][card_name][card_ex]["list_ids"]
                                                                except:
                                                                        pass
                                                                if tmp_list_ids != None:
                                                                        if idvar_old in tmp_list_ids:
                                                                                deck = tmp_deck_name
                                                        
                                                        Collection[card_name][card_ex][idvar_old] = {"id_card": id_card, "date": current_date, "condition": condition, "lang": lang, "foil": foil, "loaned": loaned, "comment": comment, "deck": deck, "nbvariant": nbvariant}
                                                        
                return(Collection)
        else:
                raise ValueError()
                                

def read_olddeck(filepath):
        """Reads the data in the deck located in filepath (old format).
        
        """
        
        if os.path.isfile(filepath):
                deck_dict = {}
                deck_dict["cards"] = {}
                
                deckfile = open(filepath, "r", encoding="UTF-8")
                deckdata = deckfile.readlines()
                deckfile.close()
                
                for i, elm in enumerate(deckdata):
                        if i == 0:
                                elm = elm.rstrip("\n\r")
                                deck_comm = elm.replace("\"\\n\"", "\n")
                                deck_dict["comm"] = deck_comm
                        elif i == 1:
                                pass
                        else:
                                card_name, ed_code, list_ids = elm.rstrip("\n\r").split(";;;")
                                list_ids = list_ids.split("|")
                                card_name, ed_code = card_validator_oldformat(card_name, ed_code)
                                if card_name != None:
                                        try:
                                                deck_dict["cards"][card_name]
                                        except KeyError:
                                                deck_dict["cards"][card_name] = {}
                                        deck_dict["cards"][card_name][ed_code] = {"list_ids": list_ids}
                return(deck_dict)
        else:
                raise ValueError()

def card_validator_oldformat(card_name, card_ex):
        """Fixes cards' data if needed.
        
        """
        
        # variant ?
        nbvariant = None
        if card_name[-1] == ")" and "/" not in card_name:
                if card_name[-2].isdigit():
                        nbvariant = card_name[-2]
                        if nbvariant == "0":
                                nbvariant = "10"
        if nbvariant != None:
                card_name = card_name.replace(" (" + nbvariant + ")", "")
                
        
        card_name = card_name.replace("AE", "Æ").replace(" [Vanguard]", "")
        if " // " in card_name:
                card_name = card_name.split(" // ")[0]
        
        if card_name == "Who/What/When/Where/Why":
                card_name = "Who"
        if card_name == "B.F.M. (Big Furry Monster) (1)":
                card_name = "B.F.M. (Big Furry Monster) {1}"
        if card_name == "B.F.M. (Big Furry Monster) (2)":
                card_name = "B.F.M. (Big Furry Monster) {2}"
        
        if card_ex == "CSPtd":
                card_ex = "CST"
        
        if card_ex == "KTK":
                if card_name == "Emblem Sarkhan":
                        card_name = "Emblem Sarkhan, the Dragonspeaker"
                if card_name == "Emblem Sorin":
                        card_name = "Emblem Sorin, Solemn Visitor"
        
        if card_ex == "UNH":
                if card_name == "Pegasus (1/1)" or card_name == "Soldier (1/1) (White)" or card_name == "Zombie (1/1)" or card_name == "Goblin (1/1)" or card_name == "Sheep (1/1)" or card_name == "Squirrel (1/1)":
                        card_ex = "UGL"
        
        if card_ex == "PPR":
                if card_name == "Ryusei, the Falling Star" or card_name == "Helm of Kaldra" or card_name == "Sword of Kaldra" or card_name == "Raging Kavu" or card_name == "Questing Phelddagrif" or card_name == "Revenant" or card_name == "Lightning Dragon" or card_name == "Silent Specter" or card_name == "Dirtcowl Wurm" or card_name == "Fungal Shambler" or card_name == "Avatar of Hope" or card_name == "Soul Collector" or card_name == "Monstrous Hound" or card_name == "Rathi Assassin" or card_name == "Glory" or card_name == "Shield of Kaldra" or card_name == "False Prophet" or card_name == "Laquatus's Champion" or card_name == "Overtaker" or card_name == "Beast of Burden":
                        card_ex = "pre"
                if card_name == "Giant Badger" or card_name == "Arena" or card_name == "Feral Throwback" or card_name == "Mana Crypt" or card_name == "Windseeker Centaur" or card_name == "Nalathni Dragon" or card_name == "Sewers of Estark":
                        card_ex = "pmo"
        
        if card_ex == "pmo":
                if card_name == "Daretti, Scrap Savant" or card_name == "Freyalise, Llanowar's Fury" or card_name == "Nahiri, the Lithomancer" or card_name == "Ob Nixilis of the Black Oath" or card_name == "Teferi, Temporal Archmage":
                        card_name = None
                        card_ex = None
        
        if nbvariant != None:
                card_name = card_name + " (" + nbvariant + ")"
        return(card_name, card_ex)
