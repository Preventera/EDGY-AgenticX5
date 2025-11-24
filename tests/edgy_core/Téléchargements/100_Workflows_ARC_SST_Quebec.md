# 100 Workflows Opérationnels SST avec ARC (Agentic Risk Coordinator)
## Conformité Réglementaire Québécoise : LSST, LMRSST, CSTC, RSST

---

## **CATÉGORIE 1 : IDENTIFICATION ET ÉVALUATION DES RISQUES (15 workflows)**

| # | Nom du Workflow | Description Succincte | Amélioration ARC | Exemple Concret Réglementaire |
|---|---|---|---|---|
| 1 | Analyse préliminaire des risques (APR) | Identification systématique des dangers avant projet/nouveau procédé | Agent d'analyse croise historique incidents, génère matrice risques automatisée et mesures préventives | Chantier démolition (CSTC Art. 2.9) - ARC propose évaluations amiante/plomb selon RSST |
| 2 | Évaluation ergonomique postes travail | Analyse contraintes physiques/cognitives pour prévenir TMS | Collecte données biométriques IoT, analyse patterns mouvement, calculs efforts normes IRSST | Poste manutention - ARC détecte 73% soulèvements >23kg (limite RSST femmes), propose aides mécaniques |
| 3 | Cartographie dynamique zones à risque | Identification/délimitation zones dangereuses selon activités | Orchestrateur croise géolocalisation temps réel, activités, météo pour balisage automatique | Chantier multi-entrepreneurs - ARC ajuste périmètre soudure/solvants selon CSTC Art. 3.23 |
| 4 | Évaluation risques psychosociaux | Identification stress, harcèlement, surcharge affectant santé mentale | Agent analyse questionnaires adaptatifs, patterns absentéisme, corrélations organisationnelles | Secteur manufacturier - ARC corrèle quarts nuit/incidents, suggère évaluation charge travail |
| 5 | Analyse risques chimiques exposition | Évaluation exposition substances dangereuses selon SIMDUT 2015 | Agent conformité scanne FDS, calcule expositions cumulatives, génère stratégies échantillonnage IRSST | Atelier peinture - ARC calcule VEMP solvants selon RSST Annexe I |
| 6 | Évaluation risques incendie/explosion | Analyse sources ignition, matières combustibles, propagation potentielle | Agent modélise scénarios incendie, calcule charges calorifiques, propose systèmes suppression | Entrepôt produits chimiques - ARC classe zones ATEX selon RSST Art. 194-199 |
| 7 | Analyse vibrations exposition | Mesure/évaluation exposition vibrations mains-bras et corps entier | Capteurs IoT mesurent vibrations continues, calculent doses quotidiennes selon ISO 5349 | Opérateur marteau-piqueur - ARC suit exposition selon RSST Art. 206, alerte si >2.5 m/s² |
| 8 | Évaluation exposition bruit | Audiométrie et mesures sonométriques selon RSST Art. 131-144 | Réseau capteurs acoustiques, audiogrammes automatisés, calculs exposition LEX,8h | Atelier mécanique - ARC programme audiométrie si >85 dB(A), propose protections auditives |
| 9 | Analyse risques électriques | Identification dangers électrocution, arc électrique, incendie électrique | Agent analyse schémas électriques, calcule énergies incidentes, propose EPI arc flash | Installation 600V industrielle - ARC calcule cal/cm² selon NFPA 70E, spécifie EPI requis |
| 10 | Évaluation travail isolé | Analyse postes travail sans surveillance directe selon RSST Art. 50 | Système géolocalisation, détection homme mort, communication bidirectionnelle automatique | Technicien maintenance nuit - ARC active protocole surveillance toutes les 2h |
| 11 | Analyse risques machines dangereuses | Évaluation sécurité machines selon RSST Art. 173-193 | Agent analyse manuels machines, audite protecteurs, vérifie dispositifs sécurité | Presse hydraulique - ARC valide conformité protecteurs ISO 14119, dispositifs arrêt urgence |
| 12 | Évaluation risques hauteur | Analyse travaux >3m selon CSTC Section III | Calculs forces chute, résistance ancrages, facteurs sécurité équipements | Charpentier toiture - ARC calcule charges ancrages CSA Z259.10, spécifie systèmes protection |
| 13 | Analyse espaces clos | Identification/classification espaces confinés selon RSST Art. 297-310 | Agent évalue atmosphères, ventilation requise, procédures entrée/surveillance | Cuve stockage - ARC programme tests O2/LIE/H2S, calcule débits ventilation selon ACGIH |
| 14 | Évaluation risques excavation | Analyse stabilité sols, services souterrains, protection travailleurs | Données géotechniques, calculs pentes talus, systèmes étayage selon CSTC Art. 3.15 | Excavation 4m urbaine - ARC consulte Info-Excavation, propose blindage selon nature sol |
| 15 | Analyse manutention manuelle | Évaluation efforts, postures, fréquence selon guide IRSST | Capteurs biomécanique, analyse posturale vidéo, calculs indices sollicitation | Préparateur commandes - ARC mesure efforts lombaires, propose aides techniques |

