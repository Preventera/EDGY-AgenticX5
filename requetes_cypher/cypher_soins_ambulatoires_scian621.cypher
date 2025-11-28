// ============================================================================
// 🛡️ REQUÊTES CYPHER GÉNÉRÉES AUTOMATIQUEMENT - SafetyGraph
// ============================================================================
// Secteur: Services de soins ambulatoires (SCIAN 621)
// Profil de risques: CNESST Québec
// Lésions annuelles secteur: 25,000
// Généré le: 2025-11-28 16:48
// Générateur: EDGY-AgenticX5 / Preventera / GenAISafety
// ============================================================================

// PROFIL DE RISQUES DU SECTEUR:
// 
// 🦴 ERGONOMIQUE: 35% des lésions - Priorité CRITIQUE
// 🦠 BIOLOGIQUE: 25% des lésions - Priorité CRITIQUE
// 🧠 PSYCHOSOCIAL: 20% des lésions - Priorité ELEVE
// 🧪 CHIMIQUE: 10% des lésions - Priorité ELEVE
// 🪜 CHUTE: 5% des lésions - Priorité MOYEN
// ⚠️ VIOLENCE: 5% des lésions - Priorité ELEVE
//
// CERTIFICATIONS REQUISES: SIMDUT, Premiers soins, RCR, PDSB, Prévention infections
// EPI CRITIQUES: gants, masque, blouse, lunettes protection, écran facial
// ============================================================================



// ============================================================================
// 1. 📋 DIAGNOSTIC INITIAL - Vue d'ensemble
// ============================================================================

// 1.1 Statistiques globales de l'organisation
MATCH (o:Organization)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)
OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(r:RisqueDanger)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
RETURN o.name AS organisation,
       o.nb_employes AS employes,
       count(DISTINCT z) AS nb_zones,
       count(DISTINCT r) AS nb_risques,
       count(DISTINCT p) AS nb_travailleurs,
       round(avg(r.probabilite * r.gravite) * 100) / 100 AS score_risque_moyen
ORDER BY nb_risques DESC;

// 1.2 Distribution des zones par niveau de risque
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
RETURN z.risk_level AS niveau_risque,
       count(z) AS nb_zones,
       collect(z.name)[0..5] AS exemples_zones
ORDER BY CASE z.risk_level 
    WHEN 'critique' THEN 1 
    WHEN 'eleve' THEN 2 
    WHEN 'moyen' THEN 3 
    ELSE 4 END;

// 1.3 Répartition des risques par catégorie
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
RETURN r.categorie AS categorie,
       count(r) AS nb_risques,
       round(avg(r.probabilite * r.gravite) * 100) / 100 AS score_moyen,
       sum(CASE WHEN r.probabilite * r.gravite >= 15 THEN 1 ELSE 0 END) AS nb_tolerance_zero
ORDER BY nb_risques DESC;



// ============================================================================
// 2. 🦴 RISQUES ERGONOMIQUE - 35% des lésions (CRITIQUE)
// ============================================================================

// 2.1 Identifier tous les risques ergonomique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'ergonomique' OR toLower(r.description) CONTAINS 'lever' OR toLower(r.description) CONTAINS 'tirer' OR toLower(r.description) CONTAINS 'manutention' OR toLower(r.description) CONTAINS 'charge' OR toLower(r.description) CONTAINS 'TMS' OR toLower(r.description) CONTAINS 'répétitif' OR toLower(r.description) CONTAINS 'lombaire' OR toLower(r.description) CONTAINS 'posture')
RETURN z.name AS zone,
       r.description AS risque,
       r.probabilite AS P,
       r.gravite AS G,
       r.probabilite * r.gravite AS score,
       CASE WHEN r.probabilite * r.gravite >= 15 THEN '🔴 TOLÉRANCE ZÉRO'
            WHEN r.probabilite * r.gravite >= 10 THEN '🟠 ÉLEVÉ'
            ELSE '🟡 MODÉRÉ' END AS priorite
