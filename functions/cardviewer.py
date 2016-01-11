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

def gen_card_viewer(cardid, box_card_viewer, object_origin, simple_search):
        """Generates and returns a card viewer with card's data.
        
        @cardid -> a string (an card's id in the database) or None
        @box_card_viewer -> a Gtk.Box (the parent widget of the card viewer)
        @object_origin -> an AdvancedSearch, Collection or Decks object (indicates the origin of the card viewer request)
        @simple_search -> an int (indicates if the card viewer is used with a simple search or another type of search)
        
        """
        
        for widget in box_card_viewer.get_children():
                box_card_viewer.remove(widget)
        
        if cardid == None:
                # if cardid is None, we show a random mana picture
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
                
                # we check if we must retrieve foreign names for flip / split cards
                # FIXME : chinese variants !
                foreign_name = defs.LOC_NAME_FOREIGN[functions.config.read_config("fr_language")]
                
                # we get the card data
                conn, c = functions.db.connect_db()
                c.execute("""SELECT * FROM cards WHERE id = \"""" + cardid + """\"""")
                reponse = c.fetchall()                
                
                split_flip_df_data = []
                
                if len(reponse) > 1:
                        print("Something is wrong in the database. IDs should be unique.")
                else:
                        id_, name, nb_variante, names, edition_code, name_chinesetrad, name_chinesesimp, name_french, name_german, name_italian, name_japanese, name_korean, name_portuguesebrazil, name_portuguese, name_russian, name_spanish, colors, manacost, cmc, multiverseid, imageurl, type_, artist, text, flavor, power, toughness, loyalty, rarity, layout, number, variations = reponse[0]
                        
                        basename = str(name)
                        
                        # we choose the foreign name to display
                        if foreign_name == "name_chinesetrad":
                                foreign__name = name_chinesetrad
                        elif foreign_name == "name_chinesesimp":
                                foreign__name = name_chinesesimp
                        elif foreign_name == "name_french":
                                foreign__name = name_french
                        elif foreign_name == "name_german":
                                foreign__name = name_german
                        elif foreign_name == "name_italian":
                                foreign__name = name_italian
                        elif foreign_name == "name_japanese":
                                foreign__name = name_japanese
                        elif foreign_name == "name_korean":
                                foreign__name = name_korean
                        elif foreign_name == "name_portuguesebrazil":
                                foreign__name = name_portuguesebrazil
                        elif foreign_name == "name_portuguese":
                                foreign__name = name_portuguese
                        elif foreign_name == "name_russian":
                                foreign__name = name_russian
                        elif foreign_name == "name_spanish":
                                foreign__name = name_spanish
                        else:
                                foreign__name = name_german # why not ?
                        
                        if foreign__name == "":
                                foreign__name = name
                        basenameforeign = str(foreign__name)
                        basetext = str(text)
                        basecolors = str(colors)
                        
                        # Flip, split and double-faced cards have more than 1 line in the database
                        if layout == "flip" or layout == "split" or layout == "double-faced":
                                # we need more data to find the complete text & foreign name
                                request = """SELECT * FROM cards WHERE layout = 'flip' OR layout = 'split' OR layout = 'double-faced'"""
                                c.execute(request)
                                split_flip_df_data = c.fetchall()
                                
                                names_tmp = names.split("|")
                                
                                if layout == "split":
                                        final_text = ""
                                        final_manacost = ""
                                        list_cmc = []
                                        final_colors = ""
                                        final_artist = ""
                                        # we try to get the complete manacost, text and the higher cmc
                                        for nn in names_tmp:
                                                for card_split_flip in split_flip_df_data:
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
                                                for card_split_flip in split_flip_df_data:
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
                                        # we try to get the complete name for english and foreign name
                                        final_name = ""
                                        if layout == "split":
                                                for nn in names_tmp:
                                                        final_name = final_name + separator + nn
                                                name = final_name[4:]
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
                                                                for card_split_flip in split_flip_df_data:
                                                                        if card_split_flip[4] == edition_code:
                                                                                if nn == card_split_flip[1]:
                                                                                        final_nameforeign = final_nameforeign + separator + card_split_flip[7]
                                                        foreign__name = final_nameforeign[4:]
                                                elif layout == "flip":
                                                        final_nameforeign = foreign__name
                                                        for nn in names_tmp:
                                                                for card_split_flip in split_flip_df_data:
                                                                        if card_split_flip[4] == edition_code:
                                                                                if nn == card_split_flip[1]:
                                                                                        if card_split_flip[7] != foreign__name:
                                                                                                final_nameforeign = final_nameforeign + separator + card_split_flip[7]
                                                        foreign__name = final_nameforeign
                        # we disconnect the database
                        functions.db.disconnect_db(conn)
                        
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
                        
                        # the card picture
                        card_pic = Gtk.Image()
                        
                        # the top left button - can be a double-faced button, or a flip button, or an empty one
                        df_button = Gtk.Button()
                        df_button.set_relief(Gtk.ReliefStyle.NONE)
                        df_pic = Gtk.Image()
                        if layout == "double-faced":
                                # we get the id of the other face
                                for tmp_name in names.split("|"):
                                        if tmp_name != basename:
                                                othername = tmp_name
                                                break
                                for tmp_card in split_flip_df_data:
                                        if tmp_card[1] == othername and tmp_card[4] == edition_code:
                                                id_otherface = tmp_card[0]
                                                break
                                
                                if basename == names.split("|")[0]:
                                        df_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="weather-clear-night-symbolic"), Gtk.IconSize.LARGE_TOOLBAR)
                                else:
                                        df_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="weather-clear-symbolic"), Gtk.IconSize.LARGE_TOOLBAR)
                                df_button.connect("clicked", object_origin.load_card_from_outside, str(id_otherface), [], simple_search)
                        elif layout == "flip" or basename == "Curse of the Fire Penguin":
                                df_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="object-flip-vertical-symbolic"), Gtk.IconSize.SMALL_TOOLBAR)
                                df_button.connect("clicked", vertical_flip_pic, card_pic)
                        else:
                                df_pic.set_from_file(os.path.join(defs.PATH_MC, "images", "nothing.png"))
                                df_button.set_sensitive(False)
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
                        if manacost == "":
                                cmc_button = Gtk.MenuButton()
                                empty_pic = Gtk.Image()
                                empty_pic.set_from_file(os.path.join(defs.PATH_MC, "images", "nothing.png"))
                                cmc_button.add(empty_pic)
                                cmc_button.set_sensitive(False)
                        else:
                                cmc_button = Gtk.MenuButton("")
                                if cmc == "1000000":
                                        cmc_button.get_child().set_markup("<small>...</small>") # workaround for 'Gleemax'
                                elif len(cmc) > 1:
                                        cmc_button.get_child().set_markup("<small>" + cmc + "</small>")
                                else:
                                        cmc_button.set_label(cmc)
                                if manacost != "":
                                        manacost_popover = gen_manacost_popover(cmc_button, manacost)
                                        cmc_button.set_popover(manacost_popover)
                                        cmc_button.set_sensitive(True)
                        cmc_button.set_relief(Gtk.ReliefStyle.NONE)
                        grid.attach_next_to(cmc_button, label_name_1, Gtk.PositionType.RIGHT, 1, 1)
                        nb_columns += 1
                        
                        # we show the label_name_2
                        if label_name_1 != label_name_2:
                                grid.attach_next_to(label_name_2, first_widget, Gtk.PositionType.BOTTOM, nb_columns, 1)
                        
                        # the edition
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
                        
                        if defs.LANGUAGE in defs.LOC_NAME_FOREIGN.keys():
                                name_for_add_popover = foreign__name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        else:
                                name_for_add_popover = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        
                        eventbox_card_pic.connect("enter-notify-event", mouse_on_pic, overlay_card_pic, card_pic, object_origin, simple_search, name_for_add_popover, edition_longname, id_, split_flip_df_data)
                        
                        eventbox_card_pic.add(card_pic)
                        overlay_card_pic.add(eventbox_card_pic)
                        
                        path = os.path.join(defs.CACHEMCPIC, "cardback.png")

                        # we try to load the image of the card. If we get a GLib error, then the picture is corrupted, and we delete it
                        try:
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
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
                                
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, pix_size, pix_size)
                                card_pic.set_from_pixbuf(pixbuf)
                                card_pic.set_size_request(size, size)
                        
                        grid.attach_next_to(overlay_card_pic, label_edition, Gtk.PositionType.BOTTOM, nb_columns, 1)
                        
                        # the colors picture
                        colors_pic = Gtk.Image()
                        if colors != "":
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "color_indicators", colors.lower() + ".png"), 22, 22)
                        else:
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "nothing.png"), 22, 22)
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
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(os.path.join(defs.CACHEMCPIC, "icons", functions.various.valid_filename_os(edition_code) + ".png")), 22, 22)
                        else:
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "nothing.png"), 22, 22)
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
                                        if text == "" or flavor == "":
                                                textbuffer.set_text(text + flavor)
                                        else:
                                                textbuffer.set_text(text + "\n\n" + flavor)
                                        # we replace {?} by pictures (see PIC_IN_TEXT in defs.py)
                                        nb_to_replace = 0
                                        for char in text:
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
                                                                        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "symbols", file_name), size, size)
                                                                        textbuffer.insert_pixbuf(match_start, pixbuf)
                                                                        # we delete this text
                                                                        start_iter = textbuffer.get_start_iter()
                                                                        found = start_iter.forward_search(text_to_search, 0, None)
                                                                        if found:
                                                                                match_start, match_end = found
                                                                                textbuffer.delete(match_start, match_end)
                                                                        
                                        # flavor in italic
                                        start_iter = textbuffer.get_start_iter()
                                        found = start_iter.forward_search(flavor, 0, None)
                                        if found:
                                                match_start, match_end = found
                                                textbuffer.apply_tag(texttagItalic, match_start, match_end)
                                                        
                                        widget.add(textview)
                        else:
                                widget = Gtk.Image()
                                widget.set_from_gicon(Gio.ThemedIcon.new_with_default_fallbacks(manacol + "-symbolic"), Gtk.icon_size_from_name("100_mana_symbol"))
                                widget.set_vexpand(True)
                        grid.attach_next_to(widget, colors_pic, Gtk.PositionType.BOTTOM, nb_columns, 1)
                        
                        # buttonmenu "more" - other editions, open Gatherer, price
                        # FIXME : add the prices !
                        more_button = Gtk.MenuButton()
                        more_button.set_relief(Gtk.ReliefStyle.NONE)
                        more_popover = gen_more_popover(more_button, multiverseid, basename, nb_variante, edition_code, name_without_variants, foreign__name_without_variants, object_origin, id_, type_, basetext, power, toughness, basecolors)
                        if more_popover == None:
                                more_pic = Gtk.Image.new_from_file(os.path.join(defs.PATH_MC, "images", "nothing.png"))
                                more_button.set_sensitive(False)
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
                                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
                                        pic_ok = 1
                                except GLib.GError:
                                        os.remove(path)
                        
                        # we apply rounded corners to the picture
                        radius = 13
                        if imageurl != "":
                                radius = 7
                        
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
                                        thread = threading.Thread(target = dd_card_pic, args = (object_origin, edition_code, name, multiverseid, imageurl, layout, card_pic, spinner, radius, flip_pic))
                                        thread.daemon = True
                                        thread.start()
                        else:
                                load_card_picture(path, pixbuf, card_pic, 1, layout, radius, flip_pic)

        else:
                print("Something is wrong. We shouldn't get an empty cardid.")

