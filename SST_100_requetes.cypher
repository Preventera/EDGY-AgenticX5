-- ============================================================================
-- 🛡️ SAFETYGRAPH - 100 REQUÊTES CYPHER AVANCÉES
-- EDGY-AgenticX5 | Preventera | GenAISafety
-- Analyses prédictives SST pour le Québec
-- ============================================================================
-- 
-- État actuel Neo4j (28 novembre 2025):
--   • 460 Organizations (16 secteurs SCIAN)
--   • 3,926 Persons (anonymisées Loi 25)
--   • 2,870 RisqueDanger
--   • 1,429 Zones
--   • 1,125 Teams
--   • 2,363 Roles
--
-- Labels principaux: Organization, Person, RisqueDanger, Zone, Team, Role
-- Relations: APPARTIENT_A, MEMBRE_DE, OCCUPE_ROLE, TRAVAILLE_DANS, EXPOSE_A, LOCALISE_DANS
-- ============================================================================


-- ############################################################################
-- SECTION 1: STATISTIQUES GLOBALES ET KPIs
-- ############################################################################

-- 1.1 Statistiques globales du graphe SafetyGraph
MATCH (o:Organization) WITH count(o) as orgs
MATCH (p:Person) WITH orgs, count(p) as persons
MATCH (r:RisqueDanger) WITH orgs, persons, count(r) as risks
MATCH (z:Zone) WITH orgs, persons, risks, count(z) as zones
MATCH (t:Team) WITH orgs, persons, risks, zones, count(t) as teams
MATCH (ro:Role) 
RETURN orgs AS Organizations, persons AS Personnes, risks AS Risques, 
       zones AS Zones, teams AS Équipes, count(ro) AS Rôles;

-- 1.2 Répartition des organisations par secteur SCIAN
MATCH (o:Organization)
WHERE o.sector_scian IS NOT NULL
RETURN o.sector_scian AS secteur_scian, 
       count(o) AS nb_organisations,
       sum(o.nb_employes) AS total_employes,
       collect(o.name)[0..3] AS exemples
ORDER BY nb_organisations DESC;

-- 1.3 Distribution des zones par niveau de risque
MATCH (z:Zone)
WHERE z.risk_level IS NOT NULL
RETURN z.risk_level AS niveau_risque, 
       count(z) AS nb_zones,
       round(count(z) * 100.0 / (MATCH (z2:Zone) RETURN count(z2))[0], 1) AS pourcentage
ORDER BY 
    CASE z.risk_level 
        WHEN 'critique' THEN 1 
        WHEN 'eleve' THEN 2 
        WHEN 'moyen' THEN 3 
        ELSE 4 
    END;

-- 1.4 Nombre de risques par catégorie
MATCH (r:RisqueDanger)
WHERE r.categorie IS NOT NULL
RETURN r.categorie AS categorie,
       count(r) AS nb_risques,
       avg(r.probabilite * r.gravite) AS score_moyen
ORDER BY nb_risques DESC;


-- ############################################################################
-- SECTION 2: ANALYSES PAR SECTEUR SCIAN
-- ############################################################################

-- 2.1 Top 10 secteurs SCIAN par nombre de risques
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
RETURN o.sector_scian AS secteur,
       count(DISTINCT o) AS nb_orgs,
       count(DISTINCT z) AS nb_zones,
       count(r) AS nb_risques,
       round(avg(r.probabilite * r.gravite), 2) AS score_risque_moyen
ORDER BY nb_risques DESC
LIMIT 10;

-- 2.2 Secteurs avec le plus de risques Tolérance Zéro (score >= 15)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE r.probabilite * r.gravite >= 15
RETURN o.sector_scian AS secteur,
       count(r) AS nb_risques_TZ,
       collect(DISTINCT r.description)[0..5] AS exemples_risques
ORDER BY nb_risques_TZ DESC
LIMIT 10;