---

## **CATÉGORIE 2 : GESTION DES PERMIS DE TRAVAIL (12 workflows)**

| # | Nom du Workflow | Description Succincte | Amélioration ARC | Exemple Concret Réglementaire |
|---|---|---|---|---|
| 16 | Permis travail espace clos | Autorisation interventions espaces confinés atmosphère dangereuse | Orchestrateur génère séquences tests, vérifie surveillants qualifiés, alerte dérives paramètres | Maintenance cuve (RSST Art. 297-310) - Tests O2/LIE/H2S automatiques, alerte si O2<19.5% |
| 17 | Permis travail à chaud | Autorisation soudage/découpage générateur chaleur/étincelles | Agent analyse proximité combustibles, météo, génère mesures préventives CSTC Art. 3.23 | Soudage raffinerie - ARC calcule dispersion étincelles selon vent, ajuste périmètre |
| 18 | Permis fouille/excavation | Autorisation travaux excavation avec analyse effondrement/services | Agent croise géotechnique, plans services, météo, calcule pentes talus CSTC Art. 3.15 | Excavation urbaine - ARC consulte Info-Excavation, propose étayage selon profondeur |
| 19 | Permis travail hauteur | Autorisation travaux >3m avec systèmes protection chute | Calculs ancrages, vérification équipements, validation formations selon CSTC Section III | Installation échafaudage - ARC vérifie certifications CSA, calcule charges admissibles |
| 20 | Permis travail électrique | Autorisation interventions équipements électriques sous tension | Cadenassage/étiquetage, mesures tension, EPI arc flash selon CSTC Art. 8.10 | Maintenance 25kV - ARC calcule énergie incidente, spécifie EPI classe protection |
| 21 | Permis entrée vaisseaux | Autorisation accès réservoirs, cuves, équipements confinés | Tests atmosphériques spécialisés, ventilation forcée, surveillance continue | Nettoyage réservoir essence - ARC programme tests benzène/vapeurs, ventilation explosion-proof |
| 22 | Permis levage critique | Autorisation manœuvres grues charges lourdes/complexes | Calculs capacités, plans levage, coordination signaleurs selon RSST Art. 255-282 | Levage 50T raffinerie - ARC valide plan levage, vérifie certifications grutier/signaleur |
| 23 | Permis démolition contrôlée | Autorisation démolition structures avec explosifs/techniques spéciales | Évaluation amiante/plomb, plans démolition, périmètres sécurité CSTC Art. 2.9 | Démolition immeuble centre-ville - ARC coordonne évaluations matières dangereuses |
| 24 | Permis travail radio-actif | Autorisation manipulation sources radioactives selon CCSN | Dosimétrie, zonage radiation, surveillance médicale spécialisée | Radiographie industrielle - ARC suit doses individuelles, alerte si >1mSv/mois |
| 25 | Permis maintenance équipement | Autorisation interventions machines production avec arrêt sécuritaire | Cadenassage multiénergies, validation isolation, procédures redémarrage | Maintenance presse 500T - ARC valide 7 points cadenassage selon RSST Art. 185-188 |
| 26 | Permis transport matières dangereuses | Autorisation circulation TMD selon Transport Canada | Classification ADR, placardage, formation conducteurs, itinéraires autorisés | Transport acide site industriel - ARC vérifie certifications TMD, route optimale |
| 27 | Permis travail proximité aéroport | Autorisation travaux zones contrôlées Transport Canada/NAV Canada | Coordination NOTAM, hauteurs maximales, balisage lumineux obligatoire | Grue proximité Trudeau - ARC coordonne avec NAV Canada, programme balisage |

