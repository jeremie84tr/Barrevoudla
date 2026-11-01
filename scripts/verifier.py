#!/usr/bin/env python3
"""Vérifie la validité des JSON et la cohérence des valeurs dérivées."""
import json, sys, glob

erreurs = []
def charger(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        erreurs.append(f"{p}: JSON invalide ({e})")

for p in glob.glob("**/*.json", recursive=True):
    charger(p)

base = charger("personnage/base.json")
etat = charger("personnage/etat.json")
if base and etat:
    pb = base["maitrises"]["bonus_maitrise"]
    for nom, c in base["caracteristiques"].items():
        attendu = (c["valeur"] - 10) // 2
        if c["modificateur"] != attendu:
            erreurs.append(f"{nom}: modificateur {c['modificateur']} != {attendu}")
        js = base["maitrises"]["jets_de_sauvegarde"][nom]
        attendu = c["modificateur"] + (pb if js["maitrise"] else 0)
        if js["bonus"] != attendu:
            erreurs.append(f"JS {nom}: bonus {js['bonus']} != {attendu}")
    cb = etat["combat"]
    if not 0 <= cb["pv_actuels"] <= cb["pv_max"]:
        erreurs.append("pv_actuels hors limites")
    for r in etat["ressources"]:
        if r["max"] - r["cases_cochees"] != r["restant"]:
            erreurs.append(f"ressource {r['nom']}: restant incohérent")

if erreurs:
    print("\n".join(erreurs)); sys.exit(1)
print("OK")
