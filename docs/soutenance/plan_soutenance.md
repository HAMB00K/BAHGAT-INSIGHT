# Plan détaillé de la soutenance — Bahgat Insight Platform

Soutenance de stage de fin d'études · INSA Hauts-de-France · 5A ICY
BEN SAID Nassim · Bahgat IT Expert (Dubaï) · 1er avril – 30 septembre 2026

Format cible : **20 minutes de présentation** (22 diapos) + démo optionnelle + questions.
Tous les chiffres ci-dessous proviennent de la dernière exécution du pipeline
(`logs/etl_report.json`, `logs/generation_manifest.json`, `powerbi/data/ML*.csv`, exécution du 04/08/2026).

Conventions du document :
- **Contenu diapo** = texte exact à placer sur la diapo (mots-clés, chiffres, libellés courts, jamais de phrases).
- **Visuel** = ce que tu fournis (capture, schéma, logo). Indication de structure uniquement, le style est à toi.
- Le **speech** est regroupé en partie B, diapo par diapo, avec un chrono indicatif.

---

# PARTIE A — CONTENU DES DIAPOS

## Diapo 1 — Titre (0:00)

**Contenu diapo**
- Surtitre : `Soutenance de stage de fin d'études · INSA Hauts-de-France · 5A ICY`
- Titre : `Bahgat Insight Platform`
- Sous-titre : `Plateforme de Business Intelligence pilotée par l'IA`
- `BEN SAID Nassim`
- `Bahgat IT Expert · Consulting & Arbitration · Dubaï`
- `1er avril – 30 septembre 2026 · stage à distance`
- `Tuteur entreprise : Ahmed BAHGAT` · `Tuteur école : Smail NIAR`

**Visuel** : logo INSA HdF + logo Bahgat IT Expert ; en fond, capture floutée/assombrie de la page Executive Overview (mode sombre).

---

## Diapo 2 — Sommaire (0:40)

**Contenu diapo** (6 blocs numérotés, une ligne chacun)
1. `Contexte & entreprise`
2. `Mission & démarche`
3. `Architecture & données`
4. `Machine learning`
5. `Restitution`
6. `Bilan & perspectives`

**Visuel** : frise horizontale ou 6 tuiles ; le bloc actif se surligne au fil de la présentation (rappel discret en haut de chaque diapo : "3 · Architecture & données").

---

## Diapo 3 — Bahgat IT Expert (1:10)

**Contenu diapo**
- Titre : `Bahgat IT Expert — conseil & arbitrage IT`
- 4 grands chiffres (tuiles) :
  - `30+` · `années d'expérience`
  - `4` · `pays · EAU, KSA, Bahreïn, Canada`
  - `6` · `pôles d'expertise`
  - `8+` · `secteurs clients`
- Liste courte des pôles : `Forensics` · `Cybersécurité` · `Infrastructure` · `Arbitrage & expertise judiciaire` · `IA & Blockchain` · **`Data & Business Intelligence`** (à mettre en avant)
- Badge : `Certifié Ministère de la Justice des EAU`
- Encadré "Mon positionnement" :
  - `Practice Data & BI`
  - `100 % à distance depuis le Maroc · décalage ≈ 3 h`
  - `Point hebdo tuteur · démo à chaque jalon`

**Visuel** : logo du cabinet, photo des locaux (Deira, Dubaï) ou carte du Golfe avec les implantations.

---

## Diapo 4 — La problématique des clients (2:10)

**Contenu diapo**
- Titre : `Des données abondantes… peu exploitées`
- 5 cartes "douleur" (icône + 2-4 mots) :
  - `Silos` · `POS · CRM · ERP · marketing · web`
  - `Reporting manuel` · `tableurs · mensuel · en retard`
  - `Fiabilité incertaine` · `doublons · formats · incohérences`
  - `Zéro vision prospective` · `pas de prévision`
  - `Incidents détectés trop tard` · `prix · pannes · fraude`
- Bandeau bas : `Ambition du cabinet → une plateforme de référence, réutilisable de client en client`

**Visuel** : pictogrammes des 5 sources qui ne se parlent pas (silos), flèche vers une croix rouge "reporting mensuel".

---

## Diapo 5 — Mission & objectifs (3:00)

**Contenu diapo**
- Titre : `Ma mission : concevoir, développer, démontrer`
- 6 objectifs (verbe + complément court, sous forme de tuiles ou de chevrons) :
  1. `Collecter` · `7 familles de données multi-sources`
  2. `Fiabiliser` · `pipelines automatisés, audit complet`
  3. `Structurer` · `entrepôt en schéma en étoile`
  4. `Prédire` · `CA à 90 j · anomalies · segments`
  5. `Restituer` · `app web Flask + rapport Power BI`
  6. `Transférer` · `documentation pour les consultants`
- Rappel discret : `Cahier des charges établi avec le tuteur · mois 1`

**Visuel** : chaîne de 6 chevrons "de la donnée brute à la décision".

---

## Diapo 6 — La contrainte devenue atout (3:50)

**Contenu diapo**
- Titre : `Confidentialité → données synthétiques + vérité terrain`
- Colonne gauche "Contrainte" :
  - `Données clients sous NDA`
  - `Inutilisables en démo, rapport, soutenance`
- Flèche centrale
- Colonne droite "Stratégie" :
  - `Générateur haute-fidélité` · `retailer fictif Al Noor Retail Group`
  - `Incidents & défauts injectés à dates connues`
  - `Chaque brique évaluée objectivement`
  - `Pipeline agnostique de la source`
- Punchline (grand, en bas) : `« 7 / 7 incidents retrouvés »  >  « ça a l'air correct »`

**Visuel** : cadenas (gauche) → éprouvette / dés (droite) ; la punchline en typographie forte.

---

## Diapo 7 — Démarche & planning (4:40)

