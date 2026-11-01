#!/usr/bin/env python3
"""Valide les JSON contre schema/*.schema.json et vérifie la cohérence des valeurs dérivées."""
import json, sys, glob

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("jsonschema manquant : pip install jsonschema")

SCHEMAS = {
    "personnage/base.json": "base",
    "personnage/etat.json": "etat",
    "personnage/inventaire.json": "inventaire",
    "campagne/campagne.json": "campagne",
    "campagne/pnj.json": "pnj",
}
erreurs = []

def charger(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        erreurs.append(f"{p}: JSON invalide ({e})")

for p in glob.glob("**/*.json", recursive=True):
    charger(p)

donnees = {}
for chemin, nom in SCHEMAS.items():
    d = charger(chemin)
    donnees[nom] = d
    schema = charger(f"schema/{nom}.schema.json")
    if d is None or schema is None:
        continue
    for e in Draft202012Validator(schema).iter_errors(d):
        chemin_err = "/".join(map(str, e.absolute_path)) or "(racine)"
        erreurs.append(f"{chemin} [{chemin_err}]: {e.message}")

base, etat = donnees.get("base"), donnees.get("etat")
if base and etat and not erreurs:
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
    if cb["pv_actuels"] > cb["pv_max"]:
        erreurs.append("pv_actuels > pv_max")
    for r in etat["ressources"]:
        if r["max"] - r["cases_cochees"] != r["restant"]:
            erreurs.append(f"ressource {r['nom']}: restant incohérent")

if erreurs:
    print("\n".join(erreurs)); sys.exit(1)
print("OK")
