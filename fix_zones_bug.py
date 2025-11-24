#!/usr/bin/env python3
"""
PATCH: Correction du bug /api/v1/zones

Exécutez ce script pour corriger le fichier api.py
"""

import re

def apply_patch():
    print("\n" + "=" * 50)
    print("  PATCH: Correction /api/v1/zones")
    print("=" * 50)
    
    # Lire le fichier api.py
    try:
        with open("api.py", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("\n  [ERREUR] api.py non trouve!")
        print("  Executez depuis le dossier EDGY-AgenticX5")
        return False
    
    # Ancien code à remplacer
    old_code = '''    def get_zones(self) -> List[Dict]:
        """Récupérer toutes les zones"""
        if self.mock_mode:
            return [{"zone_id": "ZONE-DEMO", "nom": "Zone Demo", "niveau_risque": "medium"}]
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (z:Zone)
                OPTIONAL MATCH (z)-[:A_RISQUE]->(r:Risque)
                RETURN z.zone_id as zone_id, z.nom as nom, z.type as type,
                       z.niveau_risque as niveau_risque,
                       collect(r.description) as risques
            """)
            return [dict(record) for record in result]'''
    
    # Nouveau code corrigé
    new_code = '''    def get_zones(self) -> List[Dict]:
        """Récupérer toutes les zones"""
        if self.mock_mode:
            return [{"zone_id": "ZONE-DEMO", "nom": "Zone Demo", "type": None, "niveau_risque": "medium", "risques": []}]
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (z:Zone)
                    OPTIONAL MATCH (z)-[:A_RISQUE]->(r:Risque)
                    RETURN z.zone_id as zone_id, z.nom as nom, z.type as type,
                           z.niveau_risque as niveau_risque,
                           collect(COALESCE(r.description, '')) as risques
                """)
                zones = []
                for record in result:
                    zone = {
                        "zone_id": record["zone_id"] or "unknown",
                        "nom": record["nom"],
                        "type": record["type"],
                        "niveau_risque": record["niveau_risque"],
                        "risques": [r for r in record["risques"] if r]
                    }
                    zones.append(zone)
                return zones
        except Exception as e:
            print(f"Erreur get_zones: {e}")
            return []'''
    
    # Appliquer le patch
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open("api.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("\n  [OK] Patch applique avec succes!")
        print("  Redemarrez l'API: python api.py")
        return True
    else:
        print("\n  [INFO] Le code a deja ete modifie ou differe")
        print("  Application du patch manuel...")
        
        # Essayer de trouver et remplacer de manière plus flexible
        pattern = r'def get_zones\(self\) -> List\[Dict\]:.*?return \[dict\(record\) for record in result\]'
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_code.strip(), content, flags=re.DOTALL)
            
            with open("api.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            print("\n  [OK] Patch applique (methode alternative)!")
            return True
        else:
            print("\n  [WARN] Impossible d'appliquer le patch automatiquement")
            print("  Voir les instructions manuelles ci-dessous")
            return False


def show_manual_fix():
    print("\n" + "=" * 50)
    print("  CORRECTION MANUELLE")
    print("=" * 50)
    print("""
Dans api.py, trouvez la methode get_zones() et remplacez:

    return [dict(record) for record in result]

Par:

    zones = []
    for record in result:
        zone = {
            "zone_id": record["zone_id"] or "unknown",
            "nom": record["nom"],
            "type": record["type"],
            "niveau_risque": record["niveau_risque"],
            "risques": [r for r in record["risques"] if r]
        }
        zones.append(zone)
    return zones
""")


if __name__ == "__main__":
    success = apply_patch()
    if not success:
        show_manual_fix()
    
    print("\n" + "=" * 50)
    print("  Apres correction, redemarrez l'API:")
    print("  python api.py")
    print("=" * 50 + "\n")