---

## **CATÉGORIE 3 : FORMATION ET COMPÉTENCES SST (10 workflows)**

| # | Nom du Workflow | Description Succincte | Amélioration ARC | Exemple Concret Réglementaire |
|---|---|---|---|---|
| 28 | Formation CoSS 240h théorique | Parcours formation obligatoire coordonnateurs SST selon LMRSST | Agent formateur adapte contenu sectoriel, suit progrès, génère attestations CNESST | Formation CoSS construction - ARC personnalise modules CSTC selon spécialités |
| 29 | Formation accueil sécurité | Formation obligatoire nouveaux travailleurs avant affectation LSST Art. 51 | Génère programme personnalisé selon poste, suit progression, valide compétences | Nouvel électricien - ARC intègre risques site, procédures cadenassage, évalue connaissances |
| 30 | Formation SIMDUT/SGH | Formation classification/étiquetage substances chimiques | Base données FDS actualisées, quiz adaptatifs, suivi exposition individuelle | Laboratoire chimie - ARC met à jour formations selon nouvelles classifications GHS |
| 31 | Formation protection chute | Habilitation travail hauteur et utilisation EPI selon CSA Z259 | Simulateur virtuel, vérification équipements, certification périodique obligatoire | Couvreur - ARC simule scenarios chute, valide inspection harnais, certifie compétences |
| 32 | Formation cadenassage/étiquetage | Habilitation isolation énergies dangereuses selon RSST Art. 185-188 | Modules équipements spécifiques, procédures step-by-step, validation pratique | Mécanicien maintenance - ARC génère procédures machine par machine, teste connaissances |
| 33 | Formation premiers secours | Certification secourisme industriel selon norme CSA Z1210 | Simulations RCR, scénarios trauma, recyclage automatique selon expiration | Secouriste usine - ARC programme recyclage tous les 3 ans, simule urgences spécifiques |
| 34 | Formation conduite sécuritaire | Habilitation opération véhicules/équipements mobiles | Simulateurs, évaluation conduite, suivi infractions/incidents selon SAAQ | Cariste entrepôt - ARC évalue conduite virtuelle, programme recyclage selon incidents |
| 35 | Formation protection respiratoire | Ajustement/utilisation appareils respiratoires selon CSA Z94.4 | Tests ajustement quantitatifs, maintenance équipements, surveillance médicale | Sableur industriel - ARC programme fit-test annuel, suit durées exposition, alerte renouvellement |
| 36 | Formation manipulation amiante | Habilitation travaux amiante selon RSST Art. 3.23 | Modules décontamination, équipements protection, surveillance atmosphérique | Rénovation bâtiment pré-1980 - ARC valide formation 30h, vérifie équipements classe A |
| 37 | Formation gestion crise | Préparation intervention urgences selon plan mesures urgence | Simulations évacuation, communication crise, coordination services externes | Coordonnateur urgence - ARC simule scénarios multi-risques, évalue temps réaction |

---

## **CATÉGORIE 4 : GESTION D'INCIDENTS ET ENQUÊTES (10 workflows)**

