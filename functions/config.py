#!/usr/bin/python
# -*-coding:Utf-8 -*
#
# Read & write the configuration file

import os

# importation des valeurs globales
import defs

def read_config_file():
        '''Read the configuration file.'''
        configfile = open(os.path.join(defs.CONFIGMC, "config"), "r", encoding="UTF-8")
        config = configfile.readlines()
        configfile.close()
        
        configuration = {}
        
        i = 0
        for ligne in config:
                ligne = ligne.rstrip("\n\r")
                ligneexplode = ligne.split(" ")
                configuration[ligneexplode[0]] = [ligneexplode[2], i]
                i = i + 1
        return(configuration)

def read_config(param):
        '''Return one param of config.'''
        if param in defs.VARCONFIGDEFAULT.keys():
                configuration = read_config_file()
                try:
                        valeur = configuration[param][0]
                except KeyError:
                        valeur = defs.VARCONFIGDEFAULT[param]
                return(valeur)
        else:
                print("param is unknown !")

def change_config(param, valeur):
        '''Change the configuration.'''
        configuration = read_config_file()
        if param in defs.VARCONFIGDEFAULT.keys():
                try:
                        valeuractuelle = configuration[param][0]
                except KeyError:
                        valeuractuelle = defs.VARCONFIGDEFAULT[param]
                        # param not found in the config file, adding...
                        out = open(os.path.join(defs.CONFIGMC, "config"), 'a', encoding="UTF-8")
                        nouveautexte = param + " = " + valeuractuelle + "\n"
                        out.write(nouveautexte)
                        out.close()
                        configuration = read_config_file()
                if valeuractuelle != valeur:
                        # new value != current value, changing config file
                        lines = open(os.path.join(defs.CONFIGMC, "config"), 'r', encoding="UTF-8").readlines()
                        nbligne = configuration[param][1]
                        nouveautexte = param + " = " + valeur + "\n"
                        lines[nbligne] = nouveautexte
                        out = open(os.path.join(defs.CONFIGMC, "config"), 'w', encoding="UTF-8")
                        out.writelines(lines)
                        out.close()
        else:
                print("param is unknown !")
