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

class MC_Window(Gtk.ApplicationWindow):
        '''Mainwindow creation'''
        def __init__(self, app):
                Gtk.Window.__init__(self, title=defs.STRINGS["app_name"], application=app)
                self.set_wmclass(defs.STRINGS["app_name"], defs.STRINGS["app_name"])
                self.set_title(defs.STRINGS["app_name"])
                self.set_icon_from_file(os.path.join(defs.PATH_MC, "images", "mclogo.png"))
                self.app = app
                defs.MAINWINDOW = self
                self.accelgroup = Gtk.AccelGroup()
                self.add_accel_group(self.accelgroup)
                self.connect("delete-event", self.delete_main_window)
                
                if defs.DISPLAY_WIDTH > 1279:
                        self.resize(1200, 670)
                else:
                        self.resize(1020, 570)
                
                self.main_stack = Gtk.Stack()
                
                # headerbar creation
                self.headerbar = Gtk.HeaderBar()
                self.headerbar.props.show_close_button = True
                self.headerbar.props.title = defs.STRINGS["app_name"]
                #self.set_titlebar(self.headerbar)
                
                search_button = Gtk.ToggleButton()
                search_pic = Gtk.Image.new_from_gicon(Gio.ThemedIcon(name="edit-find-symbolic"), Gtk.IconSize.BUTTON)
                search_button.add(search_pic)
                
                search_entry = Gtk.Entry()
                icon_go = Gio.ThemedIcon(name="go-jump-symbolic")
                search_entry.set_icon_from_gicon(Gtk.EntryIconPosition.PRIMARY, icon_go)
                search_entry.set_icon_sensitive(Gtk.EntryIconPosition.PRIMARY, False)
                search_entry.connect("activate", self.search_launched, self.main_stack)
                search_entry.connect("icon-release", self.search_icon_release, self.main_stack)
                search_entry.connect("changed", self.update_icons_search_entry)
                search_entry.set_no_show_all(True)
                search_entry.set_size_request(210, -1)
                
                search_button.connect("clicked", self.search_button_toggled, search_entry)
                search_button.add_accelerator("clicked", self.accelgroup, Gdk.keyval_from_name("f"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
                self.headerbar.pack_start(search_button)
                
                #search_entry.set_placeholder_text(defs.STRINGS["search_card"])
                self.headerbar.pack_start(search_entry)
                
                
                self.overlay = Gtk.Overlay()
                
                button = Gtk.Button("")
                button.get_child().set_markup("<b><big>" + defs.STRINGS["loading"] + "</big></b>")
                button.set_valign(Gtk.Align.CENTER)
                button.set_halign(Gtk.Align.CENTER)
                button.set_can_focus(False)
                #defs.MAINWINDOW.widget_overlay = button
                #defs.MAINWINDOW.overlay.add_overlay(button)
                button.show()
                #functions.various.force_update_gui(0)
                
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
                                style_provider.load_from_path(os.path.join(defs.PATH_MC, "css", "windows_css.css"))
                        else:
                                style_provider.load_from_path(os.path.join(defs.PATH_MC, "css", "non_gnome_css.css"))
                        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                else:
                        self.overlay.add(self.main_stack)
                        self.set_titlebar(self.headerbar)
                
                self.add(self.overlay)
                self.overlay.add_overlay(button)
                self.main_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        
        def delete_main_window(self, *args):
                if defs.COLL_LOCK:
                        # don't close
                        functions.various.message_dialog(defs.STRINGS["coll_busy"], 0)
                        return(True)
                else:
                        # close
                        return(False)
        
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
                        if search_text == "forest" or search_text == defs.STRINGS["forest"] or search_text == "island" or search_text == defs.STRINGS["island"] or search_text == "mountain" or search_text == defs.STRINGS["mountain"] or search_text == "swamp" or search_text == defs.STRINGS["swamp"] or search_text == "plains" or search_text == defs.STRINGS["plains"]:
                                search_entry.set_text("")
                                self.advancedsearch.comboboxtext1.set_active(0)
                                self.advancedsearch.entry1.set_text(search_text)
                                main_stack.set_visible_child_name("advancedsearch")
                                self.advancedsearch.entry1.emit("activate")
                        else:
                                request = functions.db.prepare_request([[search_entry, defs.STRINGS["name_ad"]]], None)
                                if request != None:
                                        spinner = Gtk.Spinner()
                                        spinner.show()
                                        defs.MAINWINDOW.headerbar.pack_start(spinner)
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
                        result_window, nb_result_disp = functions.various.create_window_search_name(reponses, current_object_view)
                        if nb_result_disp == 1:
                                id_ = reponses[0][0]
                                current_object_view.load_card(id_, 1)
                        else:
                                result_window.run()
                                result_window.destroy()
                search_entry.set_sensitive(True)
        
        def search_button_toggled(self, togglebutton, search_entry):
                if togglebutton.get_active():
                        search_entry.show()
                        search_entry.grab_focus()
                else:
                        search_entry.hide()
        
        def create_gui(self):
                '''GUI creation'''
                #FIXME: read configuration for knowing what to do here                
                # main content
                self.main_stackswitcher = Gtk.StackSwitcher()
                
                self.collection = objects.Collection.Collection(self)
                self.decks = objects.Decks.Decks(self)
                self.advancedsearch = objects.AdvancedSearch.AdvancedSearch(self)
                
                self.main_stackswitcher.set_stack(self.main_stack)
                
                self.headerbar.set_custom_title(self.main_stackswitcher)
                
                self.main_stackswitcher.show_all()
                self.main_stack.show_all()
                # default view is collection
                #self.main_stack.set_visible_child_name("collection")

class MagicCollection(Gtk.Application):
        '''App creation'''
        def __init__(self):
                Gtk.Application.__init__(self)
                self.mainwindow = None
                GLib.set_application_name(defs.STRINGS["app_name"])
                if functions.config.read_config("dark_theme") == "1":
                        settings = Gtk.Settings.get_default()
                        settings.set_property("gtk-application-prefer-dark-theme", True)

        def do_activate(self):
                mainwindow = MC_Window(self)
                self.mainwindow = mainwindow
                mainwindow.show_all()
                
                # we hide the MenuBar (yes, it's bad)
                for widget in self.mainwindow.get_children():
                        if widget.__class__.__name__ == "MenuBar":
                                widget.hide()
                
                '''print(defs.OS)
                print(defs.STRINGS["language_name"])'''
                
                # checking and loading database
                thread = threading.Thread(target = functions.db.check_db)
                thread.daemon = True
                thread.start()
                
        def load_mc(self):
                self.mainwindow.widget_overlay.destroy()
                if defs.DB_VERSION != None:
                        functions.various.gen_dict_editions()
                        self.mainwindow.create_gui()

        def do_startup(self):
                # start the application
                Gtk.Application.do_startup(self)
                
                # create a Gmenu
                menu = Gio.Menu()
                
                # the Help submenu
                submenu_help = Gio.Menu()
                menu.append_submenu(defs.STRINGS["help"], submenu_help)
                # doc
                submenu_help.append(defs.STRINGS["doc"], "app.doc")
                # website
                submenu_help.append(defs.STRINGS["website"], "app.website")
                
                # menu options
                menu.append(defs.STRINGS["about"], "app.about")
                menu.append(defs.STRINGS["quit"], "app.quit")
                
                # set the menu as menu of the application
                self.set_app_menu(menu)
                
                # option "doc"
                doc_action = Gio.SimpleAction.new("doc", None)
                doc_action.connect("activate", self.doc)
                self.add_action(doc_action)
                # option "website"
                website_action = Gio.SimpleAction.new("website", None)
                website_action.connect("activate", self.website)
                self.add_action(website_action)
                # option "about"
                about_action = Gio.SimpleAction.new("about", None)
                about_action.connect("activate", self.about_cb, self)
                self.add_action(about_action)
                # option "quit"
                quit_action = Gio.SimpleAction.new("quit", None)
                quit_action.connect("activate", self.quit_cb)
                self.add_action(quit_action)
                
        def doc(self, action, param):
                functions.various.open_link_in_browser(None, defs.SITEMC + "magiccollection/utilisation.html", None)
        
        def website(self, action, param):
                functions.various.open_link_in_browser(None, defs.SITEMC + "magiccollection/", None)
        
        def about_cb(self, action, parameters, app):
                aboutdialog = Gtk.AboutDialog("")
                aboutdialog.set_transient_for(app.mainwindow)
                aboutdialog.set_title(defs.STRINGS["about"] + " - " + defs.STRINGS["app_name"])
                aboutdialog.set_program_name(defs.STRINGS["app_name"])
                if defs.DB_VERSION != None:
                        aboutdialog.set_version(defs.VERSION + " - " + defs.STRINGS["aboutdialog_db"] + " " + defs.DB_VERSION)
                else:
                        aboutdialog.set_version(defs.VERSION)
                aboutdialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(os.path.join(defs.PATH_MC, "images", "mclogo_min.png")))
                aboutdialog.set_copyright(defs.STRINGS["about_copyright"])
                aboutdialog.set_comments(defs.STRINGS["about_comment"])
                aboutdialog.set_authors(["mirandir [mirandir@orange.fr]"])
                aboutdialog.set_license(defs.STRINGS["about_licence"])
                aboutdialog.set_wrap_license(True)
                
                aboutdialog.run()
                aboutdialog.destroy()

        def quit_cb(self, action, parameter):
                if defs.COLL_LOCK:
                        # don't quit
                        functions.various.message_dialog(defs.STRINGS["coll_busy"], 0)
                else:
                        # quit
                        self.quit()