| # | Nom du Workflow | Description Succincte | Amélioration ARC | Exemple Concret Réglementaire |
|---|---|---|---|---|
| 38 | Signalement incident immédiat | Processus signalement obligatoire accidents/incidents LSST Art. 62 | Collecte automatique données contextuelles, pré-remplit formulaires CNESST, notifications réglementaires | Chute hauteur - ARC capture conditions météo, état équipement, génère déclaration automatique |
| 39 | Enquête analyse causale | Investigation causes profondes selon méthode TRAP/arbre causes | Agent guide méthodologie TRAP, suggère témoins, génère arbre causes automatique | Incident manipulation - ARC structure enquête 5M, corrèle historique organisationnel |
| 40 | Déclaration CNESST obligatoire | Transmission déclarations selon délais légaux LSST Art. 280 | Formulaires pré-remplis, calcul délais, transmission électronique automatique | Accident mortel - ARC transmet déclaration <24h, alerte tous intervenants obligatoires |
| 41 | Suivi médical post-incident | Coordination soins, retour travail selon CNESST | Liaison professionnels santé, accommodements, suivi évolution capacités | Blessure dos - ARC coordonne physio, propose postes adaptés, suit progression |
| 42 | Investigation quasi-accident | Analyse événements précurseurs selon pyramide Heinrich | Collecte témoignages, analyse conditions, identification mesures préventives | Presque-chute échafaudage - ARC analyse défaillances, propose renforcements préventifs |
| 43 | Gestion témoignages | Recueil/conservation témoignages selon procédures légales | Enregistrement sécurisé, horodatage, conservation conforme durées légales | Témoin accident - ARC enregistre déposition cryptée, conserve 5 ans selon LSST |
| 44 | Analyse statistique incidents | Compilation données, calcul indices, identification tendances | Tableaux bord automatiques, indices fréquence/gravité, analyses prédictives | Usine 500 employés - ARC génère indices mensuel, identifie patterns saisonniers |
| 45 | Coordination services urgence | Interface ambulance, police, pompiers selon gravité incident | Géolocalisation précise, informations médicales, coordination multi-services | Urgence chimique - ARC transmet FDS automatiquement aux secours, guide décontamination |
| 46 | Communication interne incident | Information personnel, familles, direction selon protocoles | Messages ciblés, respect confidentialité, coordination communication externe | Accident grave - ARC informe famille, direction, syndicat selon protocoles établis |
| 47 | Suivi actions correctives | Planification/suivi mesures préventives issues enquêtes | Échéancier automatique, responsables assignés, validation efficacité mesures | Suite enquête - ARC programme formation, modification équipement, suit réalisation |

---

## **CATÉGORIE 5 : CONFORMITÉ RÉGLEMENTAIRE ET AUDITS (12 workflows)**

