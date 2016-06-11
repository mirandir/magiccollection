#!/usr/bin/python
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

# This file defines global variables for Magic Collection

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import platform
import os
import locale

# translations - each translation must be loaded here
import translations.en
import translations.fr


PATH_MC = os.path.dirname(os.path.abspath(__file__))

# OS/GUI detection
OS = ""
if platform.system() == "Windows":
        OS = "windows"
elif platform.system() == "Darwin":
        OS = "mac"
elif platform.system() == "Linux":
        if os.environ.get("XDG_CURRENT_DESKTOP") == "GNOME":
                OS = "gnome"
        elif os.environ.get("XDG_CURRENT_DESKTOP") == "Unity":
                OS = "unity"
        else:
                OS = "linux"

# language detection
LANGUAGE = "en"
if OS == "windows":
        import ctypes
        windll = ctypes.windll.kernel32
        if locale.windows_locale[windll.GetUserDefaultUILanguage()][:2] != "":
                LANGUAGE = locale.windows_locale[windll.GetUserDefaultUILanguage()][:2]
else:
        locale.setlocale(locale.LC_ALL, '')
        if locale.getlocale()[0][:2] != "":
                LANGUAGE = locale.getlocale()[0][:2]

# we load the right translation here - each new translation must be added here
if LANGUAGE == "fr":
        STRINGS = translations.fr.translate()
else:
        STRINGS = translations.en.translate()

# dict locale -> foreign name of the cards
LOC_NAME_FOREIGN = {
"zh" : "name_chinesesimp",
"fr" : "name_french",
"de" : "name_german",
"it" : "name_italian",
"ja" : "name_japanese",
"ko" : "name_korean",
"pt" : "name_portuguese",
"ru" : "name_russian",
"es" : "name_spanish"
}

# dict locale -> language name
LOC_LANG_NAME = {
0: ["zh", STRINGS["l_chinese"]],
1: ["fr", STRINGS["l_french"]],
2: ["de", STRINGS["l_german"]],
3: ["it", STRINGS["l_italian"]],
4: ["ja", STRINGS["l_japanese"]],
5: ["ko", STRINGS["l_korean"]],
6: ["pt", STRINGS["l_portuguese"]],
7: ["ru", STRINGS["l_russian"]],
8: ["es", STRINGS["l_spanish"]]
}

# screen's size
DISPLAY_WIDTH = Gdk.Screen.get_default().get_width()
DISPLAY_HEIGHT = Gdk.Screen.get_default().get_height()

# user dirs
HOME = os.path.expanduser('~')
CONFIG = GLib.get_user_config_dir()
DATA = GLib.get_user_data_dir()
CACHE = GLib.get_user_cache_dir()
if OS == "windows":
        CACHE = GLib.get_user_data_dir() # we use data dir for cache on Windows, because some tools empty the default GLib cache location
# we respect the Apple guidelines(see https://developer.apple.com/library/mac/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/MacOSXDirectories/MacOSXDirectories.html#//apple_ref/doc/uid/TP40010672-CH10-SW1)
if OS == "mac":
        CONFIG = os.path.join(HOME, "Library", "Application Support")
        DATA = os.path.join(HOME, "Library", "Application Support")
        CACHE = os.path.join(HOME, "Library", "Caches")

# MC dirs
HOMEMC = os.path.join(DATA, "magiccollection")
BACKUPMC = os.path.join(HOMEMC, "backup")
CONFIGMC = os.path.join(CONFIG, "magiccollection")
CACHEMC = os.path.join(CACHE, "magiccollection")
CACHEMCPIC = os.path.join(CACHEMC, "downloadedPics")
CACHEMCPR = os.path.join(CACHEMC, "prices")

# we add our folders to paths where GTK is looking for icons
Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.join(PATH_MC, "images", "math"))
Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.join(PATH_MC, "images", "symbolic-mana"))
Gtk.IconTheme.append_search_path(Gtk.IconTheme.get_default(), os.path.join(PATH_MC, "images", "icons"))

# we add a custom size for gicons
Gtk.icon_size_register('150_mana_symbol', 150, 150)
Gtk.icon_size_register('100_mana_symbol', 100, 100)
Gtk.icon_size_register('12_config_warning', 12, 12)

# MC website
SITEMC = "http://mirandir.pagesperso-orange.fr/"

### Config var and default values

# default values, for english language
ext_fr_name = "0"
fr_language = "de"
as_columns = "name;type;edition;colors"
coll_columns = "name;type;edition;colors;nb"
decks_columns = "name;type;edition;colors;nb"
# default values for specific language
if LANGUAGE == "fr":
        ext_fr_name = "1"
if LANGUAGE in LOC_NAME_FOREIGN.keys():
        fr_language = LANGUAGE
        as_columns = "name_foreign;type;edition;colors"
        coll_columns = "name_foreign;type;edition;colors;nb"
        decks_columns = "name_foreign;type;edition;colors;nb"

VARCONFIGDEFAULT = {
"download_pic_collection_decks": "1",
"download_pic_as": "1",
"add_collection_show_details": "0",
"not_internet_popup": "0",
"ext_sort_as": "0",
"ext_fr_name": ext_fr_name,
"fr_language": fr_language,
"show_en_name_in_card_viewer": "0",
"cards_price": "0",
"price_cur": "1",
"price_autodownload": "0",
"dark_theme": "0",
"as_columns": as_columns,
"coll_columns": coll_columns,
"decks_columns": decks_columns,
"no_reprints": "0",
"last_width": "0",
"last_height": "0"
}