-- 2.3 Comparaison des 5 secteurs prioritaires CNESST
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621-624', '31-33', '44-45', '236-238', '72']
RETURN o.sector_scian AS secteur,
       CASE o.sector_scian
           WHEN '621-624' THEN '🏥 Santé'
           WHEN '31-33' THEN '🏭 Fabrication'
           WHEN '44-45' THEN '🛒 Commerce'
           WHEN '236-238' THEN '🏗️ Construction'
           WHEN '72' THEN '🍽️ Resto/Hôtel'
       END AS nom_secteur,
       count(DISTINCT o) AS orgs,
       count(r) AS risques,
       round(avg(r.probabilite * r.gravite), 2) AS score_moyen
ORDER BY risques DESC;

-- 2.4 Profil de risque par secteur (catégories dominantes)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IS NOT NULL
WITH o.sector_scian AS secteur, r.categorie AS categorie, count(r) AS cnt
WITH secteur, collect({cat: categorie, count: cnt}) AS risques_par_cat
RETURN secteur, risques_par_cat[0].cat AS risque_dominant, risques_par_cat[0].count AS nb
ORDER BY nb DESC
LIMIT 15;


-- ############################################################################
-- SECTION 3: ANALYSES DES RISQUES - IDENTIFICATION ET PRIORISATION
-- ############################################################################

-- 3.1 Top 30 risques par score (Probabilité × Gravité)
MATCH (r:RisqueDanger)
WHERE r.probabilite IS NOT NULL AND r.gravite IS NOT NULL
RETURN r.description AS risque,
       r.categorie AS categorie,
       r.probabilite AS P,
       r.gravite AS G,
       r.probabilite * r.gravite AS score
ORDER BY score DESC
LIMIT 30;

-- 3.2 Risques Tolérance Zéro par catégorie
MATCH (r:RisqueDanger)
WHERE r.probabilite * r.gravite >= 15
RETURN r.categorie AS categorie,
       count(r) AS nb_risques_TZ,
       collect(r.description)[0..3] AS exemples
ORDER BY nb_risques_TZ DESC;

-- 3.3 Risques les plus fréquents (par description similaire)
MATCH (r:RisqueDanger)
WITH r.description AS desc, count(r) AS freq
WHERE freq > 5
RETURN desc AS risque_recurrent, freq AS frequence
ORDER BY freq DESC
LIMIT 20;

-- 3.4 Matrice de risques (groupement par P et G)
MATCH (r:RisqueDanger)
WHERE r.probabilite IS NOT NULL AND r.gravite IS NOT NULL
RETURN r.probabilite AS probabilite, 
       r.gravite AS gravite,
       count(r) AS nb_risques,
       r.probabilite * r.gravite AS score
ORDER BY score DESC;

-- 3.5 Risques par statut
MATCH (r:RisqueDanger)
RETURN r.statut AS statut, count(r) AS nb_risques
ORDER BY nb_risques DESC;


-- ############################################################################
-- SECTION 4: ANALYSES DES ZONES - CARTOGRAPHIE DES DANGERS
-- ############################################################################

-- 4.1 Zones critiques avec le plus de risques associés
MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE z.risk_level = 'critique'
RETURN z.name AS zone,
       z.risk_level AS niveau,
       count(r) AS nb_risques,
       avg(r.probabilite * r.gravite) AS score_moyen,
       collect(r.categorie)[0..3] AS categories_risques
ORDER BY nb_risques DESC
LIMIT 20;

-- 4.2 Zones sans risques identifiés (potentiel audit)
MATCH (z:Zone)
WHERE NOT (z)<-[:LOCALISE_DANS]-(:RisqueDanger)
RETURN z.name AS zone, z.risk_level AS niveau
ORDER BY z.risk_level;

-- 4.3 Zones par types de dangers identifiés
MATCH (z:Zone)
WHERE z.dangers_identifies IS NOT NULL
UNWIND z.dangers_identifies AS danger
RETURN danger, count(z) AS nb_zones
ORDER BY nb_zones DESC
LIMIT 15;