ORDER BY score DESC;

// 2.2 Travailleurs exposés aux risques ergonomique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'ergonomique' OR toLower(r.description) CONTAINS 'lever' OR toLower(r.description) CONTAINS 'tirer' OR toLower(r.description) CONTAINS 'manutention' OR toLower(r.description) CONTAINS 'charge' OR toLower(r.description) CONTAINS 'TMS' OR toLower(r.description) CONTAINS 'répétitif' OR toLower(r.description) CONTAINS 'lombaire' OR toLower(r.description) CONTAINS 'posture')
WITH p, collect(DISTINCT z.name) AS zones_exposition, count(r) AS nb_risques, max(r.probabilite * r.gravite) AS score_max
RETURN p.matricule AS travailleur,
       p.age_groupe AS age,
       zones_exposition,
       nb_risques,
       score_max
ORDER BY score_max DESC
LIMIT 30;

// 2.3 Zones critiques pour risques ergonomique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'ergonomique' OR toLower(r.description) CONTAINS 'lever' OR toLower(r.description) CONTAINS 'tirer' OR toLower(r.description) CONTAINS 'manutention' OR toLower(r.description) CONTAINS 'charge' OR toLower(r.description) CONTAINS 'TMS' OR toLower(r.description) CONTAINS 'répétitif' OR toLower(r.description) CONTAINS 'lombaire' OR toLower(r.description) CONTAINS 'posture')
WITH z, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE nb_risques >= 2
RETURN z.name AS zone_critique,
       z.risk_level AS niveau_zone,
       nb_risques,
       round(score_moyen * 100) / 100 AS score_moyen,
       z.epi_requis AS epi_actuels
ORDER BY score_moyen DESC;

// 2.4 Gap certifications pour risques ergonomique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'ergonomique' OR toLower(r.description) CONTAINS 'lever' OR toLower(r.description) CONTAINS 'tirer' OR toLower(r.description) CONTAINS 'manutention' OR toLower(r.description) CONTAINS 'charge' OR toLower(r.description) CONTAINS 'TMS' OR toLower(r.description) CONTAINS 'répétitif' OR toLower(r.description) CONTAINS 'lombaire' OR toLower(r.description) CONTAINS 'posture')
  AND r.probabilite * r.gravite >= 10
  AND (p.certifications_sst IS NULL OR NOT 'PDSB' IN p.certifications_sst)
RETURN DISTINCT p.matricule AS travailleur,
       z.name AS zone,
       p.certifications_sst AS certifications_actuelles,
       'PDSB' AS certifications_recommandees
LIMIT 30;



// ============================================================================
// 3. 🦠 RISQUES BIOLOGIQUE - 25% des lésions (CRITIQUE)
// ============================================================================

// 3.1 Identifier tous les risques biologique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'biologique' OR toLower(r.description) CONTAINS 'bactérie' OR toLower(r.description) CONTAINS 'sang' OR toLower(r.description) CONTAINS 'piqûre' OR toLower(r.description) CONTAINS 'moisissure' OR toLower(r.description) CONTAINS 'virus' OR toLower(r.description) CONTAINS 'infection')
RETURN z.name AS zone,
       r.description AS risque,
       r.probabilite AS P,
       r.gravite AS G,
       r.probabilite * r.gravite AS score,
       CASE WHEN r.probabilite * r.gravite >= 15 THEN '🔴 TOLÉRANCE ZÉRO'
            WHEN r.probabilite * r.gravite >= 10 THEN '🟠 ÉLEVÉ'
            ELSE '🟡 MODÉRÉ' END AS priorite
ORDER BY score DESC;

