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

# French translation for Magic Collection

def translate():
        translate = {}
        #########################
        translate["app_name"] = "Magic Collection"
        translate["language_name"] = "Français"
        # Gmenu
        translate["help"] = "Aide"
        translate["doc"] = "Documentation"
        translate["website"] = "Site internet"
        translate["about"] = "À propos"
        translate["quit"] = "Quitter"
        # About Window
        translate["about_comment"] = "Les informations, textes et images affichés à propos\nde Magic: The Gathering sont © Wizards of the Coast."
        
        translate["about_copyright"] = translate["app_name"] + ''' n'est pas produit, affilié ou soutenu\npar Wizards of the Coast ou Hasbro.

''' + translate["app_name"] + ''' utilise mtgjson.com pour une partie
de sa base de données.
Merci à Sembiance et AndarilhoMTG pour l'extraordinaire travail réalisé sur ce site !
Les informations de prix sont founies par TCGplayer.com.
Elles sont affichées uniquement dans un but d'information, et elles
n'engagent ni ''' + translate["app_name"] + ''' ni son auteur.'''
        
        translate["about_licence"] = translate["app_name"] + ''' est un logiciel libre : vous pouvez le redistribuer et/ou le modifier selon les termes de la Licence Publique Générale GNU 3, publiée par la Free Software Foundation.

''' + translate["app_name"] + ''' est distribué dans l'espoir qu'il puisse vous être utile, mais SANS AUCUNE GARANTIE ; sans même de garantie de VALEUR MARCHANDE ou d'ADÉQUATION A UN BESOIN PARTICULIER. Consultez la Licence Publique Générale GNU 3 pour plus de détails.

Vous devez avoir reçu une copie de la Licence Publique Générale GNU 3 en même temps que ''' + translate["app_name"] + ''' ; si ce n'est pas le cas, consultez <http://www.gnu.org/licenses/>.

Logo de ''' + translate["app_name"] + ''' par mirandir, sous licence CC BY-NC-ND 3.0 : <https://creativecommons.org/licenses/by-nc-nd/3.0/deed.fr/>

Images d'indicateurs de couleur par BaconCatBug (voir <http://www.mtgsalvation.com/forums/creativity/artwork/494438-baconcatbugs-set-and-mana-symbol-megapack/>)
Icônes mathématiques réalisées par Freepik (<http://www.flaticon.com/packs/mathbert-mathematics>)'''
        
        # mainwindow
        translate["loading"] = "Chargement…"
        translate["collection"] = "Collection"
        translate["decks"] = "Decks"
        translate["advancedsearch"] = "Recherche avancée"
        translate["search_card"] = "Chercher une carte par nom"
        translate["no_result"] = "Aucun résultat."
        translate["aboutdialog_db"] = "BDD"
        translate["choose_card"] = "Choisir"
        translate["result"] = "%%% cartes trouvées :"
        translate["coll_busy"] = "Une opération est en cours sur la collection, impossible de quitter pour l'instant."
        # non english helpers for simple search - without accents or uppercase letters (must be empty for the english translation file)
        translate["forest"] = "foret"
        translate["island"] = "ile"
        translate["mountain"] = "montagne"
        translate["swamp"] = "marais"
        translate["plains"] = "plaine"
        # Database
        translate["db_damaged"] = "La base de données semble endommagée. Merci de relancer " + translate["app_name"] + " pour corriger le problème."
        translate["no_internet_update_db"] = "Impossible de vérifier les mises à jour de la base de données : aucune connexion internet n'a été trouvée."
        translate["no_internet_download_db"] = "Impossible de télécharger la mise à jour de la base de données : aucune connexion internet n'a été trouvée."
        translate["error_download_db"] = "Erreur lors du téléchargement de la base de données."
        translate["warning_ver_db"] = "Attention : cette version de la base de données ne fonctionnera qu'avec " + translate["app_name"] + " version %%% ou supérieure."
        translate["changelog_db"] = "Nouveautés :"
        translate["new_update_db"] = "Une mise à jour de la base de données des cartes est disponible.%%%\nVoulez-vous la télécharger maintenant ?"
        translate["downloading_db"] = "Téléchargement de la base de données…"
        translate["downloading_symbols"] = "Téléchargement des icônes des éditions…"
        # advanced search
        translate["searching"] = "Recherche en cours…"
        translate["please_wait"] = "Cette opération va prendre un peu de temps…"
        translate["search_ad"] = "Rechercher"
        translate["operator_choice"] = "Opérateur logique"
        translate["operator_and"] = "et"
        translate["operator_or"] = "ou"
        translate["card"] = "carte"
        translate["cards"] = "cartes"
        translate["list_editions"] = "Liste des éditions"
        translate["add_edition"] = "Ajouter l'édition"
        translate["name_ad"] = "Nom"
        translate["edition_ad"] = "Édition"
        translate["colors_ad"] = "Couleur(s)"
        translate["manacost_eg_ad"] = "Coût de mana"
        translate["cmc_ad"] = "Coût converti"
        translate["type_ad"] = "Type"
        translate["artist_ad"] = "Artiste"
        translate["text_ad"] = "Texte"
        translate["flavor_ad"] = "Texte d'ambiance"
        translate["power_ad"] = "Force"
        translate["toughness_ad"] = "Endurance"
        translate["loyalty_ad"] = "Loyauté"
        translate["entry_eq_ad"] = "Égal"
        translate["entry_inf_eq_ad"] = "Inférieur ou égal"
        translate["entry_sup_eq_ad"] = "Supérieur ou égal"
        translate["entry_diff"] = "Différent"
        translate["nb_cards_in_db"] = "Il y a %%% cartes dans la base de données, à peu de chose près."
        translate["column_english_name"] = "Nom anglais"
        translate["column_edition"] = "Édition"
        translate["column_name_name_french"] = "Nom français"
        translate["column_name_name_chinesetrad"] = "Nom chinois (trad)"
        translate["column_name_name_chinesesimp"] = "Nom chinois (simpl)"
        translate["column_name_name_german"] = "Nom allemand"
        translate["column_name_name_italian"] = "Nom italien"
        translate["column_name_name_japanese"] = "Nom japonais"
        translate["column_name_name_korean"] = "Nom coréen"
        translate["column_name_name_portuguesebrazil"] = "Nom portugais (B)"
        translate["column_name_name_portuguese"] = "Nom portugais"
        translate["column_name_name_russian"] = "Nom russe"
        translate["column_name_name_spanish"] = "Nom espagnol"
        translate["column_colors"] = "Coul."
        translate["column_cmc"] = "CCM"
        translate["column_type"] = "Type"
        translate["column_artist"] = "Artiste"
        translate["column_power"] = "Force"
        translate["column_toughness"] = "Endu."
        translate["column_rarity"] = "Rareté"
        translate["column_nb"] = "#"
        translate["cmc_only_number"] = "La recherche par Coût converti de mana ne peut se faire qu'avec des valeurs numériques."
        translate["power_only_number"] = "La recherche par Force ne peut se faire qu'avec des valeurs numériques."
        translate["toughness_only_number"] = "La recherche par Endurance ne peut se faire qu'avec des valeurs numériques."
        translate["loyalty_only_number"] = "La recherche par Loyauté ne peut se faire qu'avec des valeurs numériques."
        # rarity
        translate["rarity"] = "Rareté"
        translate["mythic"] = "Mythique"
        translate["rare"] = "Rare"
        translate["uncommon"] = "Unco"
        translate["common"] = "Commune"
        translate["basic_land"] = "Terrain de base"
        translate["special"] = "Spéciale"
        # non english helpers - without accents or uppercase letters (must be empty for the english translation file)
        translate["artifact"] = "artefact"
        translate["artifacts"] = "artefacts"
        translate["enchantment"] = "enchantement"
        translate["enchantments"] = "enchantements"
        translate["instant"] = "ephemere"
        translate["instants"] = "ephemeres"
        translate["land"] = "terrain"
        translate["lands"] = "terrains"
        translate["planeswalker"] = "arpenteur"
        translate["planeswalkers"] = "arpenteurs"
        translate["creature"] = "creature"
        translate["creatures"] = "creatures"
        translate["sorcery"] = "rituel"
        translate["sorceries"] = "rituels"
        translate["token"] = "jeton"
        translate["tokens"] = "jetons"
        translate["emblem"] = "embleme"
        translate["emblems"] = "emblemes"
        translate["counter"] = "marqueur"
        translate["counters"] = "marqueurs"
        translate["red"] = "rouge"
        translate["green"] = "vert"
        translate["black"] = "noir"
        translate["blue"] = "bleu"
        translate["white"] = "blanc"
        translate["colorless"] = "incolore"
        translate["h_mythic"] = "mythique"
        translate["h_rare"] = "rare"
        translate["h_uncommon"] = "unco"
        translate["h_common"] = "commune"
        translate["h_basic_land"] = "terrain de base"
        translate["h_special"] = "speciale"
        # card viewer
        translate["open_gatherer"] = "Ouvrir le Gatherer"
        translate["other_edition"] = "Autre édition"
        translate["other_editions"] = "Autres éditions"
        translate["download_card_no_internet"] = "Impossible de télécharger l'image de la carte : aucune connexion internet n'a été trouvée."
        translate["add_card_question"] = "Ajouter %%% à la collection ?"
        translate["add_cards_question"] = "Ajouter les %%% cartes suivantes à la collection ?"
        translate["warning_nb_card"] = "(Attention : cette opération va prendre du temps)"
        translate["quantity"] = "Quantité :"
        translate["details"] = "Détails"
        translate["add_button_validate"] = "Ajouter"
        translate["add_button_wait"] = "Opération en cours…"
        translate["add_condition"] = "État"
        translate["condition_mint"] = "Mint"
        translate["condition_near_mint"] = "Near Mint"
        translate["condition_excellent"] = "Excellent"
        translate["condition_played"] = "Played"
        translate["condition_poor"] = "Poor"
        translate["add_lang"] = "Langue"
        translate["add_foil"] = "Foil"
        translate["add_loaned"] = "Prêté à"
        translate["add_comment"] = "Commentaire"
        # collection
        translate["db_coll_error"] = "Impossible de lire la collection."
        translate["coll_empty_welcome"] = "Bienvenue dans " + translate["app_name"] + " !\n\nVotre collection est vide. Vous pouvez rechercher des cartes en utilisant l'icône de recherche en haut à gauche, ou en utilisant la recherche avancée.\nLorsque vous avez trouvé une carte à ajouter, passez la souris sur son image et cliquez sur le '+'."
        translate["nb_card_coll_s"] = "%%% cartes dans la collection"
        translate["nb_card_coll"] = "%%% carte dans la collection"
        translate["info_select_none_coll"] = "(aucune sélection)"
        translate["info_select_coll"] = "(1 sélection)"
        translate["info_selects_coll"] = "(%%% sélections)"
        #########################
        return(translate)