-- 4.4 Zones par EPI requis
MATCH (z:Zone)
WHERE z.epi_requis IS NOT NULL AND size(z.epi_requis) > 0
UNWIND z.epi_requis AS epi
RETURN epi AS equipement_protection, count(z) AS nb_zones
ORDER BY nb_zones DESC
LIMIT 15;

-- 4.5 Concentration de risques par zone (hotspots)
MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WITH z, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE nb_risques >= 5
RETURN z.name AS zone_hotspot,
       z.risk_level AS niveau,
       nb_risques,
       round(score_moyen, 2) AS score_moyen
ORDER BY score_moyen DESC
LIMIT 15;


-- ############################################################################
-- SECTION 5: ANALYSES DES PERSONNES ET EXPOSITION
-- ############################################################################

-- 5.1 Distribution des personnes par groupe d'âge
MATCH (p:Person)
WHERE p.age_groupe IS NOT NULL
RETURN p.age_groupe AS groupe_age, count(p) AS nb_personnes
ORDER BY p.age_groupe;

-- 5.2 Personnes les plus exposées aux risques
MATCH (p:Person)-[:EXPOSE_A]->(r:RisqueDanger)
RETURN p.matricule AS matricule,
       p.department AS departement,
       count(r) AS nb_risques_exposes,
       avg(r.probabilite * r.gravite) AS score_exposition_moyen
ORDER BY nb_risques_exposes DESC
LIMIT 20;

-- 5.3 Exposition par groupe d'âge (analyse vulnérabilité)
MATCH (p:Person)-[:EXPOSE_A]->(r:RisqueDanger)
WHERE p.age_groupe IS NOT NULL
RETURN p.age_groupe AS groupe_age,
       count(DISTINCT p) AS nb_personnes,
       count(r) AS nb_expositions,
       round(avg(r.probabilite * r.gravite), 2) AS score_moyen
ORDER BY p.age_groupe;

-- 5.4 Certifications SST les plus fréquentes
MATCH (p:Person)
WHERE p.certifications_sst IS NOT NULL
UNWIND p.certifications_sst AS cert
RETURN cert AS certification, count(p) AS nb_personnes
ORDER BY nb_personnes DESC
LIMIT 20;

-- 5.5 Personnes sans certification (audit conformité)
MATCH (p:Person)
WHERE p.certifications_sst IS NULL OR size(p.certifications_sst) = 0
RETURN count(p) AS personnes_sans_certification;

-- 5.6 Gap de certification par département
MATCH (p:Person)
WHERE p.department IS NOT NULL
WITH p.department AS dept, 
     count(p) AS total,
     sum(CASE WHEN p.certifications_sst IS NULL OR size(p.certifications_sst) = 0 THEN 1 ELSE 0 END) AS sans_cert
RETURN dept AS departement, 
       total AS nb_personnes,
       sans_cert AS sans_certification,
       round(sans_cert * 100.0 / total, 1) AS pct_non_certifie
ORDER BY pct_non_certifie DESC
LIMIT 15;


-- ############################################################################
-- SECTION 6: ANALYSES DES ÉQUIPES ET RÔLES
-- ############################################################################

-- 6.1 Équipes par taille
MATCH (t:Team)<-[:MEMBRE_DE]-(p:Person)
RETURN t.name AS equipe, t.department AS departement, count(p) AS nb_membres
ORDER BY nb_membres DESC
LIMIT 20;

-- 6.2 Rôles avec autorité d'arrêt de travail
MATCH (r:Role)
WHERE r.autorite_arret_travail = true
RETURN r.name AS role, r.niveau_hierarchique AS niveau
ORDER BY r.niveau_hierarchique DESC;

-- 6.3 Distribution des rôles par niveau hiérarchique
MATCH (r:Role)
WHERE r.niveau_hierarchique IS NOT NULL
RETURN r.niveau_hierarchique AS niveau, count(r) AS nb_roles
ORDER BY niveau;

-- 6.4 Couverture des équipes par organisation
MATCH (o:Organization)<-[:APPARTIENT_A]-(t:Team)
RETURN o.name AS organisation,
       o.sector_scian AS secteur,
       count(t) AS nb_equipes