// 3.2 Travailleurs exposés aux risques biologique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'biologique' OR toLower(r.description) CONTAINS 'bactérie' OR toLower(r.description) CONTAINS 'sang' OR toLower(r.description) CONTAINS 'piqûre' OR toLower(r.description) CONTAINS 'moisissure' OR toLower(r.description) CONTAINS 'virus' OR toLower(r.description) CONTAINS 'infection')
WITH p, collect(DISTINCT z.name) AS zones_exposition, count(r) AS nb_risques, max(r.probabilite * r.gravite) AS score_max
RETURN p.matricule AS travailleur,
       p.age_groupe AS age,
       zones_exposition,
       nb_risques,
       score_max
ORDER BY score_max DESC
LIMIT 30;

// 3.3 Zones critiques pour risques biologique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'biologique' OR toLower(r.description) CONTAINS 'bactérie' OR toLower(r.description) CONTAINS 'sang' OR toLower(r.description) CONTAINS 'piqûre' OR toLower(r.description) CONTAINS 'moisissure' OR toLower(r.description) CONTAINS 'virus' OR toLower(r.description) CONTAINS 'infection')
WITH z, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE nb_risques >= 2
RETURN z.name AS zone_critique,
       z.risk_level AS niveau_zone,
       nb_risques,
       round(score_moyen * 100) / 100 AS score_moyen,
       z.epi_requis AS epi_actuels
ORDER BY score_moyen DESC;

// 3.4 Gap certifications pour risques biologique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'biologique' OR toLower(r.description) CONTAINS 'bactérie' OR toLower(r.description) CONTAINS 'sang' OR toLower(r.description) CONTAINS 'piqûre' OR toLower(r.description) CONTAINS 'moisissure' OR toLower(r.description) CONTAINS 'virus' OR toLower(r.description) CONTAINS 'infection')
  AND r.probabilite * r.gravite >= 10
  AND (p.certifications_sst IS NULL OR NOT 'SIMDUT' IN p.certifications_sst OR NOT 'Prévention infections' IN p.certifications_sst)
RETURN DISTINCT p.matricule AS travailleur,
       z.name AS zone,
       p.certifications_sst AS certifications_actuelles,
       'SIMDUT, Prévention infections' AS certifications_recommandees
LIMIT 30;



// ============================================================================
// 4. 🧠 RISQUES PSYCHOSOCIAL - 20% des lésions (ELEVE)
// ============================================================================

// 4.1 Identifier tous les risques psychosocial
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'psychosocial' OR toLower(r.description) CONTAINS 'épuisement' OR toLower(r.description) CONTAINS 'violence' OR toLower(r.description) CONTAINS 'harcèlement' OR toLower(r.description) CONTAINS 'surcharge' OR toLower(r.description) CONTAINS 'burnout' OR toLower(r.description) CONTAINS 'stress')
RETURN z.name AS zone,
       r.description AS risque,
       r.probabilite AS P,
       r.gravite AS G,
       r.probabilite * r.gravite AS score,
       CASE WHEN r.probabilite * r.gravite >= 15 THEN '🔴 TOLÉRANCE ZÉRO'
            WHEN r.probabilite * r.gravite >= 10 THEN '🟠 ÉLEVÉ'
            ELSE '🟡 MODÉRÉ' END AS priorite
ORDER BY score DESC;

// 4.2 Travailleurs exposés aux risques psychosocial
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'psychosocial' OR toLower(r.description) CONTAINS 'épuisement' OR toLower(r.description) CONTAINS 'violence' OR toLower(r.description) CONTAINS 'harcèlement' OR toLower(r.description) CONTAINS 'surcharge' OR toLower(r.description) CONTAINS 'burnout' OR toLower(r.description) CONTAINS 'stress')
WITH p, collect(DISTINCT z.name) AS zones_exposition, count(r) AS nb_risques, max(r.probabilite * r.gravite) AS score_max
RETURN p.matricule AS travailleur,
       p.age_groupe AS age,
       zones_exposition,
       nb_risques,
       score_max
ORDER BY score_max DESC
LIMIT 30;

