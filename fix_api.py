# Script de correction pour safetygraph_api.py
# Exécuter: python fix_api.py

import re

# Lire le fichier
with open('safetygraph_api.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Correction 1: Import des organisations - remplacer le bloc entier
old_org = '''    # Organisations
    for org in data.organizations:
        query = """
        CREATE (o:Organization:EDGYEntity {
            id: $id,
            name: $name,
            sector_scian: $sector_scian,
            nb_employes: $nb_employes,
            region_ssq: coalesce($region_ssq, ''),
            created_at: datetime()
        })
        """
        if db.execute_write(query, org):
            counts["organizations"] += 1'''

new_org = '''    # Organisations
    for org in data.organizations:
        query = """
        CREATE (o:Organization:EDGYEntity {
            id: $id,
            name: $name,
            sector_scian: $sector_scian,
            nb_employes: $nb_employes,
            region_ssq: $region_ssq,
            created_at: datetime()
        })
        """
        params = {
            "id": org.get("id", "ORG-" + str(int(__import__('time').time()))),
            "name": org.get("name", ""),
            "sector_scian": org.get("sector_scian", ""),
            "nb_employes": int(str(org.get("nb_employes", 0) or 0)),
            "region_ssq": org.get("region_ssq", "")
        }
        if db.execute_write(query, params):
            counts["organizations"] += 1'''

if old_org in content:
    content = content.replace(old_org, new_org)
    print("✅ Organisations corrigées")
else:
    print("⚠️ Bloc organisations non trouvé (peut-être déjà corrigé?)")

# Correction 2: Import des risques - conversion string->int
old_risk = '''    # Risks
    for risk in data.risks:
        prob = risk.get("probabilite", 1)
        grav = risk.get("gravite", 1)
        query = """
        CREATE (r:RisqueDanger:EDGYEntity {
            id: $id,
            description: $description,
            categorie: coalesce($categorie, ''),
            probabilite: $probabilite,
            gravite: $gravite,
            score: $probabilite * $gravite,
            created_at: datetime()
        })
        """
        risk["probabilite"] = prob
        risk["gravite"] = grav
        if db.execute_write(query, risk):
            counts["risks"] += 1'''

new_risk = '''    # Risks
    for risk in data.risks:
        query = """
        CREATE (r:RisqueDanger:EDGYEntity {
            id: $id,
            description: $description,
            categorie: $categorie,
            probabilite: $probabilite,
            gravite: $gravite,
            score: $score,
            created_at: datetime()
        })
        """
        try:
            prob = int(str(risk.get("probabilite", 1)))
        except:
            prob = 1
        try:
            grav = int(str(risk.get("gravite", 1)))
        except:
            grav = 1
        params = {
            "id": risk.get("id", "RISK-" + str(int(__import__('time').time()))),
            "description": risk.get("description", ""),
            "categorie": risk.get("categorie", ""),
            "probabilite": prob,
            "gravite": grav,
            "score": prob * grav
        }
        if db.execute_write(query, params):
            counts["risks"] += 1'''

if old_risk in content:
    content = content.replace(old_risk, new_risk)
    print("✅ Risques corrigés")
else:
    print("⚠️ Bloc risques non trouvé (peut-être déjà corrigé?)")

# Écrire le fichier corrigé
with open('safetygraph_api.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎉 Fichier safetygraph_api.py mis à jour!")
print("Relancez: python safetygraph_api.py")