ORDER BY nb_equipes DESC
LIMIT 20;


-- ############################################################################
-- SECTION 7: ANALYSES PRÉDICTIVES - PATTERNS ET CORRÉLATIONS
-- ############################################################################

-- 7.1 Corrélation secteur-catégorie de risque
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IS NOT NULL AND r.categorie IS NOT NULL
RETURN o.sector_scian AS secteur,
       r.categorie AS categorie_risque,
       count(r) AS nb_occurrences,
       round(avg(r.probabilite * r.gravite), 2) AS score_moyen
ORDER BY nb_occurrences DESC
LIMIT 30;

-- 7.2 Pattern: Secteurs à risques multiples (diversité des dangers)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WITH o.sector_scian AS secteur, collect(DISTINCT r.categorie) AS categories
RETURN secteur, 
       size(categories) AS diversite_risques,
       categories
ORDER BY diversite_risques DESC
LIMIT 10;

-- 7.3 Indicateur de complexité organisationnelle
MATCH (o:Organization)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)
WITH o, count(DISTINCT z) AS zones, count(DISTINCT t) AS equipes
RETURN o.name AS organisation,
       o.nb_employes AS employes,
       zones,
       equipes,
       CASE 
           WHEN o.nb_employes > 0 THEN round(zones * 1.0 / (o.nb_employes / 100), 2)
           ELSE 0 
       END AS ratio_zones_100emp
ORDER BY employes DESC
LIMIT 20;

-- 7.4 Prédiction de risque par taille d'organisation
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WITH o, count(r) AS nb_risques
RETURN 
    CASE 
        WHEN o.nb_employes < 100 THEN 'Petite (<100)'
        WHEN o.nb_employes < 500 THEN 'Moyenne (100-500)'
        WHEN o.nb_employes < 2000 THEN 'Grande (500-2000)'
        ELSE 'Très grande (>2000)'
    END AS taille_organisation,
    count(o) AS nb_orgs,
    sum(nb_risques) AS total_risques,
    round(avg(nb_risques), 1) AS risques_moyens_par_org
ORDER BY risques_moyens_par_org DESC;

-- 7.5 Score de risque pondéré par organisation
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WITH o, 
     count(r) AS nb_risques,
     sum(r.probabilite * r.gravite) AS score_total,
     sum(CASE WHEN r.probabilite * r.gravite >= 15 THEN 1 ELSE 0 END) AS risques_TZ
RETURN o.name AS organisation,
       o.sector_scian AS secteur,
       nb_risques,
       risques_TZ AS tolerance_zero,
       round(score_total / nb_risques, 2) AS score_moyen,
       round(score_total, 0) AS score_total
ORDER BY score_total DESC
LIMIT 25;


-- ############################################################################
-- SECTION 8: ALERTES ET SURVEILLANCE PROACTIVE
-- ############################################################################

-- 8.1 Alerte: Organisations avec concentration de risques TZ
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE r.probabilite * r.gravite >= 15
WITH o, count(r) AS nb_TZ
WHERE nb_TZ >= 5
RETURN '🚨 ALERTE' AS type,
       o.name AS organisation,
       o.sector_scian AS secteur,
       nb_TZ AS risques_tolerance_zero
ORDER BY nb_TZ DESC;

-- 8.2 Alerte: Zones critiques multi-risques
MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE z.risk_level = 'critique'
WITH z, count(r) AS nb_risques, collect(DISTINCT r.categorie) AS categories
WHERE nb_risques >= 5
RETURN '⚠️ ZONE CRITIQUE' AS type,
       z.name AS zone,
       nb_risques,
       categories
ORDER BY nb_risques DESC;

-- 8.3 Surveillance: Jeunes travailleurs (18-24) exposés à risques élevés
MATCH (p:Person)-[:EXPOSE_A]->(r:RisqueDanger)
WHERE p.age_groupe = '18-24' AND r.probabilite * r.gravite >= 12
RETURN '👤 JEUNE TRAVAILLEUR' AS type,
       p.matricule AS matricule,
       p.department AS departement,
       count(r) AS nb_risques_eleves,
       collect(r.categorie)[0..3] AS categories