// 4.3 Zones critiques pour risques psychosocial
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'psychosocial' OR toLower(r.description) CONTAINS 'épuisement' OR toLower(r.description) CONTAINS 'violence' OR toLower(r.description) CONTAINS 'harcèlement' OR toLower(r.description) CONTAINS 'surcharge' OR toLower(r.description) CONTAINS 'burnout' OR toLower(r.description) CONTAINS 'stress')
WITH z, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE nb_risques >= 2
RETURN z.name AS zone_critique,
       z.risk_level AS niveau_zone,
       nb_risques,
       round(score_moyen * 100) / 100 AS score_moyen,
       z.epi_requis AS epi_actuels
ORDER BY score_moyen DESC;

// 4.4 Gap certifications pour risques psychosocial
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'psychosocial' OR toLower(r.description) CONTAINS 'épuisement' OR toLower(r.description) CONTAINS 'violence' OR toLower(r.description) CONTAINS 'harcèlement' OR toLower(r.description) CONTAINS 'surcharge' OR toLower(r.description) CONTAINS 'burnout' OR toLower(r.description) CONTAINS 'stress')
  AND r.probabilite * r.gravite >= 10
  AND (p.certifications_sst IS NULL OR NOT 'SIMDUT' IN p.certifications_sst OR NOT 'Premiers soins' IN p.certifications_sst)
RETURN DISTINCT p.matricule AS travailleur,
       z.name AS zone,
       p.certifications_sst AS certifications_actuelles,
       'SIMDUT, Premiers soins, RCR' AS certifications_recommandees
LIMIT 30;



// ============================================================================
// 5. 🧪 RISQUES CHIMIQUE - 10% des lésions (ELEVE)
// ============================================================================

// 5.1 Identifier tous les risques chimique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'chimique' OR toLower(r.description) CONTAINS 'acide' OR toLower(r.description) CONTAINS 'silice' OR toLower(r.description) CONTAINS 'poussière' OR toLower(r.description) CONTAINS 'amiante' OR toLower(r.description) CONTAINS 'gaz' OR toLower(r.description) CONTAINS 'chimique' OR toLower(r.description) CONTAINS 'vapeur' OR toLower(r.description) CONTAINS 'solvant')
RETURN z.name AS zone,
       r.description AS risque,
       r.probabilite AS P,
       r.gravite AS G,
       r.probabilite * r.gravite AS score,
       CASE WHEN r.probabilite * r.gravite >= 15 THEN '🔴 TOLÉRANCE ZÉRO'
            WHEN r.probabilite * r.gravite >= 10 THEN '🟠 ÉLEVÉ'
            ELSE '🟡 MODÉRÉ' END AS priorite
ORDER BY score DESC;

// 5.2 Travailleurs exposés aux risques chimique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'chimique' OR toLower(r.description) CONTAINS 'acide' OR toLower(r.description) CONTAINS 'silice' OR toLower(r.description) CONTAINS 'poussière' OR toLower(r.description) CONTAINS 'amiante' OR toLower(r.description) CONTAINS 'gaz' OR toLower(r.description) CONTAINS 'chimique' OR toLower(r.description) CONTAINS 'vapeur' OR toLower(r.description) CONTAINS 'solvant')
WITH p, collect(DISTINCT z.name) AS zones_exposition, count(r) AS nb_risques, max(r.probabilite * r.gravite) AS score_max
RETURN p.matricule AS travailleur,
       p.age_groupe AS age,
       zones_exposition,
       nb_risques,
       score_max
ORDER BY score_max DESC
LIMIT 30;

// 5.3 Zones critiques pour risques chimique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'chimique' OR toLower(r.description) CONTAINS 'acide' OR toLower(r.description) CONTAINS 'silice' OR toLower(r.description) CONTAINS 'poussière' OR toLower(r.description) CONTAINS 'amiante' OR toLower(r.description) CONTAINS 'gaz' OR toLower(r.description) CONTAINS 'chimique' OR toLower(r.description) CONTAINS 'vapeur' OR toLower(r.description) CONTAINS 'solvant')
WITH z, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE nb_risques >= 2
RETURN z.name AS zone_critique,
       z.risk_level AS niveau_zone,
       nb_risques,
       round(score_moyen * 100) / 100 AS score_moyen,
       z.epi_requis AS epi_actuels
