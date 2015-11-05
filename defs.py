#!/usr/bin/python
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
        # FIXME: needs testing for Apple OS !
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

# MC dirs
HOMEMC = os.path.join(DATA, "magiccollection")
CONFIGMC = os.path.join(CONFIG, "magiccollection")
CACHEMC = os.path.join(CACHE, "magiccollection")
CACHEMCPIC = os.path.join(CACHEMC, "downloadedPics")
CACHEMCPR = os.path.join(CACHEMC, "prices")

# MC website
SITEMC = "http://mirandir.pagesperso-orange.fr/"

### Config var and default values

# default values, for english language
ext_fr_name = "0"
fr_language = "de"
as_columns = "name;type;edition;colors"
coll_columns = "name;type;edition;colors;nb"
# default values for specific language
if LANGUAGE == "fr":
        ext_fr_name = "1"
if LANGUAGE in LOC_NAME_FOREIGN.keys():
        fr_language = LANGUAGE
        as_columns = "name_foreign;type;edition;colors"
        coll_columns = "name_foreign;type;edition;colors;nb"

VARCONFIGDEFAULT = {
"download_pic_collection_decks": "1",
"download_pic_as": "1",
"add_collection_show_details": "0",
"not_internet_popup": "0",
"ext_sort_as": "0",
"ext_fr_name": ext_fr_name,
"fr_language": fr_language,
"cards_price": "0",
"price_cur": "0",
"dark_theme": "0",
"as_columns": as_columns,
"coll_columns": coll_columns
}

# column names available for advanced search
AS_COLUMNS_CHOICE = ["name", "edition", "name_foreign", "colors", "cmc", "type", "artist", "power", "toughness", "rarity"]

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
12:["flavor", STRINGS["flavor_ad"]]
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
"{C}": ["c.png", 18],
"{CHAOS}": ["c.png", 18],
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

# threads things
COLL_LOCK = False
BUTTON_COLL_LOCK = None
AS_LOCK = False

DB_VERSION = None
VERSION = "0.9"