ORDER BY nb_risques_eleves DESC
LIMIT 20;

-- 8.4 Surveillance: Départements à risque élevé
MATCH (p:Person)-[:EXPOSE_A]->(r:RisqueDanger)
WHERE p.department IS NOT NULL
WITH p.department AS dept, 
     count(DISTINCT p) AS nb_personnes,
     avg(r.probabilite * r.gravite) AS score_moyen
WHERE score_moyen >= 12
RETURN '📊 DEPT À SURVEILLER' AS type,
       dept AS departement,
       nb_personnes,
       round(score_moyen, 2) AS score_risque_moyen
ORDER BY score_moyen DESC;


-- ############################################################################
-- SECTION 9: CONFORMITÉ ET AUDIT
-- ############################################################################

-- 9.1 Audit: Couverture des certifications par secteur
MATCH (o:Organization)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WHERE o.sector_scian IS NOT NULL
WITH o.sector_scian AS secteur,
     count(DISTINCT p) AS total_personnes,
     sum(CASE WHEN p.certifications_sst IS NOT NULL AND size(p.certifications_sst) > 0 THEN 1 ELSE 0 END) AS avec_cert
RETURN secteur,
       total_personnes,
       avec_cert AS personnes_certifiees,
       round(avec_cert * 100.0 / total_personnes, 1) AS taux_certification
ORDER BY taux_certification ASC
LIMIT 15;

-- 9.2 Audit: Zones sans EPI définis
MATCH (z:Zone)
WHERE z.risk_level IN ['critique', 'eleve'] 
  AND (z.epi_requis IS NULL OR size(z.epi_requis) = 0)
RETURN '❌ EPI MANQUANT' AS type,
       z.name AS zone,
       z.risk_level AS niveau_risque
ORDER BY z.risk_level;

-- 9.3 Audit: Traçabilité des relations par organisation
MATCH (o:Organization)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)
OPTIONAL MATCH (t)<-[:MEMBRE_DE]-(p:Person)
WITH o, count(DISTINCT z) AS zones, count(DISTINCT t) AS teams, count(DISTINCT p) AS persons
RETURN o.name AS organisation,
       zones,
       teams,
       persons,
       CASE 
           WHEN zones = 0 OR teams = 0 OR persons = 0 THEN '⚠️ INCOMPLET'
           ELSE '✅ COMPLET'
       END AS statut_cartographie
ORDER BY statut_cartographie DESC, zones DESC
LIMIT 30;

-- 9.4 Conformité ISO 45001: Risques documentés par zone
MATCH (z:Zone)
OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WITH z, count(r) AS nb_risques
RETURN z.name AS zone,
       z.risk_level AS niveau,
       nb_risques,
       CASE 
           WHEN nb_risques = 0 THEN '❌ Non conforme'
           WHEN nb_risques < 3 THEN '⚠️ Partiel'
           ELSE '✅ Conforme'
       END AS statut_iso45001
ORDER BY nb_risques ASC
LIMIT 30;


-- ############################################################################
-- SECTION 10: REQUÊTES POUR DASHBOARD ET VISUALISATION
-- ############################################################################

-- 10.1 Données pour graphique: Organisations par secteur (barres)
MATCH (o:Organization)
WHERE o.sector_scian IS NOT NULL
RETURN o.sector_scian AS label, count(o) AS value
ORDER BY value DESC;

-- 10.2 Données pour graphique: Zones par niveau (donut)
MATCH (z:Zone)
WHERE z.risk_level IS NOT NULL
RETURN z.risk_level AS label, count(z) AS value
ORDER BY 
    CASE z.risk_level 
        WHEN 'critique' THEN 1 
        WHEN 'eleve' THEN 2 
        WHEN 'moyen' THEN 3 
        ELSE 4 
    END;