ORDER BY score_moyen DESC;

// 5.4 Gap certifications pour risques chimique
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'chimique' OR toLower(r.description) CONTAINS 'acide' OR toLower(r.description) CONTAINS 'silice' OR toLower(r.description) CONTAINS 'poussière' OR toLower(r.description) CONTAINS 'amiante' OR toLower(r.description) CONTAINS 'gaz' OR toLower(r.description) CONTAINS 'chimique' OR toLower(r.description) CONTAINS 'vapeur' OR toLower(r.description) CONTAINS 'solvant')
  AND r.probabilite * r.gravite >= 10
  AND (p.certifications_sst IS NULL OR NOT 'SIMDUT' IN p.certifications_sst)
RETURN DISTINCT p.matricule AS travailleur,
       z.name AS zone,
       p.certifications_sst AS certifications_actuelles,
       'SIMDUT' AS certifications_recommandees
LIMIT 30;



// ============================================================================
// 6. 🪜 RISQUES CHUTE - 5% des lésions (MOYEN)
// ============================================================================

// 6.1 Identifier tous les risques chute
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'chute' OR toLower(r.description) CONTAINS 'échelle' OR toLower(r.description) CONTAINS 'escalier' OR toLower(r.description) CONTAINS 'hauteur' OR toLower(r.description) CONTAINS 'plateforme' OR toLower(r.description) CONTAINS 'chute' OR toLower(r.description) CONTAINS 'échafaud' OR toLower(r.description) CONTAINS 'toiture' OR toLower(r.description) CONTAINS 'glissade')
RETURN z.name AS zone,
       r.description AS risque,
       r.probabilite AS P,
       r.gravite AS G,
       r.probabilite * r.gravite AS score,
       CASE WHEN r.probabilite * r.gravite >= 15 THEN '🔴 TOLÉRANCE ZÉRO'
            WHEN r.probabilite * r.gravite >= 10 THEN '🟠 ÉLEVÉ'
            ELSE '🟡 MODÉRÉ' END AS priorite
ORDER BY score DESC;

// 6.2 Travailleurs exposés aux risques chute
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'chute' OR toLower(r.description) CONTAINS 'échelle' OR toLower(r.description) CONTAINS 'escalier' OR toLower(r.description) CONTAINS 'hauteur' OR toLower(r.description) CONTAINS 'plateforme' OR toLower(r.description) CONTAINS 'chute' OR toLower(r.description) CONTAINS 'échafaud' OR toLower(r.description) CONTAINS 'toiture' OR toLower(r.description) CONTAINS 'glissade')
WITH p, collect(DISTINCT z.name) AS zones_exposition, count(r) AS nb_risques, max(r.probabilite * r.gravite) AS score_max
RETURN p.matricule AS travailleur,
       p.age_groupe AS age,
       zones_exposition,
       nb_risques,
       score_max
ORDER BY score_max DESC
LIMIT 30;

// 6.3 Zones critiques pour risques chute
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'chute' OR toLower(r.description) CONTAINS 'échelle' OR toLower(r.description) CONTAINS 'escalier' OR toLower(r.description) CONTAINS 'hauteur' OR toLower(r.description) CONTAINS 'plateforme' OR toLower(r.description) CONTAINS 'chute' OR toLower(r.description) CONTAINS 'échafaud' OR toLower(r.description) CONTAINS 'toiture' OR toLower(r.description) CONTAINS 'glissade')
WITH z, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE nb_risques >= 2
RETURN z.name AS zone_critique,
       z.risk_level AS niveau_zone,
       nb_risques,
       round(score_moyen * 100) / 100 AS score_moyen,
       z.epi_requis AS epi_actuels
