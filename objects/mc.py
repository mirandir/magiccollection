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

# Main Items classes for Magic Collection

from gi.repository import Gtk, Gio, GdkPixbuf, GLib, Gdk
import sys
import os
import threading

# imports def.py
import defs
# imports objects
import objects.Collection
import objects.Decks
import objects.AdvancedSearch
# imports functions
import functions.db
import functions.various
import functions.config
import functions.importexport

class MagicCollection(Gtk.Application):
        '''Creation of the application.'''
        def __init__(self):
                Gtk.Application.__init__(self, application_id="org.mirandir.MagicCollection")
                self.window = None
                self.aboutwindow = None
                self.shortcutswindow = None
                self.tips = None
                GLib.set_application_name(defs.STRINGS["app_name"])
                GLib.set_prgname("magic_collection")
                if functions.config.read_config("dark_theme") == "1":
                        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", True)
                # we disable the floating scrollbars with Windows
                if defs.OS == "windows":
                        os.environ["GTK_OVERLAY_SCROLLING"] = "0"

        def do_activate(self):
                if self.window == None:
                        self.window = MC_Window(self)
                        self.window.show_all()
                        
                        # we hide the MenuBar (yes, it's bad)
                        for widget in self.window.get_children():
                                if widget.__class__.__name__ == "MenuBar":
                                        widget.hide()
                        
                        # checking and loading database
                        thread = threading.Thread(target = functions.db.check_db)
                        thread.daemon = True
                        thread.start()
                self.window.present()
                
        def load_mc(self):
                if defs.DB_VERSION != None:
                        functions.various.gen_dict_editions()
                        # checks for old format
                        if functions.importexport.test_oldformat():
                                functions.importexport.import_oldformat()
                        # do we need to autoupdate the prices?
                        if functions.config.read_config("price_autodownload") == "1":
                                functions.prices.check_prices("auto")
                        functions.db.gen_sdf_data()
                        self.window.create_gui()
                else:
                        self.window.widget_overlay.destroy()
                        functions.various.message_dialog(defs.STRINGS["problem_db"], 0)

        def do_startup(self):
                # start the application
                Gtk.Application.do_startup(self)
                
                # create a Gmenu
                menu = Gio.Menu()
                
                # preferences
                section_pref = Gio.Menu()
                section_pref.append(defs.STRINGS["preferences"], "app.preferences")
                menu.append_section(None, section_pref)
                
                # the import/export submenu
                section_importexport = Gio.Menu()
                submenu_eximp = Gio.Menu()
                section_importexport.append_submenu(defs.STRINGS["importexport"], submenu_eximp)
                submenu_eximp.append(defs.STRINGS["import"], "app.importdata")
                submenu_eximp.append(defs.STRINGS["export"], "app.exportdata")
                menu.append_section(None, section_importexport)
                
                section_oth = Gio.Menu()
                # others menu entries
                if defs.GTK_MINOR_VERSION >= 20:
                        section_oth.append(defs.STRINGS["shortcuts"], "app.shortcuts")
                section_oth.append(defs.STRINGS["tips"], "app.tips")
                section_oth.append(defs.STRINGS["about"], "app.about")
                section_oth.append(defs.STRINGS["quit"], "app.quit")
                menu.append_section(None, section_oth)
                
                # set the menu as menu of the application
                self.set_app_menu(menu)
                
                # option "preferences"
                preferences_action = Gio.SimpleAction.new("preferences", None)
                preferences_action.connect("activate", self.preferences)
                self.add_action(preferences_action)
                # option "importdata"
                importdata_action = Gio.SimpleAction.new("importdata", None)
                importdata_action.connect("activate", self.importdata)
                self.add_action(importdata_action)
                # option "exportdata"
                exportdata_action = Gio.SimpleAction.new("exportdata", None)
                exportdata_action.connect("activate", self.exportdata)
                self.add_action(exportdata_action)
                # option "tips"
                tips_action = Gio.SimpleAction.new("tips", None)
                tips_action.connect("activate", self.tips_cb)
                self.add_action(tips_action)
                # option "shortcuts"
                if defs.GTK_MINOR_VERSION >= 20:
                        shortcuts_action = Gio.SimpleAction.new("shortcuts", None)
                        shortcuts_action.connect("activate", self.shortcuts_cb)
                        self.add_action(shortcuts_action)
                # option "about"
                about_action = Gio.SimpleAction.new("about", None)
                about_action.connect("activate", self.about_cb, self)
                self.add_action(about_action)
                # option "quit"
                quit_action = Gio.SimpleAction.new("quit", None)
                quit_action.connect("activate", self.quit_cb)
                self.add_action(quit_action)
                
        def preferences(self, action, param):
                functions.config.show_pref_dialog()
        
        def importdata(self, action, param):
                GLib.idle_add(functions.importexport.import_data)
        
        def exportdata(self, action, param):
                GLib.idle_add(functions.importexport.export_data)
        
        def tips_cb(self, action, param):
                GLib.idle_add(functions.various.show_tips_window, self)
        
        def shortcuts_cb(self, action, param):
                GLib.idle_add(functions.various.show_shortcuts_window, self)
        
        def about_cb(self, action, parameters, app):
                if self.aboutwindow == None:
                        aboutdialog = Gtk.AboutDialog("")
                        aboutdialog.set_transient_for(app.window)
                        aboutdialog.set_title(defs.STRINGS["about"] + " - " + defs.STRINGS["app_name"])
                        aboutdialog.set_program_name(defs.STRINGS["app_name"])
                        aboutdialog.set_icon_name("magic_collection")
                        if defs.DB_VERSION != None:
                                aboutdialog.set_version(defs.VERSION + " - " + defs.STRINGS["aboutdialog_db"] + " " + defs.DB_VERSION)
                        else:
                                aboutdialog.set_version(defs.VERSION)
                        aboutdialog.set_website(defs.SITEMC + "magiccollection/")
                        aboutdialog.set_website_label(defs.STRINGS["website"])
                        aboutdialog.set_logo(functions.various.gdkpixbuf_new_from_file(os.path.join(defs.PATH_MC, "images", "icons", "mclogo_min.png")))
                        aboutdialog.set_copyright(defs.STRINGS["about_copyright"])
                        aboutdialog.set_comments(defs.STRINGS["about_comment"])
                        aboutdialog.set_authors(["mirandir [mirandir@orange.fr]"])
                        aboutdialog.set_license(defs.STRINGS["about_licence"])
                        aboutdialog.set_wrap_license(True)
                        aboutdialog.add_credit_section(defs.STRINGS["about_contributors"], defs.STRINGS["about_contributors_list"].split("&&&"))
                        
                        self.aboutwindow = aboutdialog
                        aboutdialog.run()
                        aboutdialog.destroy()
                        self.aboutwindow = None
                else:
                        self.aboutwindow.present()

        def quit_cb(self, action, parameter):
                if defs.COLL_LOCK:
                        # don't quit
                        functions.various.message_dialog(defs.STRINGS["coll_busy"], 0)
                else:
                        # quit
                        # we remember the size of the window
                        width, height = self.window.get_size()
                        functions.config.change_config("last_width", str(width))
                        functions.config.change_config("last_height", str(height))
                        self.quit()