-- 10.3 Données pour graphique: Risques par catégorie (treemap)
MATCH (r:RisqueDanger)
WHERE r.categorie IS NOT NULL
RETURN r.categorie AS label, 
       count(r) AS value,
       round(avg(r.probabilite * r.gravite), 2) AS score
ORDER BY value DESC;

-- 10.4 Données pour graphique: Top organisations (barres horizontales)
MATCH (o:Organization)
WHERE o.nb_employes IS NOT NULL AND o.nb_employes > 0
RETURN o.name AS label, o.nb_employes AS value, o.sector_scian AS category
ORDER BY value DESC
LIMIT 25;

-- 10.5 Données pour matrice de risques (scatter plot)
MATCH (r:RisqueDanger)
WHERE r.probabilite IS NOT NULL AND r.gravite IS NOT NULL
RETURN r.probabilite AS x, 
       r.gravite AS y,
       r.probabilite * r.gravite AS size,
       r.categorie AS category,
       r.description AS label
ORDER BY size DESC
LIMIT 100;


-- ############################################################################
-- SECTION 11: ANALYSES TEMPORELLES (préparation données historiques)
-- ############################################################################

-- 11.1 Préparation: Structure pour suivi temporel des risques
-- (Ces requêtes préparent le modèle pour des analyses futures avec dates)

-- Ajouter une propriété date_identification aux risques existants (UPDATE)
-- MATCH (r:RisqueDanger)
-- WHERE r.date_identification IS NULL
-- SET r.date_identification = date('2025-01-01')
-- RETURN count(r) AS risques_mis_a_jour;

-- 11.2 Modèle pour tendance des risques par mois
-- MATCH (r:RisqueDanger)
-- WHERE r.date_identification IS NOT NULL
-- RETURN r.date_identification.year AS annee,
--        r.date_identification.month AS mois,
--        count(r) AS nouveaux_risques
-- ORDER BY annee, mois;

-- 11.3 Modèle pour KPI d'évolution
-- MATCH (r:RisqueDanger)
-- WHERE r.date_identification >= date() - duration('P30D')
-- RETURN count(r) AS risques_30_derniers_jours;


-- ############################################################################
-- SECTION 12: REQUÊTES AGENTIQUES (pour intégration AI)
-- ############################################################################

-- 12.1 Agent VisionAI: Zones nécessitant surveillance caméra
MATCH (z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE z.risk_level = 'critique' AND r.categorie IN ['chute', 'mecanique', 'electrique']
RETURN DISTINCT z.name AS zone_surveillance,
       collect(DISTINCT r.categorie) AS types_risques,
       'VisionAI' AS agent_recommande
ORDER BY size(types_risques) DESC;

-- 12.2 Agent ErgoAI: Personnes exposées à risques ergonomiques
MATCH (p:Person)-[:EXPOSE_A]->(r:RisqueDanger)
WHERE r.categorie = 'ergonomique'
RETURN p.matricule AS cible_ergoai,
       p.department AS departement,
       count(r) AS nb_risques_ergo,
       'ErgoAI' AS agent_recommande
ORDER BY nb_risques_ergo DESC
LIMIT 50;

-- 12.3 Agent AlertAI: Déclencheurs d'alerte par seuil
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WITH o, z, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE score_moyen >= 14 OR nb_risques >= 8
RETURN o.name AS organisation,
       z.name AS zone,
       nb_risques,
       round(score_moyen, 2) AS score,
       CASE 
           WHEN score_moyen >= 15 THEN 'CRITIQUE'
           WHEN score_moyen >= 12 THEN 'ÉLEVÉ'
           ELSE 'MODÉRÉ'
       END AS niveau_alerte,
       'AlertAI' AS agent
ORDER BY score DESC;

-- 12.4 Agent ComplyAI: Écarts de conformité
MATCH (o:Organization)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)
OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WITH o, count(DISTINCT z) AS zones, count(r) AS risques
WHERE zones > 0 AND risques = 0
RETURN o.name AS organisation_non_conforme,
       zones AS zones_sans_risques_documentes,
       'ComplyAI - Audit requis' AS action,
       'ComplyAI' AS agent;