def add_button_clicked(eventbox, signal, eventbox_pic_card, overlay, object_origin, simple_search, name_for_add_popover_ss, edition_longname_ss, id_ss, split_flip_df_data):
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
        @split_flip_df_data -> a list which contains informations about the flip / split / double-faced cards in the database. This list is empty if the displayed card are not flip / split / double-faced.
        
        """
        
        def getKey(item):
                """We use this to correctly sort some characters."""
                return(functions.various.remove_accented_char(item[1].lower().replace("œ", "oe").replace("æ", "ae")))
        
        cards_selected_list = []
        
        # we get the current selection - in the mainselect treeview
        selection = object_origin.mainselect
        try:
                count = selection.count_selected_rows()
        except AttributeError:
                count = 0
        if simple_search == 0 and count > 0:
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
                for fsdf_cards in split_flip_df_data:
                        if str(fsdf_cards[0]) == str(id__):
                                # we find it, so it's a flip - split - double-faced card
                                # if the name is different of the first names
                                first_names = fsdf_cards[3].split("|")[0]
                                if first_names != fsdf_cards[1]:
                                        # flip card, double-faced card : we need the correct name and the correct id
                                        # split card : we need the correct id
                                        for fsdf_cards2 in split_flip_df_data:
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
        
        if len(cards_selected_list) == 1:
                label_add = Gtk.Label()
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
        eventbox.destroy()
        popover.add(popover_box)
        
        grid_details, label_add_condition, comboboxtext_condition, label_add_lang, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, label_add_comment, scrolledwindow, textview = functions.various.gen_details_widgets()
        
        expander.add(grid_details)
        
        show_details = functions.config.read_config("add_collection_show_details")
        if show_details == "1":
                expander.set_expanded(True)
        
        if defs.COLL_LOCK:
                button_add = Gtk.Button(defs.STRINGS["add_button_wait"])
                button_add.set_sensitive(False)
        else:
                button_add = Gtk.Button(defs.STRINGS["add_button_validate"])
        button_add.connect("clicked", button_add_clicked, popover, spinbutton, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview, cards_selected_list, overlay_labels)
        defs.BUTTON_COLL_LOCK = button_add
        popover_box.pack_start(button_add, True, True, 0)
        
        add_pic = Gtk.Image.new_from_file(os.path.join(defs.PATH_MC, "images", "add_push.png"))
        overlay.add_overlay(add_pic)
        add_pic.show()
        
        popover.connect("closed", popover_add_close, add_pic)
        popover.set_position(Gtk.PositionType.RIGHT)
        popover.show_all()

def button_add_clicked(button_add, popover, spinbutton, comboboxtext_condition, entry_lang, checkbutton_foil, checkbutton_loaned, entry_loaned, textview, cards_selected_list, overlay_labels):
        """This is called when the user click on the add to the collection button. It add the selected cards to the collection.
        
        @button_add -> the 'add to the collection' GtkButton
        @popover -> the 'add to the collection' GtkPopover
        @spinbutton -> the GtkSpinButton where the user indicated the number of each card to add.
        @comboboxtext_condition -> the GtkComboBox where the user indicated the condition of each card to add.
        
        """
        
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
        thread = threading.Thread(target = defs.MAINWINDOW.collection.add_collection, args = [cards_to_add, spinner_labels])
        thread.daemon = True
        thread.start()

def popover_add_close(popover, add_pic):
        add_pic.destroy()
        defs.BUTTON_COLL_LOCK = None

def mouse_on_pic(eventbox_pic_card, event, overlay, card_pic, object_origin, simple_search, name_for_add_popover, edition_longname, id_, split_flip_df_data):
        add_pic = Gtk.Image.new_from_file(os.path.join(defs.PATH_MC, "images", "add.png"))
        eventbox = Gtk.EventBox()
        eventbox.connect("button-press-event", add_button_clicked, eventbox_pic_card, overlay, object_origin, simple_search, name_for_add_popover, edition_longname, id_, split_flip_df_data)
        eventbox.connect("leave-notify-event", mouse_no_more_on_pic, add_pic)
        overlay.add_overlay(eventbox)
        eventbox.add(add_pic)
        eventbox.show_all()

def mouse_no_more_on_pic(eventbox, event, add_pic):
        add_pic.destroy()
        eventbox.destroy()

def load_card_picture(path, pixbuf, card_pic, gg_pic, layout, radius, flip_pic):
        size = functions.various.card_pic_size()
        pixbuf_width = pixbuf.get_width()
        pixbuf_height = pixbuf.get_height()
        if pixbuf_width > size or pixbuf_height > size:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
        else:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        
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
                rotate_card_pic(None, None, card_pic)
        if gg_pic == 1 and layout == "flip" and flip_pic:
                vertical_flip_pic(None, card_pic)

def waiting_for_downloader(card_pic, layout, edition_code, name, spinner, internet, radius, flip_pic):
        gg_pic = 0
        if functions.various.check_card_pic(edition_code, name):
                path = os.path.join(defs.CACHEMCPIC, functions.various.valid_filename_os(edition_code), functions.various.valid_filename_os(name) + ".full.jpg")
                gg_pic = 1
        else:
                path = os.path.join(defs.CACHEMCPIC, "cardback.png")
        
        # we search the perfect size for this pixbuf
        try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        except GLib.GError:
                os.remove(path)
        else:
                load_card_picture(path, pixbuf, card_pic, gg_pic, layout, radius, flip_pic)
        spinner.stop()
        spinner.destroy()
        if internet == 0:
                functions.various.message_dialog(defs.STRINGS["download_card_no_internet"], 1)

def dd_card_pic(object_origin, edition_code, name, multiverseid, imageurl, layout, card_pic, spinner, radius, flip_pic):
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
                
        GLib.idle_add(waiting_for_downloader, card_pic, layout, edition_code, name, spinner, internet, radius, flip_pic)
                        
        #box_card_viewer.show_all()

def rotate_card_pic(eventbox, event, card_pic):
        functions.various.rotate_card_pic(card_pic)

def vertical_flip_pic(button, card_pic):
        functions.various.vertical_flip_pic(card_pic)

def gen_more_popover(more_button, multiverseid, basename, nb_variante, edition_code, name, foreign__name, object_origin, current_id, type_, basetext, power, toughness, basecolors):
        def getKey(item):
                return(item[0])
        
        link_gatherer = 0
        other_editions = 0
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
                                variant = "[" + variant + "]"
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
                linkbutton_gatherer.connect("activate-link", functions.various.open_link_in_browser, url, popover)
                popover_box.pack_start(linkbutton_gatherer, True, True, 0)
        
        if link_gatherer == 0 and other_editions == 0:
                return(None)
        else:
                popover_box.show_all()
                popover.add(popover_box)
                return(popover)

def gen_manacost_popover(cmc_button, manacost):
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
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "symbols", elm + ".png"), 100, 100)
                        else:
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(defs.PATH_MC, "images", "symbols", elm + ".png"), 20, 20)
                        mana_pic.set_from_pixbuf(pixbuf)
                        manacost_box.pack_start(mana_pic, True, True, 0)
                manacosts_box.pack_start(manacost_box, True, True, 0)
        manacosts_box.show_all()
        popover = Gtk.Popover.new(cmc_button)
        popover.add(manacosts_box)
        return(popover)
