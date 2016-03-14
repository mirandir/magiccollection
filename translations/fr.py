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
        translate["preferences"] = "Préférences"
        translate["preferences_of_mc"] = "Préférences de " + translate["app_name"]
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
        translate["search_card_tooltip"] = "Chercher une carte par nom"
        translate["no_result"] = "Aucun résultat."
        translate["aboutdialog_db"] = "BDD"
        translate["choose_card"] = "Choisir"
        translate["results"] = "%%% résultats :"
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
        translate["error_download_db"] = "Erreur lors du téléchargement de la base de données des cartes."
        translate["warning_ver_db"] = "Attention : cette version de la base de données ne fonctionnera qu'avec " + translate["app_name"] + " version %%% ou supérieure."
        translate["changelog_db"] = "Nouveautés :"
        translate["new_update_db"] = "Une mise à jour de la base de données des cartes est disponible.%%%\nVoulez-vous la télécharger maintenant ?"
        translate["downloading_db"] = "Téléchargement de la base de données…"
        translate["downloading_symbols"] = "Téléchargement des icônes des éditions…"
        translate["checking_db_update"] = "Vérification des mises à jour de la base de données…"
        # advanced search
        translate["searching"] = "Recherche en cours…"
        translate["please_wait"] = "Cette opération va prendre un peu de temps…"
        translate["search_ad"] = "Chercher"
        translate["operator_choice"] = "Opérateur logique"
        translate["operator_and"] = "et"
        translate["operator_or"] = "ou"
        translate["card"] = "carte"
        translate["cards"] = "cartes"
        translate["card_result"] = "résultat"
        translate["cards_result"] = "résultats"
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
        translate["column_internal_id"] = "id interne"
        translate["column_english_name"] = "Nom anglais" # must be 'Name' for the english file
        translate["column_english_name_complete"] = "Nom anglais" # must be 'Name' for the english file
        translate["column_edition"] = "Édition"
        translate["column_edition_complete"] = "Édition"
        translate["column_nonenglish_name"] = "Nom non-anglais"
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
        translate["column_colors_complete"] = "Couleur(s)"
        translate["column_cmc"] = "CCM"
        translate["column_cmc_complete"] = "Coût Converti de Mana"
        translate["column_type"] = "Type"
        translate["column_type_complete"] = "Type"
        translate["column_artist"] = "Artiste"
        translate["column_artist_complete"] = "Artiste"
        translate["column_power"] = "Force"
        translate["column_toughness"] = "Endurance"
        translate["column_rarity"] = "Rareté"
        translate["column_rarity_complete"] = "Rareté"
        translate["column_nb"] = "#"
        translate["column_nb_complete"] = "Quantité"
        translate["column_prices"] = "Prix"
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
        translate["open_display_price"] = "Prix indicatif : ;;;%%%"# ';;;' is replaced by the price, '%%%' by the currency
        translate["other_edition"] = "Autre édition"
        translate["other_editions"] = "Autres éditions"
        translate["download_card_no_internet"] = "Impossible de télécharger l'image de la carte : aucune connexion internet n'a été trouvée."
        translate["add_card_question"] = "Ajouter %%% à la collection ?"
        translate["add_card_question_without_collection"] = "Ajouter %%% ?"
        translate["add_cards_question"] = "Ajouter les %%% cartes suivantes à la collection ?"
        translate["add_cards_question_without_collection"] = "Ajouter les %%% cartes suivantes ?"
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
        translate["morebutton_tooltip"] = "Plus d'information"
        translate["dfbutton_seeotherside_tooltip"] = "Voir l'autre côté"
        translate["dfbutton_returncard_tooltip"] = "Retourner la carte"
        translate["cv_add_collection"] = "À la collection"
        translate["cv_add_proxies"] = "En tant que proxy"
        translate["cv_add_proxies_s"] = "En tant que proxies"
        # collection
        translate["db_coll_error"] = "Impossible de lire la collection."
        translate["coll_empty_welcome"] = "Bienvenue dans " + translate["app_name"] + " !\n\nVotre collection est vide. Vous pouvez chercher des cartes en utilisant l'icône de recherche en haut à gauche, ou en utilisant la recherche avancée.\nLorsque vous avez trouvé une carte à ajouter, passez la souris sur son image et cliquez sur le '+'."
        translate["nb_card_coll_s"] = "%%% cartes dans la collection"
        translate["nb_card_coll"] = "%%% carte dans la collection"
        translate["info_select_none_coll"] = "(aucune sélection)"
        translate["info_select_coll"] = "(1 sélection)"
        translate["info_selects_coll"] = "(%%% sélections)"
        translate["searching_coll"] = "Chercher dans la collection"
        translate["condition_coll"] = "État"
        translate["lang_coll"] = "Langue"
        translate["foil_coll"] = "Foil"
        translate["loaned_coll"] = "Prêté à"
        translate["comment_coll"] = "Commentaire"
        translate["date_coll"] = "Date d'ajout"
        translate["quantity_card_coll"] = "Nb exemplaires"
        translate["in_deck"] = "Dans deck"
        translate["search_coll"] = "Chercher"
        translate["back_to_coll"] = "Retour à la collection"
        translate["coll_button_search_wait"] = "Opération en cours…"
        translate["nb_card_found_coll_s"] = "%%% résultats"
        translate["nb_card_found_coll"] = "%%% résultat"
        translate["foil_yes"] = "oui"
        translate["foil_no"] = "non"
        translate["foil_only_yesno"] = "Le critère de recherche Foil ne peut s'utiliser qu'avec les valeurs suivantes : 1, 0, " + translate["foil_yes"] + ", " + translate["foil_no"] + "."
        translate["placeholder_date"] = "AAAA-MM-JJ" # y-m-d
        translate["date_format"] = "La recherche par Date d'ajout à la collection ne peut se faire qu'avec le format AAAA-MM-JJ (Année-Mois-Jour)."
        translate["quantity_card_coll_only_number"] = "La recherche par Nombre d'exemplaires dans la collection ne peut se faire qu'avec des valeurs numériques."
        translate["change_quantity"] = "Modifier la quantité"
        translate["change_quantity_validate"] = "Valider"
        translate["delete_select"] = "Supprimer la sélection"
        translate["delete_select_warning"] = "Tous les exemplaires de ces cartes vont être SUPPRIMÉS.\nÊtes-vous sûr(e) de vouloir continuer ?"
        translate["delete_all"] = "Effacer la collection et les decks"
        translate["delete_all_warning"] = "Tous vos decks et toutes les cartes de votre collection vont être SUPPRIMÉS.\nÊtes-vous sûr(e) de vouloir continuer ?"
        translate["state_card_coll_date"] = "Cette carte a été ajoutée à la collection le <b>{d}/{m}/{y}</b>."
        translate["state_card_coll_deck"] = "Elle est utilisée dans le deck <b>{deck}</b>."
        translate["search_collection_button"] = "Chercher dans la collection"
        translate["search_collection_tooltip"] = "Chercher dans les cartes de la collection"
        translate["show_details_tooltip"] = "Voir les détails"
        translate["change_quantity_tooltip"] = "Modifier la quantité"
        translate["add_deck_tooltip"] = "Ajouter à un deck"
        translate["estimate_cards_tooltip"] = "Estimer des cartes"
        translate["delete_cards_tooltip"] = "Supprimer des cartes"
        translate["copy_details_tooltip"] = "Copier les détails de cette carte vers toutes les autres cartes affichées"
        translate["delete_cards_details_tooltip"] = "Supprimer de la collection"
        # decks
        translate["list_decks_nb"] = "Liste des decks (%%%)"
        translate["create_new_deck"] = "Créer un nouveau deck"
        translate["estimate_deck"] = "Estimer la valeur du deck"
        translate["delete_deck"] = "Supprimer le deck"
        translate["decks_empty_welcome"] = "Vous n'avez pas encore saisi de deck dans " + translate["app_name"] + ".\nCliquez ici pour en saisir un."
        translate["create_new_deck_name"] = "Nom du deck"
        translate["create_new_deck_ok"] = "Valider"
        translate["comment_deck"] = "Commentaire du deck"
        translate["decks_click_deck"] = "Cliquez sur un deck pour afficher les cartes qu'il contient."
        translate["nb_cards_in_deck"] = "%%% carte"
        translate["nb_cards_in_deck_s"] = "%%% cartes"
        translate["move_to_other_deck"] = "Déplacer la sélection dans un autre deck"
        translate["delete_deck_warning"] = "Êtes-vous sûr(e) de vouloir supprimer le deck %%% ?"
        translate["delete_from_deck_tooltip"] = "Supprimer du deck"
        translate["move_to_other_deck_tooltip"] = "Déplacer dans un autre deck"
        # languages
        translate["l_english"] = "Anglais"
        translate["l_chinese"] = "Chinois"
        translate["l_french"] = "Français"
        translate["l_german"] = "Allemand"
        translate["l_italian"] = "Italien"
        translate["l_japanese"] = "Japonais"
        translate["l_korean"] = "Coréen"
        translate["l_portuguese"] = "Portugais"
        translate["l_russian"] = "Russe"
        translate["l_spanish"] = "Espagnol"
        # prices
        translate["error_download_db_prices"] = "Erreur lors du téléchargement de la base de données des prix des cartes."
        translate["no_internet_download_db_prices"] = "Impossible de télécharger la mise à jour de la base de données des prix des cartes : aucune connexion internet n'a été trouvée."
        translate["prices_db_damaged"] = "La base de données des prix des cartes semble endommagée. Vous pouvez la retélécharger depuis les préférences pour corriger le problème."
        # configuration
        translate["config_display"] = "Affichage"
        translate["config_editions"] = "Éditions"
        translate["config_ext_fr_name"] = "Afficher le nom français des éditions lorsqu'il existe"
        translate["config_ext_sort_as"] = "Dans la recherche avancée, trier les éditions par :"
        translate["config_ext_sort_as_date"] = "Date de sortie"
        translate["config_ext_sort_as_name"] = "Nom"
        translate["config_searches"] = "Recherches"
        translate["config_no_reprints"] = "Ne pas afficher les différentes rééditions d'une même carte lors des recherches"
        translate["config_cardviewer"] = "Visionneur de carte"
        translate["config_show_en_name_in_card_viewer"] = "Afficher également le nom anglais dans le visionneur de carte"
        translate["config_collection"] = "Collection"
        translate["config_add_collection_show_details"] = "Afficher les détails lors de l'ajout de carte à la collection"
        translate["config_general_aspect"] = "Aspect général"
        translate["config_dark_theme"] = "Utiliser le thème sombre"
        translate["config_columns"] = "Colonnes"
        translate["config_columns_helper"] = "Vous pouvez changer l'ordre d'affichage en glissant-déplaçant les intitulés des colonnes."
        translate["config_column_enabled"] = "Active"
        translate["config_nonenglish_names"] = "Noms non-anglais"
        translate["config_fr_language"] = "Langue de la colonne affichant les noms non-anglais :"
        translate["config_columns_order_disp"] = "Affichage et ordre des colonnes"
        translate["config_columns_collection"] = "Colonnes - Collection"
        translate["config_columns_decks"] = "Colonnes - Decks"
        translate["config_columns_as"] = "Colonnes - Recherche avancée"
        translate["config_internet"] = "Internet"
        translate["config_pics_cards"] = "Images des cartes"
        translate["config_download_pic_collection_decks"] = "Télécharger les images des cartes dans le mode Collection et le mode Decks"
        translate["config_download_pic_as"] = "Télécharger les images des cartes dans le mode Recherche avancée"
        translate["config_connection"] = "Connexion"
        translate["config_not_internet_popup"] = "Afficher un avertissement quand aucune connexion internet n'est trouvée"
        translate["config_cardsprices"] = "Prix des cartes"
        translate["config_cardsprices_download_first"] = "Téléchargez d'abord les prix des cartes en cliquant ici."
        translate["config_cardsprices_download"] = "Télécharger les prix des cartes"
        translate["config_prices_show"] = "Affichage des prix"
        translate["config_cardsprices_show"] = "Afficher les prix des cartes dans le menu 'Plus d'information' du visionneur de carte"
        translate["config_price_cur"] = "Les prix sont affichés en :"
        translate["config_price_dollars"] = "Dollars"
        translate["config_price_euros"] = "Euros"
        translate["config_prices_update"] = "Mise à jour des prix"
        translate["config_prices_autoupdate"] = "Mettre automatiquement à jour les prix au lancement de " + translate["app_name"]
        translate["config_prices_version"] = "Version de la base de données des prix : <b>%%%</b>."
        translate["config_cardsprices_update"] = "Mettre à jour les prix des cartes"
        translate["config_cardsprices_checking_update"] = "Vérification des mises à jour des prix des cartes…"
        translate["config_cardsprices_downloading"] = "Téléchargement des prix des cartes…"
        translate["config_need_restart"] = "Nécessite un redémarrage de " + translate["app_name"]
        #########################
        return(translate)