**Contenu diapo**
- Titre : `6 mois · 5 phases · une démo par jalon`
- Gantt simplifié (5 barres sur avril → septembre) :
  - `Cadrage & état de l'art` · `01/04 → 24/04`
  - `Données & entrepôt` · `27/04 → 29/05`
  - `Machine learning` · `01/06 → 24/07`
  - `Restitution & dashboards` · `06/07 → 28/08`
  - `Consolidation & soutenance` · `24/08 → 30/09`
- Légende : `◆ démo de fin de phase` · `point hebdomadaire tuteur`
- Note : `Chevauchement ML / restitution assumé`

**Visuel** : ton Gantt (`gantt_stage.xlsx` / `gant.png`) épuré, losanges aux jalons.

---

## Diapo 8 — Architecture (5:30)

**Contenu diapo**
- Titre : `Une architecture décisionnelle en 5 couches`
- 5 blocs de gauche à droite, 2-3 lignes chacun :
  1. `SOURCES` · `9 extractions CSV` · `POS · CRM · ERP · marketing · web`
  2. `INGESTION & QUALITÉ` · `dédoublonner · réparer · normaliser · quarantaine` · `journal d'audit`
  3. `ENTREPÔT` · `schéma en étoile SQLite` · `4 tables d'agrégats`
  4. `MACHINE LEARNING` · `prévision 90 j` · `anomalies` · `segmentation RFM`
  5. `RESTITUTION` · `app Flask · 6 pages` · `Power BI · 5 pages`
- Bandeau : `run_pipeline.py → chaîne complète ≈ 1 min · reproductible (seed 42)`
- Ligne fine : `Trajectoire production : Airflow / ADF · PostgreSQL / Synapse · conteneur + SSO · Power BI Service`

**Visuel** : ton schéma `Schema-archi.png`, flèches animées d'apparition couche par couche.

---

## Diapo 9 — Le jeu de données (6:30)

**Contenu diapo**
- Titre : `Réaliste, riche… et instrumenté`
- Bandeau de 6 chiffres :
  - `1,03 M` · `lignes de vente`
  - `3 ans` · `07/2023 → 06/2026`
  - `18` · `magasins · 16 physiques + 2 online`
  - `3` · `pays · EAU · KSA · Bahreïn`
  - `320` · `produits · 8 catégories`
  - `40 000` · `clients fidélité`
- Colonne "Réalisme du signal" :
  - `Saisonnalité hebdo + annuelle` · `Ramadan · Aïd · DSF · White Friday · rentrée`
  - `Croissance : +9 %/an magasins · +27 %/an e-commerce`
  - `Promotions corrélées aux événements`
  - `Popularité produit ∝ 1/prix (Zipf)`
  - `Clients hétérogènes (log-normale)`
- Colonne "Vérité terrain injectée" :
  - `8 incidents opérationnels datés`
  - `6 familles de défauts qualité`
  - `Tout est daté et quantifié`

