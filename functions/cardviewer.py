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

# Functions for the card viewer

from gi.repository import Gtk, Gio, GdkPixbuf, Pango, GObject, GLib, Gdk
import cairo
import os
import random
import re
import threading
import time

# imports def.py
import defs
# imports objects
import objects.mc
# imports functions
import functions.various
import functions.prices

def gen_card_viewer(cardid, box_card_viewer, object_origin, simple_search):
        """Generates and returns a card viewer with card's data.
        
        @cardid -> a string (an card's id in the database) or None
        @box_card_viewer -> a Gtk.Box (the parent widget of the card viewer)
        @object_origin -> an AdvancedSearch, Collection or Decks object (indicates the origin of the card viewer request)
        @simple_search -> an int (indicates if the card viewer is used with a simple search or another type of search)
        
        """
        
        # we clear the box_card_viewer
        for widget in box_card_viewer.get_children():
                box_card_viewer.remove(widget)
        
        if cardid == None:
                # if cardid is None, we show a random mana picture. If possible, we choose a different one
                if len(defs.LIST_LANDS_SELECTED) == 5:
                        defs.LIST_LANDS_SELECTED = []
                lchoice = random.choice(["b", "g", "r", "u", "w"])
                while lchoice in defs.LIST_LANDS_SELECTED:
                        lchoice = random.choice(["b", "g", "r", "u", "w"])
                defs.LIST_LANDS_SELECTED.append(lchoice)
                image = Gtk.Image()
                image.set_from_gicon(Gio.ThemedIcon.new_with_default_fallbacks(lchoice + "-symbolic"), Gtk.icon_size_from_name("150_mana_symbol"))
                image.show()
                size = functions.various.card_pic_size()
                image.set_size_request(size, size)
                box_card_viewer.pack_start(image, True, True, 0)
        
        elif cardid != "":
                # we get an id, we load and display the card
                
                # FIXME : chinese variants !
                foreign_name = defs.LOC_NAME_FOREIGN[functions.config.read_config("fr_language")]
                
                # we get the card data
                conn, c = functions.db.connect_db()
                c.execute("""SELECT * FROM cards WHERE id = \"""" + cardid + """\"""")
                reponse = c.fetchall()       
                # we disconnect the database
                functions.db.disconnect_db(conn)         
                
                if len(reponse) > 1:
                        print("Something is wrong in the database. IDs should be unique.")
                else:
                        id_, name, nb_variante, names, edition_code, name_chinesetrad, name_chinesesimp, name_french, name_german, name_italian, name_japanese, name_korean, name_portuguesebrazil, name_portuguese, name_russian, name_spanish, colors, manacost, cmc, multiverseid, imageurl, type_, artist, text, flavor, power, toughness, loyalty, rarity, layout, number, variations = reponse[0]
                        
                        basename = str(name)
                        show_add_button = True
                        
                        # we choose the foreign name to display
                        if foreign_name == "name_chinesetrad":
                                foreign__name = name_chinesetrad
                                nb_foreign = 5
                        elif foreign_name == "name_chinesesimp":
                                foreign__name = name_chinesesimp
                                nb_foreign = 6
                        elif foreign_name == "name_french":
                                foreign__name = name_french
                                nb_foreign = 7
                        elif foreign_name == "name_german":
                                foreign__name = name_german
                                nb_foreign = 8
                        elif foreign_name == "name_italian":
                                foreign__name = name_italian
                                nb_foreign = 9
                        elif foreign_name == "name_japanese":
                                foreign__name = name_japanese
                                nb_foreign = 10
                        elif foreign_name == "name_korean":
                                foreign__name = name_korean
                                nb_foreign = 11
                        elif foreign_name == "name_portuguesebrazil":
                                foreign__name = name_portuguesebrazil
                                nb_foreign = 12
                        elif foreign_name == "name_portuguese":
                                foreign__name = name_portuguese
                                nb_foreign = 13
                        elif foreign_name == "name_russian":
                                foreign__name = name_russian
                                nb_foreign = 14
                        elif foreign_name == "name_spanish":
                                foreign__name = name_spanish
                                nb_foreign = 15
                        else:
                                foreign__name = name_german # why not ?
                                nb_foreign = 8
                        
                        if foreign__name == "":
                                foreign__name = name
                        basenameforeign = str(foreign__name)
                        basetext = str(text)
                        basecolors = str(colors)
                        
                        names_tmp = names.split("|")
                        
                        # some work is needed with split / flip cards
                        if layout == "split" or layout == "aftermath":
                                final_text = ""
                                final_manacost = ""
                                list_cmc = []
                                final_colors = ""
                                final_artist = ""
                                # we try to get the complete manacost, text and the higher cmc
                                for nn in names_tmp:
                                        for card_split_flip in defs.SPLIT_FLIP_DF_DATA:
                                                if card_split_flip[4] == edition_code:
                                                        if nn == card_split_flip[1]:
                                                                final_manacost = final_manacost + card_split_flip[17] + "|"
                                                                list_cmc.append(card_split_flip[18])
                                                                if card_split_flip[22] not in final_artist:
                                                                        final_artist = final_artist + card_split_flip[22] + ", "
                                                                final_text = final_text + card_split_flip[1] + "\n" + card_split_flip[23] + "\n---\n"
                                                                for char in card_split_flip[16]:
                                                                        if char not in final_colors:
                                                                                final_colors = final_colors + char
                                manacost = final_manacost[:-1]
                                cmc = max(list_cmc)
                                text = final_text[:-5]
                                artist = final_artist[:-2]
                                colors = "".join(sorted(final_colors))
                        
                        if layout == "flip":
                                final_text = ""
                                zz = len(names_tmp)
                                # we try to get the complete text
                                for nn in names_tmp:
                                        for card_split_flip in defs.SPLIT_FLIP_DF_DATA:
                                                if card_split_flip[4] == edition_code:
                                                        if nn == card_split_flip[1]:
                                                                if "Creature" in card_split_flip[21]:
                                                                        final_text = final_text + card_split_flip[1] + "\n" + card_split_flip[21] + "\n" + card_split_flip[23] + "\n" + card_split_flip[25] + "/" + card_split_flip[26]
                                                                else:
                                                                        final_text = final_text + card_split_flip[1] + "\n" + card_split_flip[21] + "\n" + card_split_flip[23]
                                                                if zz == 1:
                                                                        pass
                                                                else:
                                                                        final_text = final_text + "\n---\n"
                                        zz -= 1
                                text = final_text
                        
                        if layout != "double-faced":
                                if layout == "flip":
                                        separator = " <> "
                                elif layout == "split":
                                        separator = " // "
                                elif layout == "aftermath":
                                        separator = " / "
                                # we try to get the complete name for english and foreign name
                                final_name = ""
                                if layout == "split":
                                        for nn in names_tmp:
                                                final_name = final_name + separator + nn
                                        name = final_name[4:]
                                elif layout == "aftermath":
                                        for nn in names_tmp:
                                                final_name = final_name + separator + nn
                                        name = final_name[3:]
                                elif layout == "flip":
                                        final_name = name
                                        for nn in names_tmp:
                                                if nn != name:
                                                        final_name = final_name + separator + nn
                                        name = final_name
                                
                                if foreign__name == "":
                                        foreign__name = name
                                else:
                                        final_nameforeign = ""
                                        if layout == "split":
                                                for nn in names_tmp:
                                                        for card_split_flip in defs.SPLIT_FLIP_DF_DATA:
                                                                if card_split_flip[4] == edition_code:
                                                                        if nn == card_split_flip[1]:
                                                                                final_nameforeign = final_nameforeign + separator + card_split_flip[7]
                                                foreign__name = final_nameforeign[4:]
                                        elif layout == "aftermath":
                                                for nn in names_tmp:
                                                        for card_split_flip in defs.SPLIT_FLIP_DF_DATA:
                                                                if card_split_flip[4] == edition_code:
                                                                        if nn == card_split_flip[1]:
                                                                                final_nameforeign = final_nameforeign + separator + card_split_flip[7]
                                                foreign__name = final_nameforeign[3:]
                                        elif layout == "flip":
                                                final_nameforeign = foreign__name
                                                for nn in names_tmp:
                                                        for card_split_flip in defs.SPLIT_FLIP_DF_DATA:
                                                                if card_split_flip[4] == edition_code:
                                                                        if nn == card_split_flip[1]:
                                                                                if card_split_flip[7] != foreign__name:
                                                                                        final_nameforeign = final_nameforeign + separator + card_split_flip[7]
                                                foreign__name = final_nameforeign
                        
                        name_without_variants = str(name)
                        foreign__name_without_variants = str(foreign__name)                        
                        if nb_variante != "":
                                # we add the number of the variant to the name
                                name = name + " (" + nb_variante + ")"
                                foreign__name = foreign__name + " (" + nb_variante + ")"
                        
                        # we get the name of the edition
                        edition_longname = functions.various.edition_code_to_longname(edition_code)
                        
                        ### we create widgets... many widgets ###
                        # the grid
                        grid = Gtk.Grid()
                        grid.set_row_spacing(2)
                        box_card_viewer.pack_start(grid, False, True, 0)
                        
                        first_widget = None
                        nb_columns = 0
                        
                        # the card picture - we need it now
                        card_pic = Gtk.Image()
                        
                        # the top left button - can be a double-faced button, or a flip button, or a meld button, or an empty one
                        df_pic = Gtk.Image()
                        
                        if layout == "double-faced":
                                df_button = Gtk.Button()
                                context_df_button = df_button.get_style_context()
                                style_provider_df_button = Gtk.CssProvider()
                                # we get the id of the other face
                                if id_ in defs.SDF_RECTO_IDS_LIST:
                                        id_otherface = defs.SDF_RECTO_VERSO_IDS_DICT[id_]
                                else:
                                        id_otherface = defs.SDF_VERSO_RECTO_IDS_DICT[id_]
                                
                                df_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="icon_flip_card-symbolic"), Gtk.IconSize.LARGE_TOOLBAR)
                                df_button.connect("clicked", object_origin.load_card_from_outside, str(id_otherface), [], simple_search)
                                df_button.set_tooltip_text(defs.STRINGS["dfbutton_seeotherside_tooltip"])
                                Gtk.StyleContext.add_provider(context_df_button, style_provider_df_button, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                        elif layout == "flip" or basename == "Curse of the Fire Penguin":
                                df_button = Gtk.Button()
                                context_df_button = df_button.get_style_context()
                                style_provider_df_button = Gtk.CssProvider()
                                df_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="object-flip-vertical-symbolic"), Gtk.IconSize.SMALL_TOOLBAR)
                                df_button.connect("clicked", vertical_flip_pic, card_pic)
                                df_button.set_tooltip_text(defs.STRINGS["dfbutton_returncard_tooltip"])
                                Gtk.StyleContext.add_provider(context_df_button, style_provider_df_button, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                        elif layout == "meld":
                                # we get the id(s)
                                if id_ in defs.MELD_IDS_LIST:
                                        df_button = Gtk.Button()
                                        context_df_button = df_button.get_style_context()
                                        style_provider_df_button = Gtk.CssProvider()
                                        id_melded = defs.MELD_MELDED_IDS_DICT[id_]
                                        df_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="icon_meld-symbolic"), Gtk.IconSize.LARGE_TOOLBAR)
                                        df_button.connect("clicked", object_origin.load_card_from_outside, str(id_melded), [], simple_search)
                                        df_button.set_tooltip_text(defs.STRINGS["dfbutton_meldsto_tooltip"])
                                        Gtk.StyleContext.add_provider(context_df_button, style_provider_df_button, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                                else:
                                        show_add_button = False
                                        df_button = Gtk.MenuButton()
                                        context_df_button = df_button.get_style_context()
                                        style_provider_df_button = Gtk.CssProvider()
                                        df_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="icon_meld-symbolic"), Gtk.IconSize.LARGE_TOOLBAR)
                                        df_button.set_tooltip_text(defs.STRINGS["dfbutton_meldedfrom_tooltip"])
                                        Gtk.StyleContext.add_provider(context_df_button, style_provider_df_button, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                                        
                                        meld_menu = Gtk.Menu()
                                        cards_meld_list = []
                                        
                                        for id_meld in defs.MELDED_MELD_IDS_DICT[id_]:
                                                if id_meld != id_:
                                                        for meld_data in defs.MELD_DATA:
                                                                if meld_data[0] == id_meld:
                                                                        name_meld = meld_data[1]
                                                                        nameforeign_meld = meld_data[nb_foreign]
                                                                        variant_meld = meld_data[2]
                                                                        if variant_meld != "":
                                                                                space_meld = " "
                                                                                variant_meld = "(" + variant_meld + ")"
                                                                        else:
                                                                                space_meld = ""
                                                                        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys() and foreign__name != "":
                                                                                tmp_name_meld = nameforeign_meld + space_meld + variant_meld
                                                                        else:
                                                                                tmp_name_meld = name_meld + space_meld + variant_meld
                                                                        cards_meld_list.append([id_meld, tmp_name_meld])
                                                                        
                                        cards_meld_list = sorted(cards_meld_list, key=getKey)
                                        for tmp_name_id_meld in cards_meld_list:
                                                id___, tmp_name_meld = tmp_name_id_meld
                                                menu_item = Gtk.MenuItem(tmp_name_meld)
                                                menu_item.connect("activate", object_origin.load_card_from_outside, id___, [meld_menu, None], 1)
                                                menu_item.show()
                                                meld_menu.append(menu_item)
                                        df_button.set_popup(meld_menu)
                        else:
                                # the button is empty
                                df_button = Gtk.Button()
                                context_df_button = df_button.get_style_context()
                                style_provider_df_button = Gtk.CssProvider()
                                df_button.set_sensitive(False)
                                df_button.set_tooltip_text("")
                        
                        df_button.set_relief(Gtk.ReliefStyle.NONE)
                        # we load a specific CSS for this widget
                        if defs.GTK_MINOR_VERSION >= 20:
                                widget_name = "button"
                        else:
                                widget_name = "GtkButton"
                        css = """
                        """ + widget_name + """ {
                        padding-left: 0px;
                        padding-right: 0px;
                        }
                        """
                        style_provider_df_button.load_from_data(bytes(css.encode()))
                        
                        df_button.add(df_pic)
                        grid.attach(df_button, 0, 0, 1, 1)
                        first_widget = df_button
                        nb_columns += 1
                        
                        # We now prepare 2 labels : one with the foreign name, and the other with the english name of the card.
                        # If LANGUAGE == en, we only show the english one. Else we read the configuration :
                        # If "show_en_name_in_card_viewer" is 0, we only show the foreign name. Else, we show the 2 widgets. If the card has only an english name, we show it.
                        
                        show_en_name_in_card_viewer = functions.config.read_config("show_en_name_in_card_viewer")
                        # the non-english name. If this card do not have a foreign name, the label is empty.
                        label_name_foreign = Gtk.Label()
                        label_name_foreign.set_size_request(200, -1)
                        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys() and basenameforeign != "":
                                label_name_foreign.set_markup("<b>" + foreign__name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</b>")
                                if len(foreign__name) > 29:
                                        label_name_foreign.set_has_tooltip(True)
                                        label_name_foreign.set_tooltip_text(foreign__name)
                                label_name_foreign.set_selectable(True)
                                label_name_foreign.set_max_width_chars(20)
                                label_name_foreign.set_line_wrap(True)
                                label_name_foreign.set_lines(2)
                                label_name_foreign.set_ellipsize(Pango.EllipsizeMode.END)
                                label_name_foreign.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                                label_name_foreign.set_justify(Gtk.Justification.CENTER)
                        
                        # the english name
                        label_name = Gtk.Label()
                        label_name.set_markup("<b>" + name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</b>")
                        if len(name) > 29:
                                label_name.set_has_tooltip(True)
                                label_name.set_tooltip_text(name)
                        label_name.set_selectable(True)
                        label_name.set_max_width_chars(25)
                        label_name.set_line_wrap(True)
                        label_name.set_lines(1)
                        label_name.set_ellipsize(Pango.EllipsizeMode.END)
                        label_name.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                        label_name.set_size_request(200, -1)
                        
                        if defs.LANGUAGE == "en":
                                label_name_1 = label_name
                                label_name_2 = label_name
                        else:
                                if basenameforeign != "":
                                        label_name_1 = label_name_foreign
                                else:
                                        label_name_1 = label_name
                                if show_en_name_in_card_viewer == "1":
                                        label_name_2 = label_name
                                elif basenameforeign != "":
                                        label_name_2 = label_name_foreign
                                else:
                                        label_name_2 = label_name
                        
                        grid.attach_next_to(label_name_1, df_button, Gtk.PositionType.RIGHT, 1, 1)
                        nb_columns += 1
                        
                        # cmc / manacost button
                        if manacost == "" and cmc == "0":
                                cmc_button = Gtk.MenuButton()
                                empty_pic = Gtk.Image()
                                cmc_button.add(empty_pic)
                                cmc_button.set_sensitive(False)
                        else:
                                cmc_button = Gtk.MenuButton("")
                                if cmc == "1000000":
                                        cmc_button.get_child().set_markup("<small>..</small>") # workaround for 'Gleemax'
                                elif len(cmc) > 1:
                                        cmc_button.get_child().set_markup("<small>" + cmc + "</small>")
                                else:
                                        cmc_button.set_label(cmc)
                                if manacost != "":
                                        manacost_popover = gen_manacost_popover(cmc_button, manacost)
                                        cmc_button.set_popover(manacost_popover)
                                        cmc_button.set_sensitive(True)
                                # we load a specific CSS for this widget
                                context_cmc_button = cmc_button.get_style_context()
                                style_provider_cmc_button = Gtk.CssProvider()
                                if defs.GTK_MINOR_VERSION >= 20:
                                        widget_name = "button"
                                else:
                                        widget_name = "GtkMenuButton"
                                css = """
                                """ + widget_name + """ {
                                padding-left: 8px;
                                padding-right: 8px;
                                }
                                """
                                style_provider_cmc_button.load_from_data(bytes(css.encode()))
                                Gtk.StyleContext.add_provider(context_cmc_button, style_provider_cmc_button, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                                
                        cmc_button.set_relief(Gtk.ReliefStyle.NONE)
                        grid.attach_next_to(cmc_button, label_name_1, Gtk.PositionType.RIGHT, 1, 1)
                        nb_columns += 1
                        
                        # we show the label_name_2, if needed
                        if label_name_1 != label_name_2:
                                grid.attach_next_to(label_name_2, first_widget, Gtk.PositionType.BOTTOM, nb_columns, 1)
                        
                        # the edition label
                        label_edition = Gtk.Label(edition_longname)
                        if len(edition_longname) > 29:
                                label_edition.set_has_tooltip(True)
                                label_edition.set_tooltip_text(edition_longname)
                        label_edition.set_selectable(True)
                        label_edition.set_max_width_chars(25)
                        label_edition.set_line_wrap(True)
                        label_edition.set_lines(1)
                        label_edition.set_ellipsize(Pango.EllipsizeMode.END)
                        label_edition.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                        label_edition.set_size_request(230, -1)
                        
                        if label_name_1 != label_name_2:
                                grid.attach_next_to(label_edition, label_name_2, Gtk.PositionType.BOTTOM, nb_columns, 1)
                        else:
                                grid.attach_next_to(label_edition, first_widget, Gtk.PositionType.BOTTOM, nb_columns, 1)
                        
                        # we prepare the card picture (will be loaded latter)
                        overlay_card_pic = Gtk.Overlay()
                        eventbox_card_pic = Gtk.EventBox()
                        
                        # we have to replace some characters in the name because the markup syntax
                        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                                name_for_add_popover = foreign__name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        else:
                                name_for_add_popover = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        
                        add_pic = Gtk.Image()
                        eventbox = Gtk.EventBox()
                        if show_add_button:
                                eventbox.connect("button-press-event", add_button_clicked, eventbox_card_pic, overlay_card_pic, object_origin, simple_search, name_for_add_popover, edition_longname, id_)
                        overlay_card_pic.add_overlay(eventbox)
                        eventbox.add(add_pic)
                        eventbox.show_all()
                        
                        eventbox_card_pic.add(card_pic)
                        overlay_card_pic.add(eventbox_card_pic)
                        
                        path = os.path.join(defs.CACHEMCPIC, "cardback.png")

                        # we try to load cardback.png. If we get a GLib error, then the picture is corrupted, and we delete it
                        try:
                                pixbuf = functions.various.gdkpixbuf_new_from_file(path)
                        except GLib.GError:
                                os.remove(path)
                        else:
                                size = functions.various.card_pic_size()
                                pixbuf_width = pixbuf.get_width()
                                pixbuf_height = pixbuf.get_height()
                                if pixbuf_width > size or pixbuf_height > size:
                                        pix_size = size
                                else:
                                        pix_size = max(pixbuf_width, pixbuf_height)
                                
                                pixbuf = functions.various.gdkpixbuf_new_from_file_at_size(path, pix_size, pix_size)
                                card_pic.set_from_pixbuf(pixbuf)
                                card_pic.set_size_request(size, size)
                        
                        grid.attach_next_to(overlay_card_pic, label_edition, Gtk.PositionType.BOTTOM, nb_columns, 1)
                        
                        # the colors picture
                        colors_pic = Gtk.Image()
                        if colors != "":
                                pixbuf = functions.various.gdkpixbuf_new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "color_indicators", colors.lower() + ".png"), 22, 22)
                        else:
                                pixbuf = functions.various.gdkpixbuf_new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "nothing.png"), 22, 22)
                        colors_pic.set_from_pixbuf(pixbuf)
                        grid.attach_next_to(colors_pic, overlay_card_pic, Gtk.PositionType.BOTTOM, 1, 1)
                        
                        # the type
                        label_type = Gtk.Label(type_)
                        if len(type_) > 24:
                                label_type.set_has_tooltip(True)
                                label_type.set_tooltip_text(type_)
                        label_type.set_selectable(True)
                        label_type.set_max_width_chars(25)
                        label_type.set_line_wrap(True)
                        label_type.set_lines(1)
                        label_type.set_ellipsize(Pango.EllipsizeMode.END)
                        label_type.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                        label_type.set_size_request(200, -1)
                        grid.attach_next_to(label_type, colors_pic, Gtk.PositionType.RIGHT, 1, 1)
                        
                        # the edition picture
                        edition_pic = Gtk.Image()
                        if os.path.isfile(os.path.join(defs.CACHEMCPIC, "icons", functions.various.valid_filename_os(edition_code) + ".png")):
                                pixbuf = functions.various.gdkpixbuf_new_from_file_at_size(os.path.join(defs.CACHEMCPIC, "icons", functions.various.valid_filename_os(edition_code) + ".png"), 22, 22)
                        else:
                                pixbuf = functions.various.gdkpixbuf_new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "nothing.png"), 22, 22)
                        edition_pic.set_from_pixbuf(pixbuf)
                        grid.attach_next_to(edition_pic, label_type, Gtk.PositionType.RIGHT, 1, 1)
                        
                        # the text widget
                        manacol = ""
                        # if the card is a basic land or a snow one, we replace the text box with a mana picture
                        if basename == "Plains" or basename == "Snow-Covered Plains":
                                manacol = "w"
                        elif basename == "Swamp" or basename == "Snow-Covered Swamp":
                                manacol = "b"
                        elif basename == "Mountain" or basename == "Snow-Covered Mountain":
                                manacol = "r"
                        elif basename == "Forest" or basename == "Snow-Covered Forest":
                                manacol = "g"
                        elif basename == "Island" or basename == "Snow-Covered Island":
                                manacol = "u"
                        elif basename == "Wastes":
                                manacol = "c"
                        
                        if manacol == "":
                                if text == "" and flavor == "":
                                        widget = Gtk.Label("")
                                        widget.set_vexpand(True)
                                else:
                                        widget = Gtk.ScrolledWindow()
                                        widget.set_min_content_height(100)
                                        widget.set_vexpand(True)
                                        widget.set_shadow_type(Gtk.ShadowType.IN)
                                        
                                        textview = Gtk.TextView()
                                        textview.set_left_margin(2)
                                        textview.set_right_margin(2)
                                        textbuffer = textview.get_buffer()
                                        texttagItalic = textbuffer.create_tag("Italic", style=Pango.Style.ITALIC)
                                        textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
                                        textview.set_editable(False)
                                        
                                        text_final = ""
                                        if text == "" or flavor == "":
                                                text_final = text + flavor
                                        else:
                                                text_final = text + "\n\n" + flavor
                                        textbuffer.set_text(text_final)
                                        
                                        # flavor in italic
                                        start_iter = textbuffer.get_start_iter()
                                        found = start_iter.forward_search(flavor, 0, None)
                                        if found:
                                                match_start, match_end = found
                                                textbuffer.apply_tag(texttagItalic, match_start, match_end)
                                        
                                        # we replace {?} by pictures (see PIC_IN_TEXT in defs.py)
                                        nb_to_replace = 0
                                        for char in text_final:
                                                if char == "{":
                                                        nb_to_replace += 1
                                        if nb_to_replace > 0:
                                                for nb in range(nb_to_replace):
                                                        for text_to_search, info_pic in defs.PIC_IN_TEXT.items():
                                                                file_name = info_pic[0]
                                                                size = info_pic[1]
                                                                start_iter = textbuffer.get_start_iter()
                                                                found = start_iter.forward_search(text_to_search, 0, None)
                                                                if found:
                                                                        match_start, match_end = found
                                                                        pixbuf = functions.various.gdkpixbuf_new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "symbols", file_name), size, size)
                                                                        textbuffer.insert_pixbuf(match_start, pixbuf)
                                                                        # we delete this text
                                                                        start_iter = textbuffer.get_start_iter()
                                                                        found = start_iter.forward_search(text_to_search, 0, None)
                                                                        if found:
                                                                                match_start, match_end = found
                                                                                textbuffer.delete(match_start, match_end)
                                                                        
                                        widget.add(textview)
                        else:
                                widget = Gtk.Image()
                                widget.set_from_gicon(Gio.ThemedIcon.new_with_default_fallbacks(manacol + "-symbolic"), Gtk.icon_size_from_name("100_mana_symbol"))
                                widget.set_vexpand(True)
                        grid.attach_next_to(widget, colors_pic, Gtk.PositionType.BOTTOM, nb_columns, 1)
                        
                        # buttonmenu "more" - other editions, open Gatherer, price
                        more_button = Gtk.MenuButton()
                        more_button.set_tooltip_text(defs.STRINGS["morebutton_tooltip"])
                        more_popover = gen_more_popover(more_button, multiverseid, basename, nb_variante, edition_code, name_without_variants, foreign__name_without_variants, object_origin, id_, type_, basetext, power, toughness, basecolors)
                        if more_popover == None:
                                more_pic = Gtk.Image.new_from_file(os.path.join(defs.PATH_MC, "images", "nothing.png"))
                                more_button.set_sensitive(False)
                                more_button.set_relief(Gtk.ReliefStyle.NONE)
                        else:
                                more_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="content-loading-symbolic"), Gtk.IconSize.BUTTON)
                                more_button.set_popover(more_popover)
                                more_button.set_sensitive(True)
                        more_button.add(more_pic)
                        grid.attach_next_to(more_button, widget, Gtk.PositionType.BOTTOM, 1, 1)
                        
                        # the artist
                        label_artist = Gtk.Label()
                        label_artist.set_markup("<small>" + artist.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</small>")
                        if len(artist) > 29:
                                label_artist.set_has_tooltip(True)
                                label_artist.set_tooltip_text(artist)
                        label_artist.set_selectable(True)
                        label_artist.set_max_width_chars(25)
                        label_artist.set_line_wrap(True)
                        label_artist.set_lines(1)
                        label_artist.set_ellipsize(Pango.EllipsizeMode.END)
                        label_artist.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                        label_artist.set_size_request(200, -1)
                        grid.attach_next_to(label_artist, more_button, Gtk.PositionType.RIGHT, 1, 1)
                        
                        # the label for power / toughness or loyalty
                        if power != "" or loyalty != "":
                                if loyalty != "":
                                        label_ptl = Gtk.Label(loyalty)
                                else:
                                        label_ptl = Gtk.Label(power + "/" + toughness)
                                label_ptl.set_selectable(True)
                                grid.attach_next_to(label_ptl, label_artist, Gtk.PositionType.RIGHT, 1, 1)
                        
                        box_card_viewer.show_all()
                        
                        flip_pic = False
                        if layout == "flip":
                                if basename != names_tmp[0]:
                                        flip_pic = True
                        
                        # we download / load the picture of the card now, according to the configuration
                        pic_ok = 0
                        size = functions.various.card_pic_size()
                        if functions.various.check_card_pic(edition_code, name):
                                path = os.path.join(defs.CACHEMCPIC, functions.various.valid_filename_os(edition_code), functions.various.valid_filename_os(name) + ".full.jpg") # for historical reason, we save files with a jpg extension, even if recent files are png.
                                try:
                                        pixbuf = functions.various.gdkpixbuf_new_from_file(path)
                                        pic_ok = 1
                                        if show_add_button:
                                                add_pic.set_from_file(os.path.join(defs.PATH_MC, "images", "add.png"))
                                except GLib.GError:
                                        os.remove(path)
                        
                        # we apply rounded corners to the picture. The radius depends of the type of the card or of the origin of the picture
                        radius = 13
                        if imageurl != "":
                                radius = 7
                        if type_[:7] == "Plane —":
                                radius = 18
                        
                        if pic_ok == 0:
                                origin = object_origin.__class__.__name__
                                if origin == "AdvancedSearch":
                                        download_pic = functions.config.read_config("download_pic_as")
                                elif origin == "Collection" or origin == "Decks":
                                        download_pic = functions.config.read_config("download_pic_collection_decks")
                                
                                if download_pic == "1":
                                        # we download the picture in another thread
                                        spinner = Gtk.Spinner()
                                        overlay_card_pic.add_overlay(spinner)
                                        spinner.show()
                                        spinner.start()
                                        thread = threading.Thread(target = dd_card_pic, args = (object_origin, edition_code, name, multiverseid, imageurl, layout, card_pic, spinner, radius, flip_pic, add_pic))
                                        thread.daemon = True
                                        thread.start()
                        else:
                                load_card_picture(path, pixbuf, card_pic, 1, layout, radius, flip_pic)
                                if show_add_button:
                                        add_pic.set_from_file(os.path.join(defs.PATH_MC, "images", "add.png"))

        else:
                print("Something is wrong. We shouldn't get an empty cardid.")

def getKey(item):
        """We use this to correctly sort some characters."""
        return(functions.various.remove_accented_char(item[1].lower().replace("œ", "oe").replace("æ", "ae")))

def add_button_clicked(eventbox, signal, eventbox_pic_card, overlay, object_origin, simple_search, name_for_add_popover_ss, edition_longname_ss, id_ss):
        """This function creates the popover which allows the user to add cards to his / her collection.
        
        @eventbox -> the Gtk.EventBox where the add button is displayed
        @signal -> the signal received by @eventbox
        @eventbox_pic_card -> the Gtk.EventBox where the card picture is displayed
        @overlay -> the Gtk.Overlay above the card picture
        @object_origin -> an AdvancedSearch, Collection or Decks object (indicates the origin of the card viewer request)
        @simple_search -> an int (indicates if the card viewer is used with a simple search or another type of search)
        @name_for_add_popover_ss -> a str. If @simple_search is 1, this string contains the name of the displayed card, to show it in the popover. Not used if @simple_search is not 1.
        @edition_longname_ss -> a str. Like @name_for_add_popover_ss, but for the edition of the card.
        @id_ss -> a str. Like @name_for_add_popover_ss, but for the id of the card.
        
        """
        
        def radiobutton_collection_toggled(radiobutton, expander, scrolledwindow_decks, side_checkbutton):
                if radiobutton.get_active():
                        expander.show()
                        scrolledwindow_decks.hide()
                        side_checkbutton.hide()
        
        def radiobutton_proxies_toggled(radiobutton, expander, scrolledwindow_decks, select_list_decks, side_checkbutton):
                if radiobutton.get_active():
                        expander.hide()
                        scrolledwindow_decks.show()
                        side_checkbutton.show()
                        model, pathlist = select_list_decks.get_selected_rows()
                        if len(pathlist) == 0:
                                select_list_decks.select_path(0)
        
        cards_selected_list = []
        
        nb_decks = 0
        if object_origin == defs.MAINWINDOW.decks:
                conn_coll, c_coll = functions.collection.connect_db()
                c_coll.execute("""SELECT id_deck, name FROM decks""")
                decks_names = c_coll.fetchall()
                nb_decks = len(decks_names)
                functions.collection.disconnect_db(conn_coll)
        # we get the current selection - in the mainselect treeview
        selection = object_origin.mainselect
        try:
                count = selection.count_selected_rows()
        except AttributeError:
                count = 0
        if simple_search == 0 and count > 0:
                # not a simple search, we need to get the data to display from the treeview
                model, pathlist = selection.get_selected_rows()
                for path in pathlist :
                        tree_iter = model.get_iter(path)
                        id_ = model.get_value(tree_iter, 0)
                        name = model.get_value(tree_iter, 1)
                        name_foreign = model.get_value(tree_iter, 3)
                        edition = model.get_value(tree_iter, 2)
                        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                                name_for_add_popover = name_foreign.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        else:
                                name_for_add_popover = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        if name_for_add_popover[0] == "|" and name_for_add_popover[-1] == "|":
                                # sideboard detected
                                name_for_add_popover = name_for_add_popover[:-1].replace("|" + defs.STRINGS["decks_sideboard"], "")
                        if name_for_add_popover[:3] == "-- ":
                                # proxy detected, we need to delete the "-- "
                                name_for_add_popover = name_for_add_popover[3:]
                        if id_ not in defs.MELDED_IDS_LIST:
                                cards_selected_list.append([str(id_), name_for_add_popover, edition])
                                #FIXME: generating and closing the popover when many many rows are selected is slow and can freeze MC (??!!), so we limit to 500
                                if count > 500:
                                        break
        else:
                cards_selected_list.append([str(id_ss), name_for_add_popover_ss, edition_longname_ss])
        
        # if cards in this list are flip - split - double-faced cards, we try to get the real id and the real name
        i = 0
        for card in cards_selected_list:
                id__ = card[0]
                ed_code = functions.various.edition_longname_to_code(card[2])
                for fsdf_cards in defs.SPLIT_FLIP_DF_DATA:
                        if str(fsdf_cards[0]) == str(id__):
                                # we find it, so it's a flip - split - double-faced card
                                # if the name is different of the first names
                                first_names = fsdf_cards[3].split("|")[0]
                                if first_names != fsdf_cards[1]:
                                        # flip card, double-faced card : we need the correct name and the correct id
                                        # split card : we need the correct id
                                        for fsdf_cards2 in defs.SPLIT_FLIP_DF_DATA:
                                                if fsdf_cards2[1] == first_names and fsdf_cards2[4] == ed_code:
                                                        # the id
                                                        cards_selected_list[i][0] = str(fsdf_cards2[0])
                                                        # the name
                                                        if fsdf_cards[29] == "flip" or fsdf_cards[29] == "double-faced":
                                                                en_name = first_names
                                                                foreign_name = defs.LOC_NAME_FOREIGN[functions.config.read_config("fr_language")]
                                                                # we choose the foreign name
                                                                # FIXME : chinese and name_portuguese variants !
                                                                if foreign_name == "name_chinesetrad":
                                                                        nameforeign = fsdf_cards2[5]
                                                                elif foreign_name == "name_chinesesimp":
                                                                        nameforeign = fsdf_cards2[6]
                                                                elif foreign_name == "name_french":
                                                                        nameforeign = fsdf_cards2[7]
                                                                elif foreign_name == "name_german":
                                                                        nameforeign = fsdf_cards2[8]
                                                                elif foreign_name == "name_italian":
                                                                        nameforeign = fsdf_cards2[9]
                                                                elif foreign_name == "name_japanese":
                                                                        nameforeign = fsdf_cards2[10]
                                                                elif foreign_name == "name_korean":
                                                                        nameforeign = fsdf_cards2[11]
                                                                elif foreign_name == "name_portuguesebrazil":
                                                                        nameforeign = fsdf_cards2[12]
                                                                elif foreign_name == "name_portuguese":
                                                                        nameforeign = fsdf_cards2[13]
                                                                elif foreign_name == "name_russian":
                                                                        nameforeign = fsdf_cards2[14]
                                                                elif foreign_name == "name_spanish":
                                                                        nameforeign = fsdf_cards2[15]
                                                                else:
                                                                        nameforeign = fsdf_cards2[8] # why not ?
                                                                if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                                                                        cards_selected_list[i][1] = nameforeign.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                                                                else:
                                                                        cards_selected_list[i][1] = en_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                                elif fsdf_cards[29] == "flip":
                                        cards_selected_list[i][1] = cards_selected_list[i][1].split(" &lt;&gt; ")[0]
                                else:
                                        break
                i += 1
        
        cards_selected_list = sorted(cards_selected_list, key=getKey)
        # we delete double ids, if any
        cards_selected_list2 = []
        for itm in cards_selected_list:
                if itm not in cards_selected_list2:
                        cards_selected_list2.append(itm)
        cards_selected_list = cards_selected_list2
        
        popover = Gtk.Popover.new(eventbox_pic_card)
        popover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        popover_box.set_margin_top(5)
        popover_box.set_margin_bottom(5)
        popover_box.set_margin_left(5)
        popover_box.set_margin_right(5)
        overlay_labels = None
        
        # we prepare the content of the popover
        if len(cards_selected_list) == 1:
                label_add = Gtk.Label()
                # if we are in the Decks mode, we ask for proxy
                if nb_decks > 0:
                        label_add.set_markup(defs.STRINGS["add_card_question_without_collection"].replace("%%%", "<b>" + cards_selected_list[0][1] + " (" + cards_selected_list[0][2] + ")</b>"))
                else:
                        label_add.set_markup(defs.STRINGS["add_card_question"].replace("%%%", "<b>" + cards_selected_list[0][1] + " (" + cards_selected_list[0][2] + ")</b>"))
                label_add.set_max_width_chars(70)
                label_add.set_line_wrap(True)
                label_add.set_lines(3)
                label_add.set_ellipsize(Pango.EllipsizeMode.END)
                label_add.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                popover_box.pack_start(label_add, True, True, 0)
                separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                popover_box.pack_start(separator, True, True, 0)
        else:
                # if we are in the Decks mode, we ask for proxy
                if nb_decks > 0:
                        label_add = Gtk.Label(defs.STRINGS["add_cards_question_without_collection"].replace("%%%", str(len(cards_selected_list))))
                else:
                        label_add = Gtk.Label(defs.STRINGS["add_cards_question"].replace("%%%", str(len(cards_selected_list))))
                popover_box.pack_start(label_add, True, True, 0)
                if len(cards_selected_list) > 100:
                        label_warning = Gtk.Label()
                        label_warning.set_markup("<small><b>" + defs.STRINGS["warning_nb_card"] + "</b></small>")
                        popover_box.pack_start(label_warning, True, True, 0)
                separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                popover_box.pack_start(separator, True, True, 0)
                box_labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                if len(cards_selected_list) > 6:
                        overlay_labels = Gtk.Overlay()
                        scrolledwindow_labels = Gtk.ScrolledWindow()
                        scrolledwindow_labels.set_min_content_height(150)
                        scrolledwindow_labels.set_min_content_width(400)
                        overlay_labels.add(scrolledwindow_labels)
                        popover_box.pack_start(overlay_labels, True, True, 0)
                        scrolledwindow_labels.add_with_viewport(box_labels)
                else:
                        popover_box.pack_start(box_labels, True, True, 0)
                for card_data in cards_selected_list:
                        label_tmp = Gtk.Label()
                        label_tmp.set_markup("<b>" + card_data[1] + " (" + card_data[2] + ")</b>")
                        label_tmp.set_max_width_chars(70)
                        label_tmp.set_line_wrap(True)
                        label_tmp.set_lines(3)
                        label_tmp.set_ellipsize(Pango.EllipsizeMode.END)
                        label_tmp.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                        label_tmp.set_alignment(0.0, 0.5)
                        box_labels.pack_start(label_tmp, True, True, 0)
                separator2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                popover_box.pack_start(separator2, True, True, 0)
        
        radiobutton_proxies = None
        select_list_decks = None
        side_checkbutton = None
        # if we are in the Decks mode, we ask for proxy
        if nb_decks > 0:
                box_radio_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                box_radio_buttons.set_halign(Gtk.Align.CENTER)
                radiobutton_collection = Gtk.RadioButton(label=defs.STRINGS["cv_add_collection"])
                if len(cards_selected_list) == 1:
                        radiobutton_proxies = Gtk.RadioButton(label=defs.STRINGS["cv_add_proxies"], group=radiobutton_collection)
                else:
                        radiobutton_proxies = Gtk.RadioButton(label=defs.STRINGS["cv_add_proxies_s"], group=radiobutton_collection)
                box_radio_buttons.pack_start(radiobutton_collection, False, False, 0)
                box_radio_buttons.pack_start(radiobutton_proxies, False, False, 0)
                popover_box.pack_start(box_radio_buttons, False, False, 0)
                
                scrolledwindow_decks = Gtk.ScrolledWindow()
                scrolledwindow_decks.set_min_content_width(150)
                scrolledwindow_decks.set_min_content_height(150)
                scrolledwindow_decks.set_hexpand(True)
                scrolledwindow_decks.set_shadow_type(Gtk.ShadowType.IN)
                # id_deck, name
                store_list_decks = Gtk.ListStore(str, str)
                
                tree_decks = Gtk.TreeView(store_list_decks)
                tree_decks.set_enable_search(False)
                tree_decks.show()
                renderer_decks = Gtk.CellRendererText()
                column_name_decks = Gtk.TreeViewColumn(defs.STRINGS["list_decks_nb"].replace("(%%%)", ""), renderer_decks, text=1)
                
                column_name_decks.set_sort_column_id(1)
                store_list_decks.set_sort_column_id(1, Gtk.SortType.ASCENDING)
                tree_decks.append_column(column_name_decks)
                
                select_list_decks = tree_decks.get_selection()
                
                for id_deck, name in decks_names:
                        store_list_decks.append([str(id_deck), name])
                
                scrolledwindow_decks.add(tree_decks)
                scrolledwindow_decks.set_no_show_all(True)
                side_checkbutton = Gtk.CheckButton(label=defs.STRINGS["decks_add_to_sideboard"])
                side_checkbutton.set_no_show_all(True)
                popover_box.pack_start(scrolledwindow_decks, False, False, 0)
                popover_box.pack_start(side_checkbutton, False, False, 0)
        
        box_quantity = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        label_quantity = Gtk.Label(defs.STRINGS["quantity"])
        box_quantity.pack_start(label_quantity, False, False, 0)
        adjustment = Gtk.Adjustment(value=1, lower=1, upper=100, step_increment=1, page_increment=10, page_size=0)
        spinbutton = Gtk.SpinButton(adjustment=adjustment)
        box_quantity.pack_start(spinbutton, False, False, 0)
        popover_box.pack_start(box_quantity, False, False, 0)
        
        expander = Gtk.Expander()
        label_expander = Gtk.Label()
        label_expander.set_markup("<b>" + defs.STRINGS["details"] + "</b>")
        expander.set_label_widget(label_expander)
        expander.set_spacing(4)
        popover_box.pack_start(expander, True, True, 0)
        popover.add(popover_box)
        
        # if we are in the Decks mode, we ask for proxy
        if nb_decks > 0:
                radiobutton_collection.connect("toggled", radiobutton_collection_toggled, expander, scrolledwindow_decks, side_checkbutton)
                radiobutton_proxies.connect("toggled", radiobutton_proxies_toggled, expander, scrolledwindow_decks, select_list_decks, side_checkbutton)
        
        grid_details, label_add_condition, comboboxtext_condition, label_add_lang, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, label_add_comment, scrolledwindow, textview = functions.various.gen_details_widgets()
        
        # we set the default values
        df_condition = functions.config.read_config("default_condition")
        if df_condition != "0":
                for nb, cond in defs.CONDITIONS.items():
                        if cond[0] == df_condition:
                                comboboxtext_condition.set_active(int(nb))
                                break
        
        df_lang = functions.config.read_config("default_lang")
        if df_lang != "0":
                entry_lang.set_text(df_lang)
        
        
        expander.add(grid_details)
        
        show_details = functions.config.read_config("add_collection_show_details")
        if show_details == "1":
                expander.set_expanded(True)
        
        if defs.COLL_LOCK:
                button_add = Gtk.Button(defs.STRINGS["add_button_wait"])
                button_add.set_sensitive(False)
        else:
                button_add = Gtk.Button(defs.STRINGS["add_button_validate"])
        button_add.connect("clicked", button_add_clicked, popover, spinbutton, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview, cards_selected_list, overlay_labels, radiobutton_proxies, select_list_decks, side_checkbutton)
        defs.BUTTON_COLL_LOCK = button_add
        popover_box.pack_start(button_add, True, True, 0)
        
        eventbox.remove(eventbox.get_child())
        add_pic = Gtk.Image.new_from_file(os.path.join(defs.PATH_MC, "images", "add_push.png"))
        eventbox.add(add_pic)
        add_pic.show()
        
        popover.connect("closed", popover_add_close, eventbox)
        popover.set_position(Gtk.PositionType.RIGHT)
        popover.show_all()

def button_add_clicked(button_add, popover, spinbutton, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview, cards_selected_list, overlay_labels, radiobutton_proxies, select_list_decks, side_checkbutton):
        """This is called when the user clicks on the add to the collection button. It adds the selected cards to the collection or to the deck selected if the proxy mode is enabled.
        
        @button_add -> the 'add to the collection' GtkButton
        @popover -> the 'add to the collection' GtkPopover
        @spinbutton -> the GtkSpinButton where the user indicated the number of each card to add.
        @comboboxtext_condition -> the GtkComboBox where the user indicated the condition of each card to add.
        @radiobutton_proxies -> None or a Gtk.RadioButton (for proxy mode).
        @select_list_decks -> None or a Gtk.TreeSelection (for proxy mode).
        @side_checkbutton -> None or a Gtk.CheckButton (for proxy mode).
        
        """
        
        def add_proxies(deck_name, proxies_list_to_change):
                GLib.idle_add(defs.MAINWINDOW.decks.change_nb_proxies, deck_name, proxies_list_to_change)
        
        functions.various.lock_db(True, None)
        
        button_add.set_sensitive(False)
        button_add.set_label(defs.STRINGS["add_button_wait"])
        nb = spinbutton.get_value_as_int()
        condition = ""
        for cond in defs.CONDITIONS.values():
                if cond[1] == comboboxtext_condition.get_active_text():
                        condition = cond[0]
                        break
        lang = entry_lang.get_text()
        foil = ""
        if checkbutton_foil.get_active():
                foil = "1"
        loaned = ""
        if checkbutton_loaned.get_active():
                loaned = entry_loaned.get_text()
        textbuffer = textview.get_buffer()
        start = textbuffer.get_start_iter()
        end = textbuffer.get_end_iter()
        comment = textbuffer.get_text(start, end, False)
        
        cards_to_add = []
        for card in cards_selected_list:
                cards_to_add.append([card[0], condition, lang, foil, loaned, comment, nb])
        #print(cards_to_add)
        spinner_labels = None
        if overlay_labels != None:
                spinner_labels = Gtk.Spinner()
                spinner_labels.show()
                overlay_labels.add_overlay(spinner_labels)
                spinner_labels.start()
        
        proxies_mode = 0
        if radiobutton_proxies != None:
                if radiobutton_proxies.get_active():
                        proxies_mode = 1
        
        if proxies_mode == 0:
                thread = threading.Thread(target = defs.MAINWINDOW.collection.add_collection, args = [cards_to_add, spinner_labels])
                thread.daemon = True
                thread.start()
        elif proxies_mode == 1:
                if side_checkbutton.get_active():
                        side = 1
                else:
                        side = 0
                proxies_list_to_change = []
                for card in cards_selected_list:
                        proxies_list_to_change.append([card[0], nb, side])
                model_deck, pathlist_deck = select_list_decks.get_selected_rows()
                deck_name = model_deck[pathlist_deck][1]
                thread = threading.Thread(target = add_proxies, args = (deck_name, proxies_list_to_change))
                thread.daemon = True
                thread.start()
        popover.hide()

def popover_add_close(popover, eventbox):
        eventbox.remove(eventbox.get_child())
        add_pic = Gtk.Image.new_from_file(os.path.join(defs.PATH_MC, "images", "add.png"))
        eventbox.add(add_pic)
        add_pic.show()
        defs.BUTTON_COLL_LOCK = None

def load_card_picture(path, pixbuf, card_pic, gg_pic, layout, radius, flip_pic):
        """Loads the picture from 'path' to 'card_pic'. We apply a radius and we modify the picture if needed by 'layout' or 'flip_pic'.
        
        @path -> the path to the file.
        @pixbuf -> a GdK.Pixbuf from the file. We used it to calculate the size to display the picture.
        @card_pic -> the Gtk.Image of the card.
        @gg_pic -> an int. 1 if the picture of the card has been downloaded. 0 if cardback.png is used.
        @layout -> a string, the layout of the card.
        @radius -> an int, the radius to apply to the picture of the card.
        @flip_pic -> a boolean, indicates if the picture need to be fliped.
        
        """
        
        size = functions.various.card_pic_size()
        pixbuf_width = pixbuf.get_width()
        pixbuf_height = pixbuf.get_height()
        if pixbuf_width > size or pixbuf_height > size:
                pixbuf = functions.various.gdkpixbuf_new_from_file_at_size(path, size, size)
        else:
                pixbuf = functions.various.gdkpixbuf_new_from_file(path)
        
        # we add rounded corners to the picture
        w = pixbuf.get_width()
        h = pixbuf.get_height()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        context = cairo.Context(surface)
        functions.various.draw_rounded(context, 0, 0, w, h, radius, radius)
        Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
        context.paint()
        
        pb_radius = Gdk.pixbuf_get_from_surface(surface, 0, 0, w, h)
        
        card_pic.set_from_pixbuf(pb_radius)
        
        card_pic.set_size_request(size, size)
        if gg_pic == 1 and layout == "split" and ("Who  What  When  Where  Why" not in path):
                functions.various.rotate_card_pic(card_pic)
        if gg_pic == 1 and layout == "flip" and flip_pic:
                vertical_flip_pic(None, card_pic)

def waiting_for_downloader(card_pic, layout, edition_code, name, spinner, internet, radius, flip_pic, add_pic):
        """This function is called when the thread which downloads the picture has finish. It checks if the card has been downloaded, and loads it. If not, cardback.png is used. In all cases, it adds the "Add button" above the picture.
        
        @card_pic -> the Gtk.Image of the card.
        @layout -> a string, the layout of the card.
        @edition_code -> the edition of the card.
        @name -> the name of the card.
        @spinner -> a Gtk.Spinner
        @internet -> a boolean. True: internet is ok, False it's not.
        @radius -> an int, the radius to apply to the picture of the card.
        @flip_pic -> a boolean, indicates if the picture need to be fliped.
        @add_pic -> the Gtk.Image of the "Add button".
        
        """
        gg_pic = 0
        if functions.various.check_card_pic(edition_code, name):
                path = os.path.join(defs.CACHEMCPIC, functions.various.valid_filename_os(edition_code), functions.various.valid_filename_os(name) + ".full.jpg")
                gg_pic = 1
        else:
                path = os.path.join(defs.CACHEMCPIC, "cardback.png")
        
        # we search the perfect size for this pixbuf
        try:
                pixbuf = functions.various.gdkpixbuf_new_from_file(path)
        except GLib.GError:
                os.remove(path)
        else:
                load_card_picture(path, pixbuf, card_pic, gg_pic, layout, radius, flip_pic)
        spinner.stop()
        spinner.destroy()
        add_pic.set_from_file(os.path.join(defs.PATH_MC, "images", "add.png"))
        if internet == 0:
                functions.various.message_dialog(defs.STRINGS["download_card_no_internet"], 1)

def dd_card_pic(object_origin, edition_code, name, multiverseid, imageurl, layout, card_pic, spinner, radius, flip_pic, add_pic):
        # we can try to download the picture
        internet = 1
        if functions.various.check_internet():
                nb_total_try = 3
                nb_try = 0
                
                while nb_try < nb_total_try:
                        result = functions.various.downloadPicture(multiverseid, imageurl, name, edition_code)
                        if result:
                                nb_try = 4
                        else:
                                nb_try += 1
        else:
                internet = 0
                
        GLib.idle_add(waiting_for_downloader, card_pic, layout, edition_code, name, spinner, internet, radius, flip_pic, add_pic)

def vertical_flip_pic(button, card_pic):
        """We flip the picture of the card.        
        """
        functions.various.vertical_flip_pic(card_pic)

def gen_more_popover(more_button, multiverseid, basename, nb_variante, edition_code, name, foreign__name, object_origin, current_id, type_, basetext, power, toughness, basecolors):
        """Generates the "More information" popover (or None). We get the other editions of the card, the link to the Gatherer and the price.
        
        @rotate_card_pic -> the "More information" Gtk.Button.
        @multiverseid, @basename, @nb_variante, @edition_code, @name, @foreign__name -> the characteristics of the card
        @object_origin -> an AdvancedSearch, Collection or Decks object (indicates the origin of the card viewer request)
        @current_id -> a string, the id of the card.
        @type_, @basetext, @power, @toughness, @basecolors -> the characteristics of the card (2).
        
        """
        
        def getKey(item):
                return(item[0])
        
        link_gatherer = 0
        other_editions = 0
        price = 0
        
        popover = Gtk.Popover.new(more_button)
        popover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        if functions.config.read_config("ext_fr_name") == "1":
                name_name_edition = "name_french"
        else:
                name_name_edition = "name"
        
        conn, c = functions.db.connect_db()
        c.execute("""SELECT cards.id, cards.nb_variante, CASE WHEN editions.""" + name_name_edition + """ = '' THEN editions.name ELSE editions.name_french END AS edition FROM cards, editions WHERE cards.name = \"""" + basename.replace('"', '""') + """\" AND cards.id != \"""" + str(current_id) + """\" AND editions.code = cards.edition AND cards.type = \"""" + type_ + """\" AND cards.text = \"""" + basetext.replace('"', '""') + """\" AND cards.power = \"""" + power + """\" AND cards.toughness = \"""" + toughness + """\" AND cards.colors = \"""" + basecolors + """\" ORDER BY edition ASC""")
        reponses = c.fetchall()
        functions.db.disconnect_db(conn)
        
        if len(reponses) > 0:
                if len(reponses) == 1:
                        oth_ed_button = Gtk.MenuButton(defs.STRINGS["other_edition"] + " ▶")
                else:
                        oth_ed_button = Gtk.MenuButton(defs.STRINGS["other_editions"] + " (" + str(len(reponses)) + ") ▶")
                ed_menu = Gtk.Menu()
                oth_ed_button.set_relief(Gtk.ReliefStyle.NONE)
                oth_ed_button.set_direction(Gtk.ArrowType.RIGHT)
                tmp_list = []
                for card in reponses:
                        id_, variant, edition_long = card
                        if variant != "":
                                space = " "
                                variant = "(" + variant + ")"
                        else:
                                space = ""
                        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys() and foreign__name != "":
                                tmp_name = foreign__name + space + variant + " - " + edition_long
                        else:
                                tmp_name = name + space + variant + " - " + edition_long
                        tmp_list.append([tmp_name, id_])
                
                tmp_list = sorted(tmp_list, key=getKey)
                for elm in tmp_list:
                        tmp_name, id_ = elm
                        menu_item = Gtk.MenuItem(tmp_name)
                        menu_item.connect("activate", object_origin.load_card_from_outside, id_, [ed_menu, popover], 1)
                        menu_item.show()
                        ed_menu.append(menu_item)
                oth_ed_button.set_popup(ed_menu)
                popover_box.pack_start(oth_ed_button, True, True, 0)
                other_editions = len(reponses)
        
        if multiverseid != "":
                link_gatherer = 1
                url = "http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=" + multiverseid
                linkbutton_gatherer = Gtk.LinkButton(uri=url, label=defs.STRINGS["open_gatherer"])
                linkbutton_gatherer.props.has_tooltip = False
                linkbutton_gatherer.connect("activate-link", functions.various.open_link_in_browser, url, popover)
                popover_box.pack_start(linkbutton_gatherer, True, True, 0)
        
        # we try to get a price
        if functions.config.read_config("cards_price") == "1" and functions.prices.check_prices_presence():
                tmp_price = functions.prices.get_price([current_id])
                currency = tmp_price[1]
                try:
                        current_price = tmp_price[0][current_id]
                except:
                        current_price = ""
                if current_price != "":
                        price = 1
                        
                        tcgname_edition = functions.various.edition_tcgname(edition_code)
                        tmp_name = name.replace("// ", "").replace("/", " ").replace("®", "r")
                        if "<>" in tmp_name:
                                tmp_name = name.split(" <> ")[0]
                        if "Token" in type_:
                                tmp_name = name.split("(")[0] + "Token"
                        if nb_variante != "":
                                tmp_name = name + " (Version " + nb_variante + ")"
                        if tcgname_edition == "" or edition_code == "gat" or edition_code == "pre":
                                url = "http://store.tcgplayer.com/magic/product/show?ProductName=" + functions.various.remove_accented_char(tmp_name.replace(" // ", " ").replace("/", " ").replace(":", "").lower()) + "&newSearch=false"
                        else:
                                url = "http://store.tcgplayer.com/magic/" + tcgname_edition + "/" + functions.various.remove_accented_char(tmp_name.replace(" // ", " ").replace("/", " ").replace(":", "").lower().replace(" ", "-"))
                        
                        
                        label_price = defs.STRINGS["open_display_price"].replace(";;;", str(current_price)).replace("%%%", currency)
                        linkbutton_price = Gtk.LinkButton(uri=url, label=label_price)
                        linkbutton_price.props.has_tooltip = False
                        linkbutton_price.connect("activate-link", functions.various.open_link_in_browser, url, popover)
                        popover_box.pack_start(linkbutton_price, True, True, 0)
        
        if link_gatherer == 0 and other_editions == 0 and price == 0:
                return(None)
        else:
                popover_box.show_all()
                popover.add(popover_box)
                return(popover)

def gen_manacost_popover(cmc_button, manacost):
        """Generates the popover for the Manacost button.
        
        @cmc_button -> the Gtk.Button
        @manacost -> a string.
        
        """
        manacost_all = manacost.split("|")
        manacosts_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        for manacost_list in manacost_all:
                manacost_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
                manacost_list = re.findall("\{(.*?)\}", manacost_list)
                for elm in manacost_list:
                        elm = elm.lower().replace("/", "")
                        if elm.isnumeric() == False:
                                elm = "".join(sorted(elm))
                        mana_pic = Gtk.Image()
                        if elm == "1000000":
                                pixbuf = functions.various.gdkpixbuf_new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "symbols", elm + ".png"), 100, 100)
                        else:
                                pixbuf = functions.various.gdkpixbuf_new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "symbols", elm + ".png"), 20, 20)
                        mana_pic.set_from_pixbuf(pixbuf)
                        manacost_box.pack_start(mana_pic, True, True, 0)
                manacosts_box.pack_start(manacost_box, True, True, 0)
        manacosts_box.show_all()
        popover = Gtk.Popover.new(cmc_button)
        popover.add(manacosts_box)
        return(popover)