ORDER BY score_moyen DESC;

// 6.4 Gap certifications pour risques chute
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND (r.categorie = 'chute' OR toLower(r.description) CONTAINS 'échelle' OR toLower(r.description) CONTAINS 'escalier' OR toLower(r.description) CONTAINS 'hauteur' OR toLower(r.description) CONTAINS 'plateforme' OR toLower(r.description) CONTAINS 'chute' OR toLower(r.description) CONTAINS 'échafaud' OR toLower(r.description) CONTAINS 'toiture' OR toLower(r.description) CONTAINS 'glissade')
  AND r.probabilite * r.gravite >= 10
  AND (p.certifications_sst IS NULL)
RETURN DISTINCT p.matricule AS travailleur,
       z.name AS zone,
       p.certifications_sst AS certifications_actuelles,
       '' AS certifications_recommandees
LIMIT 30;



// ============================================================================
// 🚨 ALERTES ET SURVEILLANCE PROACTIVE
// ============================================================================

// 🔴 ALERTE CRITIQUE: Risques Tolérance Zéro (score >= 15)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND r.probabilite * r.gravite >= 15
RETURN '🔴 TOLÉRANCE ZÉRO' AS alerte,
       o.name AS organisation,
       z.name AS zone,
       r.categorie AS type_risque,
       r.description AS description,
       r.probabilite * r.gravite AS score
ORDER BY score DESC;

// 🟠 ALERTE: Concentration de risques (hotspots)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
WITH z, o, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE nb_risques >= 3
RETURN z.name AS zone_hotspot,
       o.name AS organisation,
       nb_risques,
       round(score_moyen * 100) / 100 AS score_moyen,
       CASE WHEN score_moyen >= 12 THEN '🔴 CRITIQUE'
            WHEN score_moyen >= 8 THEN '🟠 ÉLEVÉ'
            ELSE '🟡 MODÉRÉ' END AS niveau_alerte
ORDER BY score_moyen DESC;

// 👤 ALERTE: Jeunes travailleurs (18-24) en zones à risque
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND p.age_groupe = '18-24'
  AND r.probabilite * r.gravite >= 10
RETURN '⚠️ JEUNE TRAVAILLEUR EXPOSÉ' AS alerte,
       p.matricule AS travailleur,
       z.name AS zone,
       collect(DISTINCT r.categorie) AS types_risques,
       max(r.probabilite * r.gravite) AS score_max;

// 👴 ALERTE: Travailleurs expérimentés (55+) - risques ergonomiques
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND p.age_groupe IN ['55-64', '65+']
  AND r.categorie = 'ergonomique'
RETURN '⚠️ TRAVAILLEUR EXPÉRIMENTÉ - RISQUE ERGO' AS alerte,
       p.matricule AS travailleur,
       z.name AS zone,
       r.description AS risque;



// ============================================================================
// ✅ CONFORMITÉ ET AUDIT - RSST, Loi sur les infirmières, Protocoles infectieux
// ============================================================================

// Vérification EPI par zone à risque
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND z.risk_level IN ['critique', 'eleve']
RETURN z.name AS zone,
       z.risk_level AS niveau,
       z.epi_requis AS epi_definis,
       CASE WHEN z.epi_requis IS NULL OR size(z.epi_requis) = 0 
            THEN '❌ EPI NON DÉFINIS - ACTION REQUISE'
            WHEN size(z.epi_requis) < 3
            THEN '⚠️ EPI POSSIBLEMENT INCOMPLETS'
            ELSE '✅ OK' END AS statut_epi;

// Taux de certification par équipe
MATCH (o:Organization)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
WITH t, o,
     count(p) AS total,
     sum(CASE WHEN p.certifications_sst IS NOT NULL AND size(p.certifications_sst) > 0 THEN 1 ELSE 0 END) AS certifies