**Visuel** : courbe de CA quotidien sur 3 ans avec les pics saisonniers annotés (capture de l'Overview 365 j ou du graphe Sales mensuel).

---

## Diapo 10 — Entrepôt : schéma en étoile (7:20)

**Contenu diapo**
- Titre : `Modélisation Kimball : faits, dimensions, agrégats`
- Étiquettes autour du schéma :
  - `5 dimensions` · `date · store · product · customer · supplier`
  - `5 faits` · `sales (1 M lignes) · returns · marketing · web · inventory`
  - `4 agrégats` · `KPIs quotidiens · par magasin · par catégorie · retours`
  - `Sorties ML réinjectées` · `forecast · anomalies · segments`
- Chiffre isolé : `< 100 ms` · `par requête dashboard`
- Chiffre isolé : `1,33 M` · `lignes chargées`

**Visuel** : ton `schema_etoile.png` en pleine largeur, les étiquettes en périphérie.

---

## Diapo 11 — ETL & qualité des données (8:00)

**Contenu diapo**
- Titre : `Fiabiliser, tracer, charger`
- Tableau 3 colonnes (Défaut · Lignes · Action) :
  - `Doublons de transactions` · `2 573` · `supprimés`
  - `Dates JJ/MM/AAAA` · `61 712` · `normalisées ISO`
  - `ID client manquant` · `252 978` · `NULL explicite (invité)`
  - `Libellés paiement` · `41 128` · `normalisés`
  - `Prix nuls` · `150` · `réparés via référentiel`
  - `Quantités négatives` · `180` · `quarantaine`
  - `Casse des villes` · `1 600` · `normalisée`
  - `E-mails dupliqués` · `60` · `flag revue`
  - `Retours orphelins` · `5` · `quarantaine`
- 3 chiffres en colonne droite :
  - `≈ 360 k` · `décisions qualité journalisées`
  - `22 s` · `Extract 2,4 · Transform 6,3 · Load 13,6`
  - `1 032 070 → 1 029 317` · `lignes de vente in / out`
- Principe : `Rien n'est supprimé en silence · table dq_log`

**Visuel** : capture de la page Data Pipeline (rapport de fiabilisation) ou de la console ETL.

---

## Diapo 12 — Prévision du CA (9:00)

**Contenu diapo**
- Titre : `Champion vs challenger, départagés par backtest`
- Deux cartes face à face :
  - `Holt-Winters` · `statistique` · `niveau · tendance amortie · saison hebdo (m = 7)`
  - `Gradient Boosting` · `ML` · `calendrier (Ramadan, événements) + retards J-1/7/14/28` · `prévision récursive`
- Protocole : `Holdout 60 j jamais vu` · `Métrique : MAPE`
- Tableau résultat :
  - `Holt-Winters` · `MAPE 8,55 %` · `RMSE 33 149 AED` · `🏆 Champion`
  - `Gradient Boosting` · `MAPE 10,37 %` · `RMSE 43 871 AED` · `Challenger`
- Sortie : `Prévision 90 j` · `IC 95 % s'élargissant avec l'horizon` · `+ 8 prévisions par catégorie (MAPE 10 – 24 %)`

**Visuel** : capture de la page Forecasting (courbe + bande d'intervalle) ; le tableau "Model tournament" à côté.

---

## Diapo 13 — Détection d'anomalies (10:00)

**Contenu diapo**
- Titre : `Deux détecteurs, deux échelles`
- Carte 1 : `Isolation Forest` · `multivarié · niveau entreprise`
  - `Vecteur journalier : CA · commandes · panier · remise · marge · remboursements`
  - `Détecte les combinaisons anormales`
  - `Contamination 1,5 % · 300 arbres`
- Carte 2 : `Z-score robuste` · `univarié · par magasin`
  - `Référence même-jour-de-semaine (8 occurrences)`
  - `Plancher de variance · règle de sauvegarde`
  - `Même logique sur les retours → fraude`
- Exemple clé (encadré) : `Bug de prix 03/09/2025 · CA normal · marge effondrée · invisible en univarié`
- `4 niveaux de sévérité` · `Low → Critical`

**Visuel** : capture de la chronologie des anomalies (points rouges sur la courbe de CA).

---

## Diapo 14 — Validation contre la vérité terrain (10:50)

**Contenu diapo**
- Titre : `7 / 7 incidents retrouvés`
- Tableau (Incident · Date · Périmètre · Détecté par) :
  - `Panne POS` · `14/05/2024` · `Deira City Centre` · `z-score`
  - `Coupure électrique` · `17/09/2024` · `Riyadh Park` · `z-score`
  - `Inondation entrepôt` · `10–12/02/2025` · `2 magasins Sharjah` · `z-score`
  - `Méga vente flash` · `15/06/2025` · `tous magasins` · `IF + z-score`
  - `Bug de prix −50 %` · `03/09/2025` · `tous magasins` · `IF + z-score`
  - `Pic White Friday` · `28–29/11/2025` · `2 sites online` · `IF + z-score`
  - `Fraude aux retours` · `08–14/01/2026` · `Sahara Centre` · `IF + z-score`
- Lecture : `Incidents locaux → z-score magasin` · `Incidents systémiques → Isolation Forest`
- Grand chiffre : `100 %` · `rappel · volume d'alertes maîtrisé`

**Visuel** : capture de la carte "Validation" de la page Anomalies, coches vertes.

---

## Diapo 15 — Leçon d'ingénierie (11:40)

**Contenu diapo**
- Titre : `Quand un détecteur "correct" échoue`
- Frise en 3 étapes :
  - `SYMPTÔME` · `−75 % de CA non détecté` · `> 1 000 fausses alertes`
  - `DIAGNOSTIC` · `requêtes directes dans l'entrepôt` · `saisonnalité hebdo gonfle l'écart-type` · `queues lourdes : 1 vente = 20 % du CA du jour`
  - `CORRECTION` · `baseline même-jour-de-semaine` · `générateur : popularité ↓ avec le prix` · `règle de sauvegarde · plancher de variance`
- Bandeau : `Hypothèse → mesure → diagnostic → correction`

**Visuel** : avant / après : deux mini-graphes (série avec fenêtre glissante brute vs référence même-jour-de-semaine) ou l'extrait de code de 6 lignes (annexe du rapport).

---

## Diapo 16 — Segmentation client (12:30)

**Contenu diapo**
- Titre : `RFM + KMeans → 5 segments actionnables`
- Méthode (ligne de chevrons) : `Récence · Fréquence · Montant` → `log + standardisation` → `KMeans k = 5` → `étiquetage auto des centroïdes`
- Tableau (Segment · Clients · Part du CA · Risque churn moyen) :
  - `Champions` · `5 130` · `45,5 %` · `0,04`
  - `Loyal Customers` · `9 581` · `34,1 %` · `0,36`
  - `Promising Mid-Tier` · `4 656` · `6,3 %` · `0,04`
  - `Slipping Away` · `11 271` · `12,9 %` · `0,77`
  - `Hibernating` · `6 461` · `1,2 %` · `0,89`
- Chiffre clé : `14 % des clients → 45 % du CA`
- Scores individuels : `Churn : logistique, seuil 120 j` · `CLV annualisée, écrêtée P99`
- Livrable : `Churn watchlist` · `forte valeur × risque élevé · triée par CLV`

**Visuel** : donut des segments + capture de la watchlist (page Customers).

---

## Diapo 17 — Application web Flask (13:30)

**Contenu diapo**
- Titre : `6 pages, une API, < 100 ms`
- Liste des pages (icône + nom) : `Executive Overview` · `Sales Analytics` · `Forecasting` · `Anomaly Detection` · `Customer Intelligence` · `Data Pipeline`
- Caractéristiques :
  - `≈ 20 endpoints JSON` · `fenêtres 30 / 90 / 365 j`
  - `ApexCharts · JS natif · zéro framework lourd`
  - `Design system type shadcn/ui · mode sombre`
  - `Palette accessible · icône + libellé, jamais la couleur seule`

**Visuel** : montage de 2-3 captures (Overview clair, Overview sombre, Forecasting) en perspective.

---

## Diapo 18 — Rapport Power BI (14:20)

**Contenu diapo**
- Titre : `Même entrepôt, second canal de restitution`
- 3 colonnes :
  - `Modèle sémantique` · `19 tables · 16 relations` · `table de dates marquée · clés masquées`
  - `Bibliothèque DAX` · `36 mesures` · `ventes · retours · time intelligence (YoY, cumuls) · marketing · ML`
  - `Rapport` · `5 pages` · `thème JSON personnalisé` · `slicers synchronisés` · `format projet PBIP`
- Bandeau : `18 CSV exportés automatiquement par le pipeline`

**Visuel** : capture de la vue Modèle (`star.png`) + capture d'une page (`pbi1.png` ou `pbi3.png`).

---

## Diapo 19 — Démonstration (15:00)

**Contenu diapo**
- Titre : `Démonstration`
- 4 étapes numérotées :
  1. `Pipeline en direct` · `--only etl`
  2. `Executive Overview` · `mode sombre`
  3. `Forecast → Anomalies → validation`
  4. `Power BI` · `slicer · même modèle`

**Visuel** : diapo sobre, sert de transition vers l'écran de démo. (Si pas de démo live : remplacer par une vidéo de 60-90 s enregistrée.)

---

## Diapo 20 — Résultats mesurés (17:00)

**Contenu diapo**
- Titre : `Ce que la plateforme délivre`
- 6 grandes tuiles chiffrées :
  - `1,3 M` · `lignes ingérées par exécution`
  - `≈ 360 k` · `décisions qualité journalisées`
  - `8,55 %` · `MAPE prévision · backtest 60 j`
  - `7 / 7` · `incidents retrouvés · rappel 100 %`
  - `5` · `segments + churn watchlist`
  - `≈ 1 min` · `chaîne complète · reproductible`
- Encadré "Pour le cabinet" :
  - `Démonstrateur commercial sans donnée réelle`
  - `Base de code source-agnostique`
  - `Bibliothèque DAX + design system réutilisables`

**Visuel** : tuiles uniquement, pas d'image.

---

## Diapo 21 — Compétences & enseignements (17:50)

**Contenu diapo**
- Titre : `Ce que ce stage m'a appris`
- Colonne "Techniques" :
  - `Modélisation Kimball · pipelines ETL audités`
  - `Séries temporelles · backtest sans fuite`
  - `Détection d'anomalies validée par vérité terrain`
  - `Full-stack : API Flask · front JS · accessibilité`
  - `Power BI · DAX · modèle sémantique`
- Colonne "Humaines" :
  - `Projet de 6 mois en autonomie, du cadrage à la livraison`
  - `Vulgariser le ML pour des décideurs`
  - `Travail à distance, contexte international, anglais quotidien`
- Bandeau "À approfondir" : `Orchestration (Airflow) · MLOps · prévision multivariée`

**Visuel** : deux colonnes + pictos.

---

## Diapo 22 — Limites & perspectives (18:40)

**Contenu diapo**
- Titre : `Limites assumées, feuille de route tracée`
- Deux colonnes en vis-à-vis (limite → perspective) :
  - `SQLite local · app sans auth` → `PostgreSQL / Synapse · conteneur + SSO`
  - `Prévision univariée` → `Covariables promo / marketing · SARIMAX, LightGBM`
  - `Churn heuristique` → `Modèle supervisé dès labels réels · suivi de dérive`
  - `Pas de retour analyste` → `Confirmer / rejeter les alertes → seuils adaptatifs`
  - `Refresh Power BI manuel` → `Power BI Service · gateway · row-level security`

**Visuel** : flèches limite → perspective, code couleur orange → vert.

---

## Diapo 23 — Conclusion & merci (19:30)

**Contenu diapo**
- `De la donnée brute à la décision, de bout en bout`
- 3 mots-clés : `Mesurer` · `Diagnostiquer` · `Rendre intelligible`
- `Merci de votre attention`
- `Place à vos questions`
- Pied : `BEN SAID Nassim · nassimb.bensaid@gmail.com` · logos INSA HdF + Bahgat IT Expert

**Visuel** : même fond que la diapo 1 pour boucler.

---

## Diapos de réserve (après la diapo "Merci", pour les questions)

- **R1 — Formules** : équations Holt-Winters (ℓ, b, s), MAPE, courbe logistique churn.
- **R2 — Extrait de code z-score** : les 8 lignes de `anomaly_detection.py` (annexe du rapport).
- **R3 — Modèle Power BI** : vue Modèle complète + 4 mesures DAX de time intelligence.
- **R4 — Trajectoire production** : tableau local → production (CSV → Blob · run_pipeline → Airflow/ADF · SQLite → Synapse · Flask → conteneur SSO · Desktop → Service).
- **R5 — Dictionnaire de données** : tes 3 images `dico_*.png`.
- **R6 — Pages complémentaires** : Sales Analytics (app + Power BI), Anomalies Power BI, Customers Power BI.

---
---

# PARTIE B — SPEECH

Chrono indicatif pour 20 minutes. Débit normal ≈ 130 mots/min. Les passages entre crochets sont des indications de geste ou de clic, pas du texte à dire.

## Diapo 1 — Titre (0:00 → 0:40)

Bonjour à toutes et à tous, et merci d'être présents. Je m'appelle Nassim Ben Said, élève-ingénieur en cinquième année ICY à l'INSA Hauts-de-France. Je vais vous présenter mon projet de fin d'études, réalisé pendant six mois, du 1er avril au 30 septembre 2026, au sein du cabinet Bahgat IT Expert, basé à Dubaï.

Ce projet, c'est la conception et le développement complet d'une plateforme de Business Intelligence pilotée par l'intelligence artificielle, baptisée Bahgat Insight Platform. Je remercie mon tuteur entreprise, M. Ahmed Bahgat, et mon tuteur académique, M. Smail Niar, pour leur accompagnement.

## Diapo 2 — Sommaire (0:40 → 1:10)

Ma présentation suit la logique du projet en six temps. D'abord le contexte : le cabinet et le problème que rencontrent ses clients. Ensuite ma mission et la démarche adoptée, avec un point important sur la confidentialité des données. Puis le cœur technique en deux blocs : l'architecture et les données, et les trois modules de machine learning. Je terminerai par la restitution, avec une courte démonstration, puis le bilan et les perspectives.

## Diapo 3 — Bahgat IT Expert (1:10 → 2:10)

Bahgat IT Expert est un cabinet de conseil et d'arbitrage spécialisé dans les technologies de l'information. Son siège est à Dubaï, avec des bureaux en Arabie Saoudite, à Bahreïn et au Canada. Il a plus de trente ans d'expérience et une particularité : il est certifié auprès du Ministère de la Justice des Émirats, ce qui le place à la croisée de l'expertise technique et de l'expertise judiciaire.

Ses activités couvrent six pôles : l'investigation numérique, la cybersécurité, l'infrastructure, l'arbitrage, l'IA et la blockchain, et la practice Data et Business Intelligence, dans laquelle j'ai effectué mon stage. Cette practice construit des tableaux de bord décisionnels pour des clients du retail, de la finance, de l'hôtellerie ou de l'énergie.

Une précision sur l'organisation : le stage s'est déroulé intégralement à distance depuis le Maroc, avec un décalage horaire d'environ trois heures, un point hebdomadaire avec mon tuteur et une démonstration à chaque jalon. Cela a beaucoup pesé sur ma façon de travailler, j'y reviendrai dans le bilan.

## Diapo 4 — La problématique (2:10 → 3:00)

Pourquoi ce projet ? Les clients de la practice partagent un constat : ils ont énormément de données, mais elles sont peu exploitées. Elles vivent dans des silos, le point de vente, le CRM, l'ERP, les plateformes marketing, l'analytics web, et rien ne les consolide.

Le reporting repose sur des extractions manuelles dans des tableurs, produites chaque mois, souvent avec des semaines de retard. Ces consolidations manuelles introduisent des doublons et des erreurs. Il n'y a aucune vision prospective : personne ne dispose d'une prévision structurée pour piloter les achats. Et les incidents, une erreur de prix, une panne en magasin, une fraude aux retours, ne sont découverts qu'au moment du reporting.

Face à cela, le cabinet ne veut plus reconstruire un tableau de bord ad hoc à chaque mission. Il veut une plateforme de référence, réutilisable de client en client. C'est l'ambition dans laquelle s'inscrit mon projet.

## Diapo 5 — Mission & objectifs (3:00 → 3:50)

Le cahier des charges, établi avec mon tuteur durant le premier mois, fixe six objectifs qui suivent la chaîne de valeur de la donnée.

Collecter des données de sept familles différentes : ventes, retours, clients, produits, stocks, marketing et web. Fiabiliser ces données avec des pipelines automatisés et une traçabilité complète de chaque correction. Structurer un entrepôt performant, en schéma en étoile. Prédire, avec trois modules de machine learning : le chiffre d'affaires à 90 jours, les anomalies opérationnelles et la segmentation client. Restituer dans deux couches complémentaires : une application web moderne et un rapport Power BI. Et enfin transférer, c'est-à-dire documenter l'ensemble pour que les consultants du cabinet puissent reprendre le projet.

## Diapo 6 — La contrainte devenue atout (3:50 → 4:40)

Avant d'entrer dans la technique, un point de méthode qui structure tout le projet. Les données des clients du cabinet sont sous accord de confidentialité strict. Impossible de les utiliser pour une démonstration, encore moins de les montrer ici.

Plutôt que de subir cette contrainte, j'en ai fait un atout. J'ai développé un générateur de données synthétiques haute-fidélité qui simule trois ans d'activité d'un distributeur omnicanal du Golfe, un client fictif que j'ai appelé Al Noor Retail Group.

Le point décisif, c'est que dans ces données, j'ai volontairement injecté des incidents opérationnels et des défauts de qualité, à des dates et des ampleurs que je connais. J'ai donc une vérité terrain. Chaque brique de la plateforme peut être évaluée objectivement : le pipeline a-t-il corrigé tous les défauts ? Le détecteur a-t-il retrouvé tous les incidents ? Dire "sept incidents sur sept retrouvés" vaut beaucoup plus que dire "ça a l'air correct". Et le pipeline reste agnostique de la source : on branche les extractions réelles d'un client, rien ne change en aval.

## Diapo 7 — Démarche & planning (4:40 → 5:30)

Le projet a été conduit en cinq phases sur six mois, selon une démarche itérative. Un mois de cadrage : découverte du cabinet, état de l'art BI et machine learning, cahier des charges et maquettes. Un mois sur les données : le générateur, la modélisation en étoile et le pipeline ETL. Presque deux mois de machine learning, de juin à fin juillet, pour la prévision, les anomalies et la segmentation, avec leurs validations. La restitution a démarré en chevauchement dès juillet, parce que les dashboards ont besoin des sorties ML pour être testés. Et le dernier mois a été consacré aux tests de bout en bout, à la documentation et à la préparation de cette soutenance.

Chaque fin de phase a donné lieu à une démonstration à mon tuteur, ce qui a permis de réajuster le périmètre régulièrement.

## Diapo 8 — Architecture (5:30 → 6:30)

Voici l'architecture, à lire de gauche à droite. [désigner chaque couche]

Les sources : neuf extractions CSV qui simulent les systèmes d'un retailer, point de vente, CRM, ERP, marketing et web. La couche d'ingestion et de qualité : elle dédoublonne, répare, normalise, met en quarantaine ce qui ne peut pas être corrigé, et journalise chaque action. L'entrepôt : un schéma en étoile dans SQLite, complété de tables d'agrégats pré-calculées. Le machine learning : trois modules qui lisent l'entrepôt et y réinscrivent leurs résultats. Et la restitution : une application web Flask de six pages, et un rapport Power BI de cinq pages, tous deux branchés sur le même entrepôt.

L'ensemble est orchestré par un script unique qui rejoue la chaîne complète en une minute environ, de façon reproductible grâce à une graine aléatoire fixée. Et j'ai documenté la trajectoire vers la production : orchestrateur Airflow ou Data Factory, entrepôt PostgreSQL ou Synapse, application conteneurisée, Power BI Service. Chaque brique se remplace sans toucher aux autres.

## Diapo 9 — Le jeu de données (6:30 → 7:20)

Quelques chiffres sur le jeu de données. Un peu plus d'un million de lignes de vente sur trois ans, de juillet 2023 à juin 2026. Dix-huit magasins, dont deux sites e-commerce, dans trois pays du Golfe. 320 produits en huit catégories, 40 000 clients fidélité.

Le réalisme repose sur la superposition de plusieurs couches de signal, calibrées sur le retail du Golfe. Une saisonnalité hebdomadaire, avec les pics du week-end, et annuelle : Ramadan et Aïd, dont les dates se décalent chaque année, le Dubai Shopping Festival, le White Friday, la rentrée. Une croissance différenciée : neuf pour cent par an en magasin, vingt-sept pour cent en ligne. Des promotions corrélées aux événements. Une popularité produit qui décroît avec le prix, ce qui est une propriété importante sur laquelle je reviendrai. Et des comportements clients hétérogènes, condition pour obtenir une segmentation qui a du sens.

À cela s'ajoute la vérité terrain : huit incidents opérationnels datés, et six familles de défauts de qualité de données.

## Diapo 10 — Schéma en étoile (7:20 → 8:00)

L'entrepôt suit la modélisation dimensionnelle de Kimball. Les mesures, montants et quantités, vivent dans cinq tables de faits ; la table des ventes fait un million de lignes, au grain de la ligne de ticket. Les axes d'analyse vivent dans cinq dimensions partagées : le calendrier enrichi avec les week-ends, le Ramadan et les événements commerciaux, les magasins, les produits, les clients et les fournisseurs.

Quatre tables d'agrégats pré-calculées, par jour, par magasin, par catégorie, garantissent des temps de réponse inférieurs à cent millisecondes sur les dashboards. C'est le même principe qu'une vue matérialisée en production. Enfin, les sorties du machine learning sont réinjectées dans l'entrepôt, si bien que les deux couches de restitution partagent exactement le même modèle sémantique.

## Diapo 11 — ETL & qualité (8:00 → 9:00)

Le pipeline ETL enchaîne extraction, transformation et chargement, chaque étape étant instrumentée. Voici le bilan réel d'une exécution.

Les fichiers sont lus en typage chaîne strict, pour qu'aucune conversion implicite ne masque un défaut. Ensuite, chaque défaut déclenche une action adaptée. 2 573 doublons d'export supprimés. 61 712 dates au format jour-mois-année normalisées en ISO. 253 000 identifiants client manquants convertis en NULL explicite, ce sont des achats invités. 41 000 libellés de paiement normalisés. 150 prix nuls réparés depuis le référentiel produit. Et ce qui ne peut pas être réparé, quantités négatives, retours orphelins, part en quarantaine.

Au total, environ 360 000 décisions de qualité, toutes journalisées dans une table d'audit. Rien n'est supprimé en silence. Et tout cela s'exécute en 22 secondes. Pour un consultant, ce tableau est aussi un livrable : c'est le rapport de fiabilisation qu'on présente au client.

## Diapo 12 — Prévision (9:00 → 10:00)

Premier module de machine learning : la prévision du chiffre d'affaires quotidien à 90 jours. J'ai adopté une démarche champion contre challenger.

Le champion statistique est Holt-Winters, un lissage exponentiel triple qui modélise le niveau, une tendance amortie et la saisonnalité hebdomadaire. Le challenger est un Gradient Boosting entraîné sur des variables calendaires, jour de semaine, Ramadan, événements, et sur des retards de la série, avec une prévision récursive multi-pas.

Les deux sont évalués sur un holdout de 60 jours jamais vu à l'entraînement, avec la MAPE comme métrique. Résultat : Holt-Winters l'emporte avec 8,55 % d'erreur contre 10,37 %. Ce n'est pas une surprise et je sais l'expliquer : sur une série à saisonnalité hebdomadaire forte et stable, les méthodes de lissage restent très compétitives, pour un coût de calcul et une interprétabilité bien meilleurs. Le champion produit la prévision officielle à 90 jours, avec un intervalle de confiance à 95 % qui s'élargit avec l'horizon, complétée de huit prévisions par catégorie.

## Diapo 13 — Détection d'anomalies (10:00 → 10:50)

Deuxième module : la détection d'anomalies, avec deux détecteurs complémentaires qui travaillent à deux échelles.

Au niveau de l'entreprise, un Isolation Forest multivarié. Chaque journée est décrite par un vecteur de KPIs : chiffre d'affaires, commandes, panier moyen, taux de remise, taux de marge, remboursements. L'algorithme isole les journées atypiques dans leur combinaison d'indicateurs. L'exemple parfait, c'est le bug de prix du 3 septembre 2025 : le chiffre d'affaires était normal, mais la marge s'était effondrée. Un contrôle univarié ne le voit pas, l'Isolation Forest le voit.

Au niveau de chaque magasin, un z-score robuste : le chiffre d'affaires est comparé à une référence des huit dernières occurrences du même jour de semaine, avec un plancher de variance et une règle de sauvegarde sur les effondrements massifs. La même logique s'applique aux retours pour détecter les abus de remboursement. Chaque alerte reçoit un niveau de sévérité pour permettre le tri par les équipes.

## Diapo 14 — Validation (10:50 → 11:40)

Voici la validation contre la vérité terrain. Sept incidents de ventes et de retours ont été injectés : deux pannes locales, une inondation sur deux magasins, une méga vente flash, le bug de prix, le pic e-commerce du White Friday et une semaine de fraude aux retours.

Les détecteurs combinés retrouvent les sept, soit un rappel de cent pour cent, avec un volume d'alertes maîtrisé. Et la granularité de la vérité terrain permet d'attribuer chaque détection à la bonne méthode : les incidents localisés, panne et inondation, sont capturés par le z-score magasin ; les incidents systémiques, vente flash et bug de prix, par l'Isolation Forest. Chaque détecteur fait exactement le travail pour lequel il a été conçu.

## Diapo 15 — Leçon d'ingénierie (11:40 → 12:30)

Ce résultat n'a pas été obtenu du premier coup, et c'est l'épisode le plus formateur du stage.

La première version du détecteur magasin comparait chaque journée à la moyenne et à l'écart-type des 28 jours précédents. Statistiquement correct. Pourtant, il manquait des effondrements de moins 75 % de chiffre d'affaires, tout en levant plus de mille fausses alertes.

Le diagnostic, mené en interrogeant directement l'entrepôt, a révélé deux causes. D'abord, la saisonnalité hebdomadaire gonflait l'écart-type : les week-ends côtoyaient les jours creux dans la même fenêtre. Ensuite, la distribution à queue lourde des ventes : un article à 10 000 dirhams pouvait être le plus vendu de sa catégorie, si bien qu'une seule vente faisait varier de 20 % le chiffre d'affaires du jour.

La correction a été double : comparer chaque jour à ses homologues du même jour de semaine, et rendre le générateur plus réaliste, avec une popularité qui décroît avec le prix, comme dans le retail réel. Plus des garde-fous sur l'ampleur relative de l'écart. La leçon : un détecteur juste sur le papier peut échouer sur des données réalistes, et seule une vérité terrain permet de s'en apercevoir.

## Diapo 16 — Segmentation (12:30 → 13:30)

Troisième module : la segmentation client. Elle repose sur l'analyse RFM des 37 000 clients actifs : récence du dernier achat, fréquence des commandes, montant cumulé. Après transformation logarithmique, les distributions étant très asymétriques, et standardisation, un KMeans en cinq groupes est appliqué. Chaque groupe est étiqueté automatiquement à partir de son centroïde.

On retrouve une structure conforme aux régularités du retail : les Champions représentent 14 % des clients et concentrent 45 % du chiffre d'affaires. À l'autre extrémité, les clients en hibernation ont un risque d'attrition de 0,89.

Deux scores individuels complètent la segmentation : un risque d'attrition par courbe logistique centrée sur 120 jours d'inactivité, et une valeur client annualisée. Leur croisement produit le livrable le plus directement actionnable de la plateforme : une liste de surveillance des clients à forte valeur et à risque élevé, triée par valeur. Le marketing reçoit une campagne de rétention prête à lancer.

## Diapo 17 — Application web (13:30 → 14:20)

Passons à la restitution. La première couche est une application web Flask de six pages : vue exécutive avec KPIs et variations, analyse des ventes, prévision, anomalies, intelligence client, et une page de transparence sur le pipeline lui-même.

L'architecture est volontairement simple : une vingtaine d'endpoints JSON qui interrogent l'entrepôt sur des fenêtres de 30, 90 ou 365 jours, et des graphiques construits côté navigateur. Aucun framework front-end lourd, ce qui simplifie le déploiement chez un client.

J'ai porté une attention particulière au design : un design system sobre inspiré de shadcn, un mode sombre, et une palette de graphiques validée pour l'accessibilité. Les niveaux de sévérité associent toujours une icône et un libellé à la couleur, pour que l'information ne repose jamais sur la couleur seule.

## Diapo 18 — Power BI (14:20 → 15:00)

La seconde couche s'adresse à l'écosystème Microsoft, standard chez les clients du cabinet. Le pipeline exporte automatiquement dix-huit fichiers CSV propres, et le rapport Power BI est construit dessus.

Trois volets de travail. Le modèle sémantique : dix-neuf tables, seize relations, une table de dates marquée, les clés techniques masquées. Une bibliothèque de trente-six mesures DAX organisée par thème, avec de la time intelligence, comparaisons année sur année et cumuls, et des mesures issues du ML. Cette bibliothèque est réutilisable telle quelle sur des données réelles. Et cinq pages de rapport qui reprennent la logique de l'application, avec un thème personnalisé aux couleurs de la plateforme. Le tout est livré au format projet Power BI, donc versionnable.

## Diapo 19 — Démonstration (15:00 → 17:00)

[Basculer sur l'écran de démo. Version courte, 2 minutes.]

Je vous propose de voir la plateforme en fonctionnement.

[Terminal] Je relance uniquement l'étape ETL : vous voyez défiler le journal de fiabilisation, les doublons supprimés, les prix réparés, en une vingtaine de secondes.

[Overview] Voici la vue exécutive : les KPIs avec leur variation, la tendance du chiffre d'affaires sur laquelle on distingue le Ramadan et le Dubai Shopping Festival. Je bascule en mode sombre.

[Forecasting] La prévision à 90 jours avec son intervalle, et le tournoi de modèles.

[Anomalies] La chronologie avec les journées signalées, et la carte de validation : sept sur sept.

[Power BI] Le même entrepôt vu dans Power BI : je filtre sur un pays, tout le rapport se met à jour.

[Revenir aux diapos.]

## Diapo 20 — Résultats (17:00 → 17:50)

Pour résumer ce que la plateforme délivre à chaque exécution. 1,3 million de lignes ingérées, dont un million de lignes de ventes fiabilisées. 360 000 décisions de qualité journalisées. Une prévision à 90 jours avec 8,55 % d'erreur en backtest. Cent pour cent des incidents injectés retrouvés. Cinq segments clients et une liste de surveillance prête à l'emploi. Le tout en une minute, reproductible à l'identique.

Pour le cabinet, c'est un démonstrateur commercial qu'on peut montrer à un prospect sans exposer la moindre donnée réelle, une base de code source-agnostique, et une bibliothèque DAX et un design system réutilisables sur les missions suivantes.

## Diapo 21 — Compétences (17:50 → 18:40)

Sur le plan technique, ce stage m'a fait couvrir toute la chaîne : la modélisation dimensionnelle et les pipelines audités, les séries temporelles et l'évaluation par backtest sans fuite de données, la détection d'anomalies validée par vérité terrain, le développement full-stack, et Power BI avec le langage DAX.

Sur le plan humain, j'ai conduit un projet de six mois en autonomie, du cadrage à la livraison. J'ai appris à vulgariser des choix de modèles et des métriques auprès de consultants non spécialistes, ce qui conditionne l'impact réel d'un projet data. Et le travail à distance dans un contexte international m'a imposé une communication écrite structurée et une documentation systématique.

J'ai aussi identifié mes axes de progression : l'orchestration à grande échelle, les architectures MLOps et la prévision multivariée.

## Diapo 22 — Limites & perspectives (18:40 → 19:30)

La plateforme est un démonstrateur et ses limites sont assumées ; elles dessinent sa feuille de route.

L'entrepôt SQLite et l'application sans authentification deviennent PostgreSQL ou Synapse et un conteneur derrière SSO. La prévision univariée s'enrichit de covariables, promotions et marketing, avec des modèles comme SARIMAX ou LightGBM. Le score de churn heuristique laisse place à un modèle supervisé dès que des étiquettes réelles existent. Une boucle de retour analyste, confirmer ou rejeter une alerte, permettra d'affiner les seuils. Et la publication sur Power BI Service automatise l'actualisation avec de la sécurité au niveau ligne. Chaque évolution a été documentée pour les équipes du cabinet.

## Diapo 23 — Conclusion (19:30 → 20:00)

Pour conclure, ce stage m'a permis de livrer une plateforme complète, de la donnée brute jusqu'à la décision. Mais au-delà de la réalisation, ce que je retiens, c'est une démarche d'ingénieur : mesurer plutôt que supposer, diagnostiquer jusque dans les données, et rendre les résultats intelligibles pour ceux qui décident. Cette expérience confirme mon projet professionnel dans l'ingénierie de la donnée et ses applications décisionnelles.

Je vous remercie pour votre attention et je suis à votre disposition pour vos questions.

---

# PARTIE C — RÉPONSES PRÉPARÉES AUX QUESTIONS PROBABLES

**Pourquoi des données synthétiques, ce n'est pas de la triche ?**
Confidentialité contractuelle. Le générateur conserve les propriétés difficiles du réel : saisonnalité, tendance, bruit, défauts. Il ajoute ce que le réel ne donne jamais : une vérité terrain. Le pipeline est agnostique de la source ; on branche les extractions réelles et rien ne change en aval.

**Pourquoi Holt-Winters plutôt que Prophet ou du deep learning ?**
Série journalière de 1 100 points, saisonnalité hebdomadaire forte : les méthodes classiques sont compétitives, s'entraînent en secondes et sont explicables. Le backtest a tranché, pas la mode. Avec plus de covariables, je testerais SARIMAX, Prophet ou LightGBM enrichi.

**Comment ça passe à l'échelle ?**
SQLite vers PostgreSQL ou Synapse = changement de chaîne de connexion, le SQL est portable. Orchestrateur vers Airflow ou Data Factory. Agrégats vers vues matérialisées. Power BI vers le Service avec actualisation planifiée. Le schéma en étoile est déjà la bonne forme.

**Comment limitez-vous les faux positifs ?**
Contamination plafonnée à 1,5 %, référence glissante strictement antérieure au jour évalué, plancher de variance, règle d'ampleur relative, alertes sur les retours seulement à la hausse, quatre niveaux de sévérité pour le tri. Prochaine étape : la boucle de retour analyste.

**Pourquoi KMeans et pourquoi k = 5 ?**
RFM est l'espace comportemental standard du retail ; après log-scaling, KMeans est rapide et interprétable. Cinq segments équilibrent distinction et actionnabilité : cinq campagnes différenciées. La graine fixée a permis de vérifier la stabilité des clusters ; une analyse silhouette est l'extension naturelle.

**Le churn est-il un vrai modèle ?**
Non, c'est un score heuristique fondé sur la récence, assumé comme tel. Un modèle supervisé exige des événements de churn étiquetés sur une fenêtre plus longue. Le score actuel est déjà utile pour prioriser une liste de rétention.

**Quelle a été la plus grosse difficulté ?**
Le détecteur d'anomalies aveuglé par la variance sur de petits échantillons : diagnostic dans l'entrepôt, correction du générateur et garde-fous. Plus généralement, garantir des évaluations honnêtes sans fuite de données.

**Sécurité et confidentialité ?**
Démo locale, aucune donnée personnelle réelle. En production : SSO, sécurité au niveau ligne dans Power BI, stockage chiffré.

**Pourquoi 8 incidents injectés et 7 validés ?**
Le huitième, la rupture de stock électronique, vit dans la table d'inventaire mensuelle et n'est pas du périmètre des détecteurs de ventes et retours. Il sert de piste d'extension : un détecteur de stock.

**Pourquoi deux front-ends ?**
Deux publics : l'application web pour la démonstration et les usages hors écosystème Microsoft ; Power BI parce que c'est l'outil attendu par les clients du cabinet. Un seul entrepôt, un seul modèle sémantique, deux consommations.

**Combien de temps pour brancher un vrai client ?**
Écrire les connecteurs d'extraction vers les neuf formats attendus ; tout le reste est inchangé. Le rapport de qualité de données devient un premier livrable d'audit pour le client.