| # | Nom du Workflow | Description Succincte | Amélioration ARC | Exemple Concret Réglementaire |
|---|---|---|---|---|
| 48 | Audit conformité CSTC | Vérification systématique conformité Code sécurité construction | Agent génère grilles audit par section CSTC, suit écarts, programme correctifs | Audit protection chutes - ARC vérifie certifications harnais, conformité ancrages CSA Z259 |
| 49 | Préparation inspection CNESST | Préparation proactive visites inspection Commission | Agent compile documents requis, identifie lacunes, génère plan préventif | Inspection chantier - ARC prépare registres formation, rapports équipements, procédures |
| 50 | Audit interne programme prévention | Révision annuelle PPSST selon LSST Art. 59 | Structure automatique selon exigences, intègre évaluations risques, suit mises à jour | PPSST manufacturier - ARC génère sections obligatoires, planifie révisions annuelles |
| 51 | Vérification conformité EPI | Audit équipements protection individuelle selon normes | Base données certifications, suivi expiration, vérification usage conforme | Casques chantier - ARC vérifie certifications CSA Z94.1, programme remplacement 5 ans |
| 52 | Audit ventilation industrielle | Vérification systèmes captage/ventilation selon ACGIH | Mesures débits, efficacité captage, maintenance préventive programmée | Atelier soudage - ARC mesure vitesses captage, programme nettoyage conduits |
| 53 | Audit machines/équipements | Vérification sécurité machines selon RSST Art. 173-193 | Inventaire automatique, check-lists spécialisées, suivi non-conformités | Machines production - ARC audit protecteurs, dispositifs arrêt urgence, maintenance |
| 54 | Contrôle exposition substances | Audit conformité VEMP selon RSST Annexe I | Stratégies échantillonnage, calculs exposition, actions si dépassement | Exposition silice cristalline - ARC programme échantillonnage, calcule TWA 8h |
| 55 | Audit système cadenassage | Vérification procédures isolation énergies RSST Art. 185-188 | Inventaire points cadenassage, validation procédures, formation opérateurs | Maintenance sécuritaire - ARC audit 150 machines, valide procédures individuelles |
| 56 | Vérification espaces clos | Audit classification/procédures espaces confinés RSST Art. 297-310 | Inventaire complet, classification risques, procédures entrée/surveillance | Espaces industriels - ARC classe 47 espaces selon atmosphère, ventilation requise |
| 57 | Audit ergonomie postes | Évaluation systématique facteurs ergonomiques selon IRSST | Analyses posturales, calculs efforts, recommandations aménagement | Chaîne assemblage - ARC évalue 25 postes, propose améliorations TMS |
| 58 | Contrôle qualité formation | Audit efficacité programmes formation selon compétences | Évaluations learning, corrélation formation/incidents, amélioration continue | Formation sécurité - ARC corrèle formation harnais/incidents chute, ajuste contenu |
| 59 | Audit documentation SST | Vérification complétude/conformité documents obligatoires | Inventaire documents, vérification signatures/dates, mise à jour automatique | Documentation légale - ARC vérifie 150 documents, alerte expirations/manquants |

---

## **CATÉGORIE 6 : GESTION DES ÉQUIPEMENTS ET EPI (8 workflows)**

| # | Nom du Workflow | Description Succincte | Amélioration ARC | Exemple Concret Réglementaire |
|---|---|---|---|---|
| 60 | Inspection équipements levage | Vérifications obligatoires grues/palans selon RSST Art. 255-282 | Planificateur programme inspections, génère check-lists, suit non-conformités | Grue mobile - ARC programme inspection quotidienne/hebdo/annuelle CSA B167, génère rapports |
| 61 | Gestion cycle vie EPI | Suivi attribution/entretien/remplacement équipements protection | Gestionnaire suit expiration, usure selon usage, commandes préventives | Harnais sécurité - ARC suit utilisation quotidienne, calcule durée vie selon UV/produits |
| 62 | Maintenance préventive équipements | Planification entretien selon recommandations fabricant/réglementation | Calendrier automatique, ordres travail, suivi historique pannes | Compresseurs industriels - ARC programme maintenance selon heures fonctionnement, ASME |
| 63 | Certification équipements pression | Gestion inspections réservoirs/chaudières selon RLRQ c.M-6 | Suivi certifications, planification inspections, liaison avec inspecteurs | Chaudière 2000 kPa - ARC programme inspection annuelle, coordonne avec RBQ |
| 64 | Contrôle équipements électriques | Vérifications sécurité installations selon CSA/code électrique | Tests isolation, continuité masses, vérification protections différentielles | Installation 600V - ARC programme tests thermographie, vérification relais protection |
| 65 | Gestion outils portatifs | Contrôle sécurité outils électriques/pneumatiques selon CSA | Inspections visuelles, tests électriques, étiquetage conforme/non-conforme | Outils chantier - ARC teste isolation classe II, programme vérification mensuelle |
| 66 | Suivi équipements détection | Maintenance détecteurs gaz/incendie selon normes NFPA | Calibrations périodiques, tests fonctionnels, remplacement capteurs | Détecteurs H2S - ARC programme calibration mensuelle, alerte expiration capteurs |
| 67 | Inventaire équipements urgence | Gestion trousses premiers secours/équipements urgence | Vérification contenus, expiration produits, formation utilisateurs | Trousses secours - ARC vérifie expiration pansements, programme formation RCR |