RETURN o.name AS organisation,
       t.name AS equipe,
       total AS nb_membres,
       certifies AS nb_certifies,
       round(certifies * 100.0 / total) AS taux_certification,
       CASE WHEN certifies * 100.0 / total < 80 THEN '⚠️ FORMATION REQUISE' ELSE '✅' END AS statut
ORDER BY taux_certification ASC;

// Vérification certifications requises secteur: SIMDUT, Premiers soins, RCR, PDSB, Prévention infections
MATCH (o:Organization)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
WITH p, p.certifications_sst AS certs
WHERE certs IS NULL OR size([c IN certs WHERE c IN ['SIMDUT', 'Premiers soins', 'RCR', 'PDSB', 'Prévention infections']]) < 2
RETURN p.matricule AS travailleur,
       certs AS certifications_actuelles,
       'SIMDUT, Premiers soins, RCR' AS certifications_prioritaires
LIMIT 50;

// Score de maturité SST par organisation
MATCH (o:Organization)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WITH o,
     count(DISTINCT z) AS zones,
     count(DISTINCT r) AS risques,
     count(DISTINCT p) AS personnes,
     sum(CASE WHEN p.certifications_sst IS NOT NULL THEN 1 ELSE 0 END) AS certifies,
     sum(CASE WHEN z.epi_requis IS NOT NULL THEN 1 ELSE 0 END) AS zones_epi
WITH o, zones, risques, personnes, certifies, zones_epi,
     CASE WHEN zones > 0 THEN 20 ELSE 0 END +
     CASE WHEN risques > 0 THEN 20 ELSE 0 END +
     CASE WHEN personnes > 0 AND certifies * 1.0 / personnes > 0.5 THEN 30 ELSE 15 END +
     CASE WHEN zones > 0 AND zones_epi * 1.0 / zones > 0.7 THEN 20 ELSE 10 END AS score_maturite
RETURN o.name AS organisation,
       score_maturite AS 'Score /90',
       CASE WHEN score_maturite >= 70 THEN '✅ MATURE'
            WHEN score_maturite >= 50 THEN '🟡 EN PROGRESSION'
            ELSE '🔴 À AMÉLIORER' END AS niveau_maturite;



// ============================================================================
// 🤖 REQUÊTES POUR AGENTS IA - SafetyGraph
// ============================================================================

// Agent VisionAI - Zones prioritaires surveillance caméra
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND z.risk_level = 'critique'
  AND r.categorie IN ['ergonomique', 'biologique', 'psychosocial']
RETURN DISTINCT z.name AS zone_surveillance,
       collect(DISTINCT r.categorie) AS types_risques,
       'VisionAI' AS agent,
       'Détection comportements à risque en temps réel' AS mission;

// Agent ErgoAI - Postes à analyser
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
MATCH (p:Person)-[:TRAVAILLE_DANS]->(z)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
  AND r.categorie = 'ergonomique'
WITH z, count(DISTINCT p) AS nb_exposes, avg(r.probabilite * r.gravite) AS score
WHERE nb_exposes >= 3
RETURN z.name AS poste_analyse,
       nb_exposes AS travailleurs_exposes,
       round(score * 100) / 100 AS score_ergo,
       'ErgoAI' AS agent,
       'Analyse posturale et recommandations' AS mission
ORDER BY score DESC;

// Agent AlertAI - Déclencheurs d'alertes
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
WITH z, o, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score_moyen
WHERE score_moyen >= 10 OR nb_risques >= 5
RETURN o.name AS organisation,
       z.name AS zone,
       nb_risques,
       round(score_moyen * 100) / 100 AS score,
       CASE 
           WHEN score_moyen >= 15 THEN 'CRITIQUE - Alerte immédiate'
           WHEN score_moyen >= 12 THEN 'ÉLEVÉ - Alerte superviseur'
           ELSE 'MODÉRÉ - Surveillance renforcée'
       END AS action_alertai
ORDER BY score DESC;

