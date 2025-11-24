#!/usr/bin/env python3
"""
Test connexion Neo4j réelle - EDGY-AgenticX5
"""

from neo4j import GraphDatabase
import os

def test_neo4j_connection():
    print("\n" + "=" * 60)
    print("  TEST CONNEXION NEO4J REELLE")
    print("=" * 60 + "\n")
    
    # Configuration (auth désactivée)
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")
    
    print(f"URI: {uri}")
    print(f"User: {user}")
    print(f"Auth: {'Désactivée' if not password else 'Activée'}")
    print()
    
    try:
        # Connexion sans authentification
        if password:
            driver = GraphDatabase.driver(uri, auth=(user, password))
        else:
            driver = GraphDatabase.driver(uri, auth=None)
        
        # Test de connexion
        with driver.session() as session:
            result = session.run("RETURN 'SafetyGraph connecté!' AS message, datetime() AS timestamp")
            record = result.single()
            print(f"✅ {record['message']}")
            print(f"⏰ Timestamp: {record['timestamp']}")
            
            # Info sur la base
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            for record in result:
                print(f"\n📊 Neo4j {record['name']}")
                print(f"   Version: {record['versions'][0]}")
                print(f"   Edition: {record['edition']}")
            
            # Compter les noeuds existants
            result = session.run("MATCH (n) RETURN count(n) AS total")
            total = result.single()["total"]
            print(f"\n📈 Noeuds existants: {total}")
        
        driver.close()
        print("\n" + "=" * 60)
        print("  ✅ CONNEXION NEO4J REUSSIE!")
        print("=" * 60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        print("\nSolutions possibles:")
        print("  1. Vérifiez que Neo4j est démarré (Graph DBMS actif)")
        print("  2. Vérifiez le port 7687")
        print("  3. pip install neo4j")
        return False


def create_safetygraph_schema():
    """Créer le schéma SafetyGraph"""
    print("\n" + "=" * 60)
    print("  CREATION SCHEMA SAFETYGRAPH")
    print("=" * 60 + "\n")
    
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    driver = GraphDatabase.driver(uri, auth=None)
    
    constraints = [
        ("Zone", "zone_id"),
        ("Travailleur", "matricule"),
        ("Equipement", "equipement_id"),
        ("Capteur", "capteur_id"),
        ("Incident", "incident_id"),
        ("NearMiss", "near_miss_id"),
        ("Risque", "risque_id"),
        ("Regle", "regle_id"),
        ("Formation", "formation_id"),
        ("EPI", "epi_id"),
        ("Alerte", "alerte_id"),
        ("Inspection", "inspection_id")
    ]
    
    with driver.session() as session:
        for label, prop in constraints:
            try:
                query = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
                session.run(query)
                print(f"  ✅ Contrainte {label}.{prop}")
            except Exception as e:
                print(f"  ⚠️ {label}: {e}")
    
    driver.close()
    print("\n✅ Schéma créé!")
    return True


def inject_demo_data():
    """Injecter des données de démonstration SST"""
    print("\n" + "=" * 60)
    print("  INJECTION DONNEES DEMO SST")
    print("=" * 60 + "\n")
    
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    driver = GraphDatabase.driver(uri, auth=None)
    
    with driver.session() as session:
        # Créer des zones
        zones = [
            ("ZONE-PROD-001", "Atelier Production", "production", "high"),
            ("ZONE-MAINT-001", "Atelier Maintenance", "maintenance", "medium"),
            ("ZONE-BUREAU-001", "Bureaux Administration", "bureau", "low"),
            ("ZONE-ENTREPOT-001", "Entrepôt Logistique", "stockage", "medium")
        ]
        
        for zone_id, nom, type_zone, niveau_risque in zones:
            session.run("""
                MERGE (z:Zone {zone_id: $zone_id})
                SET z.nom = $nom, z.type = $type, z.niveau_risque = $niveau_risque
            """, zone_id=zone_id, nom=nom, type=type_zone, niveau_risque=niveau_risque)
        print(f"  ✅ {len(zones)} zones créées")
        
        # Créer des travailleurs
        travailleurs = [
            ("EMP-001", "Martin Tremblay", "Opérateur Machine", "ZONE-PROD-001"),
            ("EMP-002", "Sophie Gagnon", "Technicienne Maintenance", "ZONE-MAINT-001"),
            ("EMP-003", "Jean Bergeron", "Cariste", "ZONE-ENTREPOT-001"),
            ("EMP-004", "Marie Roy", "Superviseure SST", "ZONE-BUREAU-001")
        ]
        
        for matricule, nom, poste, zone_id in travailleurs:
            session.run("""
                MERGE (t:Travailleur {matricule: $matricule})
                SET t.nom = $nom, t.poste = $poste
                WITH t
                MATCH (z:Zone {zone_id: $zone_id})
                MERGE (t)-[:TRAVAILLE_DANS]->(z)
            """, matricule=matricule, nom=nom, poste=poste, zone_id=zone_id)
        print(f"  ✅ {len(travailleurs)} travailleurs créés")
        
        # Créer des capteurs
        capteurs = [
            ("CAPT-TEMP-001", "temperature", "ZONE-PROD-001", "celsius", 22.5),
            ("CAPT-BRUIT-001", "noise", "ZONE-PROD-001", "dB", 78.0),
            ("CAPT-GAZ-001", "gas", "ZONE-MAINT-001", "ppm", 150.0),
            ("CAPT-HUM-001", "humidity", "ZONE-ENTREPOT-001", "%", 45.0)
        ]
        
        for capteur_id, type_capteur, zone_id, unite, valeur in capteurs:
            session.run("""
                MERGE (c:Capteur {capteur_id: $capteur_id})
                SET c.type = $type, c.unite = $unite, c.derniere_valeur = $valeur
                WITH c
                MATCH (z:Zone {zone_id: $zone_id})
                MERGE (c)-[:INSTALLE_DANS]->(z)
            """, capteur_id=capteur_id, type=type_capteur, zone_id=zone_id, unite=unite, valeur=valeur)
        print(f"  ✅ {len(capteurs)} capteurs créés")
        
        # Créer des risques
        risques = [
            ("RISQUE-001", "Exposition au bruit", "physical", "high", "ZONE-PROD-001"),
            ("RISQUE-002", "Chute de plain-pied", "ergonomic", "medium", "ZONE-ENTREPOT-001"),
            ("RISQUE-003", "Exposition chimique", "chemical", "high", "ZONE-MAINT-001")
        ]
        
        for risque_id, description, categorie, severite, zone_id in risques:
            session.run("""
                MERGE (r:Risque {risque_id: $risque_id})
                SET r.description = $description, r.categorie = $categorie, r.severite = $severite
                WITH r
                MATCH (z:Zone {zone_id: $zone_id})
                MERGE (z)-[:A_RISQUE]->(r)
            """, risque_id=risque_id, description=description, categorie=categorie, severite=severite, zone_id=zone_id)
        print(f"  ✅ {len(risques)} risques créés")
        
        # Créer des règles RSST
        regles = [
            ("RSST-116", "Température des lieux de travail", "RSST art. 116-120", 30.0, "temperature"),
            ("RSST-130", "Exposition au bruit", "RSST art. 130-141", 85.0, "noise"),
            ("RSST-101", "Qualité de l'air", "RSST art. 101-108", 1000.0, "gas")
        ]
        
        for regle_id, titre, reference, seuil, type_mesure in regles:
            session.run("""
                MERGE (r:Regle {regle_id: $regle_id})
                SET r.titre = $titre, r.reference = $reference, r.seuil = $seuil, r.type_mesure = $type_mesure
            """, regle_id=regle_id, titre=titre, reference=reference, seuil=seuil, type_mesure=type_mesure)
        print(f"  ✅ {len(regles)} règles RSST créées")
        
        # Compter le total
        result = session.run("MATCH (n) RETURN count(n) AS total")
        total = result.single()["total"]
        
        result = session.run("MATCH ()-[r]->() RETURN count(r) AS total")
        relations = result.single()["total"]
    
    driver.close()
    
    print(f"\n📊 Total: {total} noeuds, {relations} relations")
    print("\n" + "=" * 60)
    print("  ✅ DONNEES DEMO INJECTEES!")
    print("=" * 60 + "\n")
    return True


if __name__ == "__main__":
    # Charger .env si disponible
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    print("\n🔷 EDGY-AgenticX5 - Configuration Neo4j SafetyGraph\n")
    
    if test_neo4j_connection():
        print("\nVoulez-vous créer le schéma SafetyGraph? (o/n): ", end="")
        try:
            response = input().strip().lower()
            if response in ['o', 'oui', 'y', 'yes']:
                create_safetygraph_schema()
                
                print("\nVoulez-vous injecter des données de démo? (o/n): ", end="")
                response = input().strip().lower()
                if response in ['o', 'oui', 'y', 'yes']:
                    inject_demo_data()
        except:
            # Mode non-interactif
            create_safetygraph_schema()
            inject_demo_data()
