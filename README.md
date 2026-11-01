# Barrevoudla

Fiche de personnage et journal de campagne de **Barrevoudla**, Barbare drakéide rouge (Magie sauvage), joué par Jérémie dans la campagne « Halloween sur l'île de Corvelune » (MJ : Nicolas Urban).

## Structure

```
personnage/
  base.json         données stables (identité, caractéristiques, maîtrises, traits)
  etat.json         données qui changent en jeu (PV, attaques, ressources, sorts)
  inventaire.json   équipement, objets magiques, monnaie
campagne/
  campagne.json     métadonnées (session en cours), quêtes, lieux, situation actuelle
  pnj.json          PNJ rencontrés et créatures
sessions/
  session-NN.md     récit de chaque session
scripts/
  generer_fiche.py  génère fiche.md (fiche lisible) depuis les JSON
  verifier.py       valide les JSON (schémas) et la cohérence des valeurs dérivées
schema/             JSON Schema de chaque fichier de données
.github/workflows/  GitHub Action qui lance verifier.py à chaque push et PR
```

`fiche.md` (à la racine) est la fiche lisible, **générée** : ne pas la modifier à la main.

## Règle d'or : une seule source de vérité

- Le **récit** d'une session vit uniquement dans `sessions/session-NN.md`.
- Les **faits persistants** (statut d'un PNJ, lieux, quêtes) vivent dans `campagne/`.
- Ne pas recopier l'un dans l'autre : le récit renvoie vers les fiches, pas l'inverse.

## Mettre à jour après une session

1. Créer `sessions/session-NN.md` (copier le précédent comme modèle).
2. Mettre à jour `campagne/campagne.json` (`session`, `date_maj`, `statut`, `situation_actuelle`) et `campagne/pnj.json`.
3. Mettre à jour `personnage/etat.json` (PV, ressources) et `inventaire.json`.
4. Lancer `pip install jsonschema && python3 scripts/verifier.py`, puis `python3 scripts/generer_fiche.py` pour régénérer `fiche.md`, et committer le tout (la CI vérifie les deux).

## Montée de niveau

Modifier `niveau`, puis recalculer à la main `bonus_maitrise`, les bonus de jets de sauvegarde, `pv_max` et les ressources ; `verifier.py` signale les incohérences.