// Agent PredictAI - Features ML pour prédiction
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(t:Team)<-[:MEMBRE_DE]-(p:Person)
WITH o,
     count(DISTINCT z) AS nb_zones,
     count(DISTINCT r) AS nb_risques,
     count(DISTINCT t) AS nb_equipes,
     count(DISTINCT p) AS nb_personnes,
     avg(r.probabilite * r.gravite) AS score_moyen,
     sum(CASE WHEN r.categorie = 'ergonomique' THEN 1 ELSE 0 END) AS risques_cat1,
     sum(CASE WHEN r.categorie = 'biologique' THEN 1 ELSE 0 END) AS risques_cat2,
     sum(CASE WHEN r.probabilite * r.gravite >= 15 THEN 1 ELSE 0 END) AS risques_TZ
RETURN o.name AS organisation,
       o.nb_employes AS employes,
       nb_zones, nb_risques, nb_equipes, nb_personnes,
       round(score_moyen * 100) / 100 AS score_moyen,
       risques_cat1 AS 'ergonomique',
       risques_cat2 AS 'biologique',
       risques_TZ AS tolerance_zero,
       round(nb_risques * 1.0 / CASE WHEN nb_zones > 0 THEN nb_zones ELSE 1 END * 100) / 100 AS densite_risques;

// Agent ComplyAI - Écarts de conformité
MATCH (o:Organization)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
OPTIONAL MATCH (o)<-[:APPARTIENT_A]-(z:Zone)
OPTIONAL MATCH (z)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WITH o, count(DISTINCT z) AS zones, count(r) AS risques
WHERE zones > 0 AND risques = 0
RETURN o.name AS organisation,
       zones AS zones_sans_risques_documentes,
       'ComplyAI' AS agent,
       '⚠️ Audit de conformité requis - Risques non documentés' AS action;



// ============================================================================
// 📊 DONNÉES POUR DASHBOARD ET VISUALISATION
// ============================================================================

// Données graphique - Risques par catégorie (barres/donut)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
RETURN r.categorie AS label,
       count(r) AS value,
       round(avg(r.probabilite * r.gravite) * 100) / 100 AS score_moyen
ORDER BY value DESC;

// Données graphique - Zones par niveau de risque (donut)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
RETURN z.risk_level AS label, count(z) AS value
ORDER BY CASE z.risk_level 
    WHEN 'critique' THEN 1 WHEN 'eleve' THEN 2 
    WHEN 'moyen' THEN 3 ELSE 4 END;

// Données matrice de risques (scatter plot P x G)
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
RETURN r.probabilite AS x,
       r.gravite AS y,
       count(r) AS size,
       r.categorie AS category
ORDER BY x, y;

// Données KPI cards
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
WITH count(DISTINCT o) AS orgs,
     count(DISTINCT z) AS zones,
     count(r) AS risques,
     sum(CASE WHEN r.probabilite * r.gravite >= 15 THEN 1 ELSE 0 END) AS TZ,
     avg(r.probabilite * r.gravite) AS score_moy
RETURN orgs AS nb_organisations,
       zones AS nb_zones,
       risques AS nb_risques,
       TZ AS risques_tolerance_zero,
       round(score_moy * 100) / 100 AS score_risque_moyen,
       round(TZ * 100.0 / risques) AS pct_critique;

// Top 10 organisations par risque
MATCH (o:Organization)<-[:APPARTIENT_A]-(z:Zone)<-[:LOCALISE_DANS]-(r:RisqueDanger)
WHERE o.sector_scian IN ['621', '622', '623', '624', '621-624']
WITH o, count(r) AS nb_risques, avg(r.probabilite * r.gravite) AS score
RETURN o.name AS organisation, nb_risques, round(score * 100) / 100 AS score_moyen
ORDER BY score DESC
LIMIT 10;



// ============================================================================
// FIN DES REQUÊTES GÉNÉRÉES POUR SCIAN 621 - SOINS AMBULATOIRES
// Total: ~50 requêtes personnalisées selon profil CNESST
// ============================================================================