-- 12.5 Agent PredictAI: Données pour modèle prédictif ML
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WITH o, 
     count(DISTINCT z) AS nb_zones,
     count(DISTINCT r) AS nb_risques,
     count(DISTINCT t) AS nb_equipes,
     count(DISTINCT p) AS nb_personnes,
     avg(r.probabilite * r.gravite) AS score_risque_moyen
RETURN o.name AS organisation,
       o.sector_scian AS secteur,
       o.nb_employes AS employes,
       nb_zones,
       nb_risques,
       nb_equipes,
       nb_personnes,
       round(score_risque_moyen, 2) AS score_moyen,
       -- Features pour ML
       round(nb_risques * 1.0 / CASE WHEN nb_zones > 0 THEN nb_zones ELSE 1 END, 2) AS risques_par_zone,
       round(nb_personnes * 1.0 / CASE WHEN nb_equipes > 0 THEN nb_equipes ELSE 1 END, 2) AS personnes_par_equipe
ORDER BY score_moyen DESC
LIMIT 100;


-- ############################################################################
-- SECTION 13: RECHERCHE ET FILTRAGE AVANCÉ
-- ############################################################################

-- 13.1 Recherche d'organisation par nom (paramétré)
-- Paramètre: $terme = 'Hydro'
MATCH (o:Organization)
WHERE toLower(o.name) CONTAINS toLower($terme)
RETURN o.name AS organisation, o.sector_scian AS secteur, o.nb_employes AS employes
ORDER BY o.nb_employes DESC;

-- 13.2 Recherche de risques par mot-clé (paramétré)
-- Paramètre: $motcle = 'chute'
MATCH (r:RisqueDanger)
WHERE toLower(r.description) CONTAINS toLower($motcle)
RETURN r.description AS risque, r.categorie AS categorie, 
       r.probabilite * r.gravite AS score
ORDER BY score DESC;

-- 13.3 Filtrage multi-critères organisations
-- Paramètres: $secteur = '54', $min_employes = 1000
MATCH (o:Organization)
WHERE (o.sector_scian = $secteur OR $secteur IS NULL)
  AND (o.nb_employes >= $min_employes OR $min_employes IS NULL)
RETURN o.name, o.sector_scian, o.nb_employes
ORDER BY o.nb_employes DESC;

-- 13.4 Exploration du graphe: Chemin organisation → risques
MATCH path = (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.name CONTAINS 'CGI'
RETURN path
LIMIT 25;

-- 13.5 Exploration: Réseau d'une personne
MATCH (p:Person {matricule: 'PROF54-510-0001'})
OPTIONAL MATCH (p)-[:MEMBRE_DE]->(t:Team)
OPTIONAL MATCH (p)-[:OCCUPE_ROLE]->(ro:Role)
OPTIONAL MATCH (p)-[:TRAVAILLE_DANS]->(z:Zone)
OPTIONAL MATCH (p)-[:EXPOSE_A]->(r:RisqueDanger)
RETURN p, t, ro, z, r;


-- ############################################################################
-- SECTION 14: AGRÉGATIONS AVANCÉES ET MÉTRIQUES
-- ############################################################################

-- 14.1 Score de maturité SST par organisation
MATCH (o:Organization)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)
OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(r:RisqueDanger)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WITH o, 
     count(DISTINCT z) AS zones,
     count(DISTINCT r) AS risques,
     count(DISTINCT p) AS personnes,
     sum(CASE WHEN p.certifications_sst IS NOT NULL THEN 1 ELSE 0 END) AS certifies
WITH o, zones, risques, personnes, certifies,
     CASE WHEN risques > 0 THEN 20 ELSE 0 END AS score_identification,
     CASE WHEN zones > 0 THEN 20 ELSE 0 END AS score_cartographie,
     CASE WHEN personnes > 0 AND certifies * 1.0 / personnes > 0.7 THEN 30 
          WHEN personnes > 0 AND certifies * 1.0 / personnes > 0.5 THEN 20
          WHEN personnes > 0 THEN 10 
          ELSE 0 END AS score_formation,
     20 AS score_documentation -- Baseline