class MC_Window(Gtk.ApplicationWindow):
        '''Creation of the mainwindow.'''
        def __init__(self, app):
                Gtk.Window.__init__(self, title=defs.STRINGS["app_name"], application=app)
                self.set_wmclass(defs.STRINGS["app_name"], defs.STRINGS["app_name"])
                self.set_icon_name("magic_collection")
                if defs.OS == "windows":
                        self.set_icon_from_file(os.path.join(defs.PATH_MC, "images", "icons", "mclogo_min.png"))
                self.app = app
                defs.MAINWINDOW = self
                self.accelgroup = Gtk.AccelGroup()
                self.add_accel_group(self.accelgroup)
                self.connect("delete-event", self.delete_main_window)
                self.connect("key-press-event", self.change_mode)
                
                #print(self.get_preferred_size())
                last_width = int(functions.config.read_config("last_width"))
                last_height = int(functions.config.read_config("last_height"))
                if last_width > 99 and last_height > 99:
                        self.set_default_size(last_width, last_height)
                else:
                        if defs.DISPLAY_WIDTH > 1279:
                                if defs.OS == "gnome":
                                        self.set_default_size(1170, 570)
                                else:
                                        self.set_default_size(1000, 500)
                        else:
                                if defs.OS == "gnome":
                                        self.set_default_size(1020, 500)
                                else:
                                        self.set_default_size(920, 500)
                
                self.main_stack = Gtk.Stack()
                
                # headerbar creation
                self.headerbar = Gtk.HeaderBar()
                self.headerbar.props.show_close_button = True
                self.headerbar.props.title = defs.STRINGS["app_name"]
                
                search_button = Gtk.ToggleButton()
                search_button.set_tooltip_text(defs.STRINGS["search_card_tooltip"])
                search_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="edit-find-symbolic"), Gtk.IconSize.BUTTON)
                search_button.add(search_pic)
                
                search_revealer = Gtk.Revealer()
                search_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
                search_revealer.set_transition_duration(150)
                
                search_entry = Gtk.Entry()
                icon_go = Gio.ThemedIcon(name="go-jump-symbolic")
                search_entry.set_icon_from_gicon(Gtk.EntryIconPosition.PRIMARY, icon_go)
                search_entry.set_icon_sensitive(Gtk.EntryIconPosition.PRIMARY, False)
                search_entry.connect("activate", self.search_launched, self.main_stack)
                search_entry.connect("icon-release", self.search_icon_release, self.main_stack)
                search_entry.connect("changed", self.update_icons_search_entry)
                search_entry.connect("button-press-event", self.focus_press_search_entry)
                search_entry.connect("button-release-event", self.focus_release_search_entry)
                search_entry.set_size_request(210, -1)
                search_revealer.add(search_entry)
                
                search_button.connect("clicked", self.search_button_toggled, search_entry, search_revealer)
                search_button.add_accelerator("clicked", self.accelgroup, Gdk.keyval_from_name("f"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
                self.headerbar.pack_start(search_button)
                
                self.headerbar.pack_start(search_revealer)
                
                self.overlay = Gtk.Overlay()
                
                button = Gtk.Button("")
                button.get_child().set_markup("<b><big>" + defs.STRINGS["loading"] + "</big></b>")
                button.set_valign(Gtk.Align.CENTER)
                button.set_halign(Gtk.Align.CENTER)
                button.set_can_focus(False)
                button.show()
                
                self.widget_overlay = button
                
                if defs.OS != "gnome":
                        non_gnome_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                        self.overlay.add(non_gnome_box)
                        non_gnome_box.pack_start(self.headerbar, False, False, 0)
                        non_gnome_box.pack_start(self.main_stack, True, True, 0)
                        self.headerbar.set_decoration_layout("menu:")
                        # we load a specific CSS
                        style_provider = Gtk.CssProvider()
                        if defs.OS == "windows":
                                css = """
                                * {
                                        font-family: 'Segoe UI';
                                        font-size: 9.5px;
                                }
                                GtkHeaderBar {
                                        border-radius: 0;
                                }
                                """
                        elif defs.OS == "mac":
                                css = """
                                * {
                                        font-family: 'San Francisco';
                                        font-size: 13px;
                                }
                                GtkHeaderBar {
                                        border-radius: 0;
                                }
                                """
                        else:
                                css = """
                                GtkHeaderBar {
                                        border-radius: 0;
                                }
                                """
                        if defs.GTK_MINOR_VERSION >= 20:
                                css = css.replace("GtkHeaderBar", "headerbar")
                        style_provider.load_from_data(bytes(css.encode()))
                        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                else:
                        self.overlay.add(self.main_stack)
                        self.set_titlebar(self.headerbar)
                
                self.add(self.overlay)
                self.overlay.add_overlay(button)
                self.main_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        
        def change_mode(self, window, event):
                keyname = Gdk.keyval_name(event.keyval)
                if event.state & Gdk.ModifierType.MOD1_MASK and keyname == "c" :
                        if self.main_stack.get_visible_child_name() != "collection":
                                self.main_stack.set_visible_child_name("collection")
                if event.state & Gdk.ModifierType.MOD1_MASK and keyname == "d" :
                        if self.main_stack.get_visible_child_name() != "decks":
                                self.main_stack.set_visible_child_name("decks")
                if event.state & Gdk.ModifierType.MOD1_MASK and keyname == "s" :
                        if self.main_stack.get_visible_child_name() != "advancedsearch":
                                self.main_stack.set_visible_child_name("advancedsearch")
        
        def delete_main_window(self, *args):
                if defs.COLL_LOCK:
                        # don't close
                        functions.various.message_dialog(defs.STRINGS["coll_busy"], 0)
                        return(True)
                else:
                        # we remember the size of the window
                        width, height = self.get_size()
                        functions.config.change_config("last_width", str(width))
                        functions.config.change_config("last_height", str(height))
                        # close
                        return(False)
        
        def focus_press_search_entry(self, entry, eventbutton):
                if entry.has_focus():
                        defs.SIMPLY_SEARCH_ENTRY_HAD_FOCUS = True
                else:
                        defs.SIMPLY_SEARCH_ENTRY_HAD_FOCUS = False
        
        def focus_release_search_entry(self, entry, eventbutton):
                if entry.get_text() != "" and defs.SIMPLY_SEARCH_ENTRY_HAD_FOCUS == False:
                        entry.select_region(0, -1)
        
        def update_icons_search_entry(self, entry):
                if entry.get_text() == "":
                        entry.set_icon_from_gicon(Gtk.EntryIconPosition.SECONDARY, None)
                        entry.set_icon_sensitive(Gtk.EntryIconPosition.PRIMARY, False)
                else:
                        icon_clear = Gio.ThemedIcon(name="edit-clear-symbolic")
                        if entry.get_icon_gicon(Gtk.EntryIconPosition.SECONDARY) == None:
                                entry.set_icon_from_gicon(Gtk.EntryIconPosition.SECONDARY, icon_clear)
                        entry.set_icon_sensitive(Gtk.EntryIconPosition.PRIMARY, True)
        
        def search_icon_release(self, search_entry, icon, event, main_stack):
                if icon.value_name == "GTK_ENTRY_ICON_SECONDARY":
                        search_entry.set_text("")
                        search_entry.grab_focus()
                elif icon.value_name == "GTK_ENTRY_ICON_PRIMARY":
                        search_entry.emit("activate")
        
        def search_launched(self, search_entry, main_stack):
                search_text = functions.various.py_lara(search_entry.get_text())
                if search_text != "":
                        current_view = main_stack.get_visible_child_name()
                        if current_view == "collection":
                                current_object_view = self.collection
                        elif current_view == "advancedsearch":
                                current_object_view = self.advancedsearch
                        elif current_view == "decks":
                                current_object_view = self.decks
                        if (search_text == "forest" or search_text == defs.STRINGS["forest"] or search_text == "island" or search_text == defs.STRINGS["island"] or search_text == "mountain" or search_text == defs.STRINGS["mountain"] or search_text == "swamp" or search_text == defs.STRINGS["swamp"] or search_text == "plains" or search_text == defs.STRINGS["plains"]) and functions.config.read_config("no_reprints") == "0":
                                search_entry.set_text("")
                                self.advancedsearch.comboboxtext1.set_active(0)
                                self.advancedsearch.entry1.set_text(search_text)
                                main_stack.set_visible_child_name("advancedsearch")
                                self.advancedsearch.entry1.emit("activate")
                        else:
                                request = functions.db.prepare_request([[search_entry, defs.STRINGS["name_ad"]]], "db")[0]
                                if request != None:
                                        spinner = Gtk.Spinner()
                                        spinner.show()
                                        self.headerbar.pack_start(spinner)
                                        spinner.start()
                                        search_entry.set_sensitive(False)
                                        try:
                                                prev_search = defs.MEM_SEARCHS[request]
                                        except KeyError:
                                                thread = threading.Thread(target = self.search_by_name, args = (request, spinner, search_entry, current_object_view))
                                                thread.daemon = True
                                                thread.start()
                                        else:
                                                self.show_result(prev_search, spinner, search_entry, current_object_view)
        
        def search_by_name(self, request, spinner, search_entry, current_object_view):
                conn, c = functions.db.connect_db()
                c.execute(request)
                reponses = c.fetchall()
                functions.db.disconnect_db(conn)
                defs.MEM_SEARCHS[request] = reponses
                GLib.idle_add(self.show_result, reponses, spinner, search_entry, current_object_view)
        
        def show_result(self, reponses, spinner, search_entry, current_object_view):
                spinner.destroy()
                if len(reponses) == 0:
                        functions.various.message_dialog(defs.STRINGS["no_result"], 0)
                elif len(reponses) == 1:
                        id_ = reponses[0][0]
                        current_object_view.load_card(id_, 1)
                else:
                        result_window, nb_result_disp, store_results = functions.various.create_window_search_name(reponses, current_object_view)
                        if nb_result_disp == 1:
                                id_ = store_results[0][0]
                                current_object_view.load_card(id_, 1)
                        else:
                                result_window.run()
                                result_window.destroy()
                search_entry.set_sensitive(True)
        
        def search_button_toggled(self, togglebutton, search_entry, search_revealer):
                if togglebutton.get_active():
                        search_revealer.set_reveal_child(True)
                        search_entry.grab_focus()
                else:
                        search_revealer.set_reveal_child(False)
        
        def create_gui(self):
                '''Creation of the GUI.'''
                self.main_stackswitcher = Gtk.StackSwitcher()
                
                self.collection = objects.Collection.Collection(self)
                self.decks = objects.Decks.Decks(self)
                self.advancedsearch = objects.AdvancedSearch.AdvancedSearch(self)
                
                self.main_stackswitcher.set_stack(self.main_stack)
                
                self.headerbar.set_custom_title(self.main_stackswitcher)
                
                self.main_stackswitcher.show_all()
                self.main_stack.show_all()
                self.widget_overlay.destroy()