---

## **CATÉGORIE 7 : PLANS D'URGENCE ET GESTION DE CRISE (8 workflows)**

| # | Nom du Workflow | Description Succincte | Amélioration ARC | Exemple Concret Réglementaire |
|---|---|---|---|---|
| 68 | Plan évacuation urgence | Élaboration procédures évacuation selon RSST Art. 54-57 | Simulateur modélise temps évacuation, identifie goulots, optimise itinéraires | Site 500 employés - ARC calcule temps selon occupation, teste scénarios incendie/toxique |
| 69 | Gestion matières dangereuses | Procédures intervention déversement/fuite substances chimiques | Agent urgence accède FDS, calcule zones exclusion, génère procédures confinement | Déversement H2SO4 - ARC consulte FDS, calcule dispersion météo, plan neutralisation |
| 70 | Plan mesures urgence | Élaboration PMU selon secteur activité et réglementation municipale | Coordination services externes, communication crise, exercices périodiques | Usine chimique - ARC coordonne avec pompiers, programme exercices trimestriels |
| 71 | Gestion communication crise | Coordination information interne/externe lors urgences | Messages pré-rédigés, contacts prioritaires, liaison médias selon protocoles | Incident majeur - ARC informe automatiquement: famille, autorités, médias selon gravité |
| 72 | Procédures confinement | Plans refuge sur place selon risques atmosphériques | Calculs temps protection, étanchéité bâtiments, ventilation forcée | Fuite chlore proximité - ARC active confinement, arrête ventilation, guide décontamination |
| 73 | Coordination secours externes | Interface pompiers/ambulance/police selon type urgence | Géolocalisation précise, plans accès, informations risques spécifiques | Urgence industrielle - ARC transmet plans site aux pompiers, guide accès sécuritaire |
| 74 | Gestion continuité activités | Plans maintien opérations critiques post-incident | Identification processus essentiels, sites alternatifs, fournisseurs secours | Panne électrique majeure - ARC active génératrices priorités, maintient sécurité |
| 75 | Exercices simulation urgence | Organisation exercices évacuation/intervention selon fréquences réglementaires | Scénarios variables, évaluation performances, amélioration continue | Exercice annuel - ARC simule incendie réaliste, mesure temps, identifie améliorations |

---

## **CATÉGORIE 8 : COMMUNICATION ET SENSIBILISATION SST (8 workflows)**

| # | Nom du Workflow | Description Succincte | Amélioration ARC | Exemple Concret Réglementaire |
|---|---|---|---|---|
| 76 | Animation comité SST | Organisation réunions obligatoires comité selon LSST Art. 78-86 | Communicateur génère ordre du jour selon incidents, suit actions, programme échéances | Comité mensuel - ARC compile statistiques, recommandations suspens, génère PV structuré |
| 77 | Campagne sensibilisation ciblée | Messages prévention adaptés risques/populations selon analyse incidents | Communicateur analyse patterns, identifie groupes risque, génère contenus personnalisés | Sensibilisation TMS - ARC identifie postes problématiques, crée vidéos démonstration |
| 78 | Communication incidents | Information personnelle suite accidents selon protocoles établis | Messages ciblés selon gravité, respect confidentialité, coordination externe | Accident grave - ARC informe équipes selon proximité, respecte vie privée victime |
| 79 | Affichage obligatoire SST | Gestion affichage réglementaire selon LSST/CNESST | Mise à jour automatique, emplacements conformes, langues multiples | Affichage droits travailleurs - ARC met à jour selon modifications CNESST, traduit |
| 80 | Boîte suggestions sécurité | Système collecte amélioration par employés selon participation LSST | Plateforme digitale, analyse automatique, feedback systématique proposants | Amélioration continue - ARC classe suggestions, priorise selon impact, informe suites |
| 81 | Bulletin sécurité périodique | Publication régulière information SST selon plan communication | Génération automatique contenu selon actualités, statistiques, bonnes pratiques | Bulletin mensuel - ARC compile incidents mois, conseils préventifs, nouveautés réglementaires |
| 82 | Formation sensibilisation générale | Sessions information SST pour tous employés selon LSST Art. 51 | Modules adaptatifs selon postes, évaluations interactives, suivi participation | Formation annuelle - ARC personnalise selon expositions individuelles, évalue acquisitions |
| 83 | Communication multilingue | Adaptation messages SST selon diversité linguistique milieu | Traduction automatique, pictogrammes universels, validation compréhension | Site multiculturel - ARC traduit procédures 5 langues, utilise symboles ISO |