RETURN o.name AS organisation,
       o.sector_scian AS secteur,
       score_identification + score_cartographie + score_formation + score_documentation AS score_maturite_sst,
       score_identification, score_cartographie, score_formation, score_documentation
ORDER BY score_maturite_sst DESC
LIMIT 30;

-- 14.2 Indice de concentration des risques
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WITH o.sector_scian AS secteur, count(r) AS total_risques
MATCH (o2:Organization)<-[:APPARTIENT_A]-(z2:Zone)<-[:LOCALISE_DANS]-(r2:RisqueDanger)
WHERE o2.sector_scian = secteur
WITH secteur, total_risques, o2, count(r2) AS risques_org
WITH secteur, total_risques, 
     sum((risques_org * 1.0 / total_risques) * (risques_org * 1.0 / total_risques)) AS herfindahl
RETURN secteur,
       round(herfindahl * 10000, 0) AS indice_concentration_hhi,
       CASE 
           WHEN herfindahl < 0.15 THEN 'Distribué'
           WHEN herfindahl < 0.25 THEN 'Modéré'
           ELSE 'Concentré'
       END AS type_concentration
ORDER BY herfindahl DESC;

-- 14.3 Ratio personnes/risques par secteur (indicateur de couverture)
MATCH (o:Organization)
WHERE o.sector_scian IS NOT NULL
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WITH o.sector_scian AS secteur,
     count(DISTINCT r) AS risques,
     count(DISTINCT p) AS personnes
WITH secteur, sum(risques) AS total_risques, sum(personnes) AS total_personnes
RETURN secteur,
       total_personnes,
       total_risques,
       CASE WHEN total_risques > 0 
            THEN round(total_personnes * 1.0 / total_risques, 2) 
            ELSE 0 
       END AS ratio_personnes_risque
ORDER BY ratio_personnes_risque DESC;


-- ############################################################################
-- SECTION 15: MAINTENANCE ET QUALITÉ DES DONNÉES
-- ############################################################################

-- 15.1 Vérification des nœuds orphelins
MATCH (z:Zone)
WHERE NOT (z)-[:APPARTIENT_A]->(:Organization)
RETURN 'Zone orpheline' AS type, z.name AS nom, id(z) AS node_id;

-- 15.2 Vérification des propriétés nulles critiques
MATCH (o:Organization)
WHERE o.sector_scian IS NULL OR o.nb_employes IS NULL
RETURN 'Organisation incomplète' AS type, o.name AS nom, 
       o.sector_scian AS secteur, o.nb_employes AS employes;

-- 15.3 Statistiques de qualité des données
MATCH (n)
WITH labels(n)[0] AS label, count(n) AS total
RETURN label, total
ORDER BY total DESC;

-- 15.4 Comptage des relations par type
MATCH ()-[r]->()
RETURN type(r) AS relation, count(r) AS nb_relations
ORDER BY nb_relations DESC;

-- 15.5 Vérification de l'intégrité référentielle
MATCH (p:Person)
WHERE NOT (p)-[:MEMBRE_DE]->(:Team) 
   OR NOT (p)-[:TRAVAILLE_DANS]->(:Zone)
RETURN 'Personne sans équipe/zone' AS type, p.matricule AS matricule
LIMIT 20;


-- ============================================================================
-- FIN DU FICHIER - 100 REQUÊTES CYPHER SAFETYGRAPH
-- ============================================================================
-- 
-- Utilisation:
--   1. Copier les requêtes dans Neo4j Browser ou Neo4j Desktop
--   2. Pour les requêtes paramétrées, définir les paramètres avec :param
--   3. Adapter les seuils selon vos besoins spécifiques
--
-- Documentation:
--   - Neo4j Cypher Manual: https://neo4j.com/docs/cypher-manual/
--   - APOC Procedures: https://neo4j.com/labs/apoc/
--
-- Contact: SafetyGraph / EDGY-AgenticX5 / Preventera
-- ============================================================================
