#!/usr/bin/env python3
"""Génère fiche.md (fiche lisible) depuis les JSON.

Usage : python3 scripts/generer_fiche.py [--check]
  --check : échoue si fiche.md n'est pas à jour (utilisé en CI).
"""
import json, sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "fiche.md"

def charger(p):
    return json.loads((RACINE / p).read_text(encoding="utf-8"))

def signe(n):
    return f"{n:+d}" if n is not None else "–"

LIBELLES = {
    "dexterite": "Dextérité", "athletisme": "Athlétisme", "discretion": "Discrétion",
    "perception": "Perception", "medecine": "Médecine", "religion": "Religion",
    "dressage": "Dressage", "persuasion": "Persuasion", "representation": "Représentation",
    "intimidation": "Intimidation", "tromperie": "Tromperie", "perspicacite": "Perspicacité",
    "survie": "Survie", "defauts": "Défauts", "ideaux": "Idéaux", "traits_de_caractere": "Traits de caractère",
}

def nom(cle):
    return LIBELLES.get(cle) or cle.replace("_", " ").capitalize()

def liste(items):
    return ", ".join(items) if items else "–"

def tableau(entetes, lignes):
    out = ["| " + " | ".join(entetes) + " |", "|" + "---|" * len(entetes)]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in l) + " |" for l in lignes]
    return out

def generer():
    b, e = charger("personnage/base.json"), charger("personnage/etat.json")
    inv, camp = charger("personnage/inventaire.json"), charger("campagne/campagne.json")
    pnj = charger("campagne/pnj.json")
    i, c, m = b["identite"], e["combat"], b["maitrises"]
    L = []
    L += [f"# {i['nom']}", "",
          "> Fichier généré par `scripts/generer_fiche.py` : ne pas modifier à la main.", "",
          f"{i['espece']} {i['lignee'].lower()} · {i['classe']} ({i['sous_classe']}) niveau {e['niveau']['niveau']} · "
          f"{i['historique']} · {i['alignement']}",
          f"Joueur : {i['joueur']} · Campagne : {camp['nom']} (MJ {camp['mj']}) · "
          f"Session {camp['session']}, mise à jour le {camp['date_maj']}", "",
          "## Combat", ""]
    L += tableau(["PV", "PV temp.", "CA", "Initiative", "Vitesse", "Maîtrise", "Perception passive"],
                 [[f"{c['pv_actuels']}/{c['pv_max']}", c["pv_temporaires"], c["classe_armure"],
                   signe(c["initiative"]), c["vitesse"], signe(m["bonus_maitrise"]),
                   e["sens"]["perception_passive"]]])
    dv = c["des_de_vie"]
    L += ["", f"- Dés de vie : {dv['restants']}/{dv['total']} {dv['type']}",
          f"- Résistances : {liste(c['resistances'])} · Immunités : {liste(c['immunites'])} · "
          f"Vulnérabilités : {liste(c['vulnerabilites'])}",
          f"- États : {liste(c['etats'])} · Inspiration : {'oui' if c['inspiration'] else 'non'}",
          f"- Sens : {e['sens']['vision']}", "", "## Caractéristiques", ""]
    L += tableau(["", "Valeur", "Mod.", "Jet de sauvegarde"],
                 [[nom(k), v["valeur"], signe(v["modificateur"]),
                   signe(m["jets_de_sauvegarde"][k]["bonus"]) + (" ●" if m["jets_de_sauvegarde"][k]["maitrise"] else "")]
                  for k, v in b["caracteristiques"].items()])
    L += ["", "## Compétences", ""]
    L += tableau(["Compétence", "Carac.", "Bonus"],
                 [[nom(k) + (" ●" if v["maitrise"] else ""), nom(v["carac"]), signe(v["bonus"])]
                  for k, v in m["competences"].items()])
    L += ["", "● = maîtrise", "", "## Attaques", ""]
    L += tableau(["Attaque", "Bonus", "Dégâts", "Notes"],
                 [[a["nom"], signe(a["bonus_attaque"]), (a["degats"] + " " + a.get("type_degats", "")).strip(),
                   a.get("notes", "")] for a in e["attaques"]])
    L += ["", "## Ressources", ""]
    L += tableau(["Ressource", "Restant", "Recharge", "Notes"],
                 [[r["nom"], f"{r['restant']}/{r['max']}", r["recharge"], r.get("notes", "")]
                  for r in e["ressources"]])
    L += ["", "## Traits et aptitudes", ""]
    for t in b["traits"]["traits_d_espece"] + b["traits"]["aptitudes_de_classe"]:
        L.append(f"- **{t['nom']}** : {t['description']}")
    L += ["", "### Bottes d'arme", ""]
    for t in b["traits"]["bottes_d_arme_details"]:
        L.append(f"- **{t['nom']}** ({t['declencheur'].lower()}) : {t['description']}")
    L += ["", "### Dons", ""]
    for t in b["traits"]["dons"]:
        L.append(f"- **{t['nom']}** ({t['origine']}) : {t['description']}")
    L += ["", "## Maîtrises", "",
          f"- Armures : {liste(m['armures'])}", f"- Armes : {liste(m['armes'])}",
          f"- Outils : {liste(m['outils'])}", f"- Langues : {liste(m['langues'])}", "",
          "## Équipement", "", f"Équipé : {liste(inv['equipe'])}", ""]
    for o in inv["inventaire"]:
        meta = " · ".join(str(o[k]) for k in ("type", "rarete", "valeur", "masse", "poids") if k in o)
        L.append(f"- **{o['nom']}**" + (f" ({meta})" if meta else "") + f" : {o.get('description', '')}")
    mo = inv["monnaie"]
    L += ["", f"Monnaie : {mo['po']} po, {mo['pa']} pa, {mo['pc']} pc, {mo['pe']} pe, {mo['pp']} pp"
          + (f" ({mo['note']})" if mo.get("note") else ""), ""]
    if e["notes"]:
        L += ["## Règles à retenir", ""] + [f"- {n}" for n in e["notes"]] + [""]
    p = b["personnalite"]
    L += ["## Personnalité", ""] + [f"- **{nom(k)}** : {v}" for k, v in p.items()]
    s = camp["situation_actuelle"]
    L += ["", "## Situation actuelle", "",
          f"{camp['statut']}. Lieu : {s['lieu']}." + (f" {s['notes']}" if s.get("notes") else ""), "",
          "### Quêtes", ""] + [f"- {q}" for q in camp["quetes"]]
    L += ["", "### PNJ", ""]
    L += tableau(["Nom", "Rôle", "Statut"], [[x["nom"], x["role"], x["statut"]] for x in pnj["pnj"]])
    L += ["", "### Créatures", ""] + [f"- **{x['nom']}** ({x['statut']}) : {x['description']}" for x in pnj["creatures"]]
    return "\n".join(L).rstrip() + "\n"

if __name__ == "__main__":
    texte = generer()
    if "--check" in sys.argv:
        if not SORTIE.exists() or SORTIE.read_text(encoding="utf-8") != texte:
            sys.exit("fiche.md n'est pas à jour : lancer python3 scripts/generer_fiche.py")
        print("fiche.md à jour")
    else:
        SORTIE.write_text(texte, encoding="utf-8")
        print(f"{SORTIE.name} généré")