---

## **CATÉGORIE 9 : SURVEILLANCE DE LA SANTÉ AU TRAVAIL (7 workflows)**

| # | Nom du Workflow | Description Succincte | Amélioration ARC | Exemple Concret Réglementaire |
|---|---|---|---|---|
| 84 | Surveillance médicale exposition | Organisation suivi médical obligatoire travailleurs exposés RSST Art. 121-126 | Agent santé suit expositions cumulatives, programme examens, corrèle surveillance biologique | Exposition plomb - ARC suit plombémies, programme prélèvements, alerte seuil 1.45 μmol/L |
| 85 | Gestion aptitude travail | Évaluation/suivi restrictions médicales selon accommodements CNESST | Adaptateur analyse restrictions, propose postes compatibles, suit évolution capacités | Restriction port charges - ARC identifie postes <15kg, propose rotation équipes |
| 86 | Programme audiométrie | Suivi auditif exposition bruit selon RSST Art. 131-144 | Audiogrammes automatisés, corrélation exposition/perte, programme protection | Exposition >85 dB(A) - ARC programme audiométrie annuelle, analyse évolution audition |
| 87 | Surveillance respiratoire | Suivi fonction pulmonaire exposition poussières/gaz selon spirométrie | Tests spirométriques périodiques, corrélation exposition/fonction, actions préventives | Exposition silice - ARC programme spirométrie selon guide IRSST, suit évolution |
| 88 | Gestion vaccinations | Suivi vaccinations obligatoires selon expositions professionnelles | Calendrier automatique, rappels échéances, coordination services santé | Hépatite B laboratoire - ARC suit sérologie, programme rappels selon protocole |
| 89 | Suivi biologique exposition | Dosages biologiques substances selon RSST indicateurs biologiques | Planification prélèvements, suivi évolution, actions si dépassement IBE | Exposition solvants - ARC programme dosages urinaires, compare aux IBE |
| 90 | Analyse aptitude postes | Évaluation capacités individuelles selon exigences postes | Tests aptitudes physiques/cognitives, adaptation charges travail, suivi évolution | Exigences physiques - ARC évalue capacités cardiovasculaires, adapte exigences |

---

## **CATÉGORIE 10 : DOCUMENTATION ET TRAÇABILITÉ (10 workflows)**