# column names available for the configuration window
AS_COLUMNS_CHOICE = ["name", "edition", "name_foreign", "colors", "cmc", "type", "artist", "power", "toughness", "rarity"]
COLL_COLUMNS_CHOICE = ["name", "edition", "name_foreign", "colors", "cmc", "type", "artist", "power", "toughness", "rarity", "nb"]
DECKS_COLUMNS_CHOICE = ["name", "edition", "name_foreign", "colors", "cmc", "type", "artist", "power", "toughness", "rarity", "nb"]

# dict column name -> column name translated
COLUMN_NAME_TRANSLATED = {
"name": STRINGS["column_english_name_complete"],
"edition": STRINGS["column_edition_complete"],
"name_foreign": STRINGS["column_nonenglish_name"],
"colors": STRINGS["column_colors_complete"],
"cmc": STRINGS["column_cmc_complete"],
"type": STRINGS["column_type_complete"],
"artist": STRINGS["column_artist_complete"],
"power": STRINGS["column_power"],
"toughness": STRINGS["column_toughness"],
"rarity": STRINGS["column_rarity_complete"],
"nb": STRINGS["column_nb_complete"]
}

SEARCH_ITEMS = {
0:["name", STRINGS["name_ad"]],
1:["edition", STRINGS["edition_ad"]],
2:["type", STRINGS["type_ad"]],
3:["colors", STRINGS["colors_ad"]],
4:["manacost", STRINGS["manacost_eg_ad"]],
5:["cmc", STRINGS["cmc_ad"]],
6:["rarity", STRINGS["rarity"]],
7:["power", STRINGS["power_ad"]],
8:["toughness", STRINGS["toughness_ad"]],
9:["loyalty", STRINGS["loyalty_ad"]],
10:["text", STRINGS["text_ad"]],
11:["artist", STRINGS["artist_ad"]],
12:["flavor", STRINGS["flavor_ad"]],
13:["condition", STRINGS["condition_coll"]],
14:["lang", STRINGS["lang_coll"]],
15:["foil", STRINGS["foil_coll"]],
16:["loaned", STRINGS["loaned_coll"]],
17:["comment", STRINGS["comment_coll"]],
18:["date", STRINGS["date_coll"]],
19:["in_deck", STRINGS["in_deck"]],
20:["quantity_card", STRINGS["quantity_card_coll"]]
}

CONDITIONS = {
0: ["mint", STRINGS["condition_mint"]],
1: ["near_mint", STRINGS["condition_near_mint"]],
2: ["excellent", STRINGS["condition_excellent"]],
3: ["played", STRINGS["condition_played"]],
4: ["poor", STRINGS["condition_poor"]]
}

# text to replace with a picture in cards' texts
# text: [file, image size to display]
PIC_IN_TEXT = {
"{T}": ["t.png", 15],
"{Q}": ["q.png", 15],
"{0}": ["0.png", 15],
"{B}": ["b.png", 15],
"{G}": ["g.png", 15],
"{R}": ["r.png", 15],
"{U}": ["u.png", 15],
"{W}": ["w.png", 15],
"{2/B}": ["2b.png", 15],
"{2/G}": ["2g.png", 15],
"{2/R}": ["2r.png", 15],
"{2/U}": ["2u.png", 15],
"{2/W}": ["2w.png", 15],
"{∞}": ["infinite.png", 15],
"{C}": ["c.png", 15],
"{CHAOS}": ["chaos.png", 18],
"{hr}": ["hr.png", 15],
"{hw}": ["hw.png", 15],
"{S}": ["s.png", 15],
"{X}": ["x.png", 15],
"{Y}": ["y.png", 15],
"{Z}": ["z.png", 15],
"{100}": ["100.png", 28],
"{B/G}": ["bg.png", 15],
"{B/R}": ["br.png", 15],
"{U/B}": ["bu.png", 15],
"{W/B}": ["bw.png", 15],
"{R/G}": ["gr.png", 15],
"{G/U}": ["gu.png", 15],
"{G/W}": ["gw.png", 15],
"{U/R}": ["ru.png", 15],
"{R/W}": ["rw.png", 15],
"{W/U}": ["uw.png", 15],
"{B/P}": ["bp.png", 15],
"{G/P}": ["gp.png", 15],
"{R/P}": ["pr.png", 15],
"{U/P}": ["pu.png", 15],
"{W/P}": ["pw.png", 15],
"{P}": ["p.png", 15]
}

for nb in range(20):
        PIC_IN_TEXT["{" + str(nb) + "}"] = [str(nb) + ".png", 15]

DICT_EDITIONS = {}
LIST_LANDS_SELECTED = []

# editions for prices search only, from TCG
EDITIONS_PRICES = ["champs promos", "game day promos", "grand prix promos", "launch party cards", "media promos", "pro tour promos", "release event cards", "special occasion", "wpn promos", "unique and miscellaneous promos"]

MAINWINDOW = None
DB_DOWNLOAD_PROGRESS = 0
MEM_SEARCHS = {}
PREF_WINDOW_OPEN = False

SIMPLY_SEARCH_ENTRY_HAD_FOCUS = None

# threads things
COLL_LOCK = False
BUTTON_COLL_LOCK = None
AS_LOCK = False
CURRENT_SAVEDETAILS_THREAD = None
CURRENT_SAVE_COMMENT_DECK_THREAD = None
SAVEDETAILS_TIMER = None
SAVE_COMMENT_DECK_TIMER = None
READ_COLL_FINISH = False

GTK_MINOR_VERSION = Gtk.get_minor_version()

PRICES_DATE = None
DB_VERSION = None
VERSION = "0.8.106"
