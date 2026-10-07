# Ouvrir le rapport Power BI (projet PBIP prêt à l'emploi)

Ce dossier contient un **projet Power BI complet** : le modèle sémantique
(19 tables, 16 relations, 36 mesures DAX) **et** un rapport de 5 pages avec
les visuels déjà construits. Vous n'avez rien à assembler.

## Prérequis

1. **Power BI Desktop récent** (version 2024 ou plus — téléchargeable via
   Microsoft Store). Si l'ouverture échoue sur une vieille version, activez :
   *Fichier > Options > Fonctionnalités en préversion > "Power BI Project
   (.pbip) save option"*, puis redémarrez.
2. **Les CSV doivent exister** : lancez `python run_pipeline.py` au moins une
   fois (ils sont dans `powerbi/data/`).

## Ouverture (3 étapes)

1. Double-cliquez sur **`BahgatInsight.pbip`** (ou Fichier > Ouvrir dans
   Power BI Desktop).
2. Cliquez sur **Actualiser** (Accueil > Actualiser). Les ~1,3M de lignes se
   chargent en 1 à 2 minutes.
3. C'est tout — les 5 pages se remplissent : Executive Overview, Sales
   Analytics, Forecast (ML), Anomalies (ML), Customers (ML).

## Si vous avez déplacé le projet

Le chemin des CSV est un **paramètre** : Accueil > Transformer les données >
Modifier les paramètres > `DataFolder` → mettez le chemin de votre dossier
`powerbi\data\` (avec le `\` final), puis Actualiser. Valeur par défaut :

```
C:\Users\BENSAID\Desktop\Internship project\powerbi\data\
```

## Finitions recommandées (2 minutes)

- **Thème** : Affichage > Thèmes > Rechercher des thèmes >
  `powerbi/BahgatTheme.json` (applique la charte de la plateforme).
- **Segments (slicers)** : ajoutez un slicer `DimDate[date]` et
  `DimStore[country]` sur la page Overview si vous voulez filtrer en live
  pendant la démo.
- **Top N produits** : sur le tableau des produits (page Sales), volet
  Filtres > `product_name` > Top N = 15 par `Net Revenue`.
- **Watchlist churn** : sur le tableau de la page Customers, volet Filtres >
  `churn_risk` > "supérieur ou égal à 0,5".
- Enregistrez ensuite sous **`.pbix`** (Fichier > Enregistrer sous) pour
  obtenir le fichier unique à montrer en soutenance.

## En cas d'erreur à l'ouverture

Notez le message exact et transmettez-le : le format projet est en texte, donc
tout est corrigeable rapidement. Les causes classiques : CSV absents (pipeline
pas encore exécuté) ou paramètre `DataFolder` incorrect.