| # | Nom du Workflow | Description Succincte | Amélioration ARC | Exemple Concret Réglementaire |
|---|---|---|---|---|
| 91 | Registre accidents/incidents | Tenue obligatoire registre selon LSST Art. 280 conservation 5 ans | Documentaire compile automatiquement événements, génère statistiques, assure conservation | Registre annuel - ARC génère bilans, calcule indices fréquence/gravité, rapports CNESST |
| 92 | Programme prévention (PPSST) | Élaboration/mise à jour programme selon LSST Art. 59 | Gestionnaire structure selon exigences, intègre évaluations risques, suit mises à jour | PPSST manufacturier - ARC génère sections obligatoires, intègre évaluations, révisions annuelles |
| 93 | Dossiers formation SST | Conservation attestations/certificats selon durées légales | Base données centralisée, alertes expiration, génération relevés formation | Dossiers employés - ARC conserve formations 5 ans, alerte recyclages obligatoires |
| 94 | Rapports inspection équipements | Documentation vérifications selon fréquences réglementaires | Génération automatique rapports, signatures électroniques, archivage sécurisé | Inspections grues - ARC génère rapports quotidiens/annuels, archive 10 ans |
| 95 | Certificats médicaux travail | Gestion aptitudes médicales selon exigences postes | Dossiers confidentiels, alertes expiration, liaison professionnels santé | Aptitudes conduire - ARC alerte expiration certificats, programme renouvellements |
| 96 | Procès-verbaux comité SST | Rédaction/conservation PV réunions selon LSST Art. 78-86 | Génération automatique selon ordre jour, suivi actions décidées, archivage légal | PV mensuels - ARC structure selon participants, décisions, actions, conserve indéfiniment |
| 97 | Déclarations réglementaires | Soumission rapports obligatoires selon échéanciers CNESST | Compilation automatique données, génération rapports, transmission électronique | Rapport annuel CNESST - ARC compile statistiques, génère formulaires, transmet délais |
| 98 | Archives sécurité projet | Conservation documents projets selon durées légales variables | Gestion cycle vie documents, conservation différenciée, destruction sécurisée | Archives chantier - ARC conserve permis 5 ans, plans 10 ans, PV indéfiniment |
| 99 | Traçabilité substances dangereuses | Suivi utilisation/élimination matières selon manifests | Base données utilisations, calculs bilans matières, déclarations environnementales | Solvants industriels - ARC suit consommation, génère manifests déchets dangereux |
| 100 | Système qualité SST | Gestion documentaire système selon ISO 45001/BNQ 9700-800 | Contrôle versions, workflows approbation, audits documentation, amélioration continue | Système ISO 45001 - ARC gère 500+ documents, workflows validation, audit annuel |

---

## **SYNTHÈSE RÉGLEMENTAIRE PAR CADRE LÉGISLATIF**

### **LSST (Loi sur la santé et la sécurité du travail)**
- **Articles clés couverts** : 51 (formation), 59 (programme prévention), 62 (déclaration), 78-86 (comité SST), 280 (registre)
- **Workflows principaux** : 29, 38, 48, 76, 91, 96, 97

### **LMRSST (Loi modernisant le régime SST)**  
- **Nouvelles exigences** : CoSS obligatoire >100 travailleurs, formation 240h, présence terrain
- **Workflows spécifiques** : 28, 48, 49, 97

### **CSTC (Code sécurité travaux construction)**
- **Sections majeures** : II (organisation), III (protection chutes), VIII (électricité), IX (excavation)
- **Workflows construction** : 1, 3, 12, 14, 16-19, 25, 48

### **RSST (Règlement santé sécurité travail)**
- **Chapitres principaux** : III (machines), IV (EPI), V (espaces clos), VIII (substances), IX (bruit)
- **Workflows généraux** : 2, 5, 8, 13, 16, 31, 34, 50, 54, 56, 84, 86

---

## **BÉNÉFICES OPÉRATIONNELS ARC PAR CATÉGORIE**

| Catégorie | Gain Temps | Amélioration Conformité | Réduction Erreurs | Traçabilité |
|---|---|---|---|---|
| **Identification risques** | 60-75% | +25% | -80% | 100% |
| **Permis travail** | 70-85% | +30% | -90% | 100% |
| **Formation SST** | 50-65% | +40% | -70% | 100% |
| **Gestion incidents** | 55-70% | +35% | -85% | 100% |
| **Conformité/audits** | 65-80% | +45% | -75% | 100% |
| **Équipements/EPI** | 60-75% | +30% | -80% | 100% |
| **Plans urgence** | 70-85% | +25% | -85% | 100% |
| **Communication SST** | 50-70% | +20% | -60% | 100% |
| **Surveillance santé** | 55-75% | +35% | -75% | 100% |
| **Documentation** | 75-90% | +50% | -95% | 100% |

---

**Note méthodologique** : Ces 100 workflows couvrent l'ensemble des obligations réglementaires québécoises en SST et représentent les processus opérationnels où l'assistance agentique d'ARC apporte une valeur ajoutée mesurable en termes d'efficacité, conformité et traçabilité.
