# Script de correction pour les organisations
import re

with open('safetygraph_api.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Chercher et remplacer le bloc organisations avec regex
old_pattern = r'# Organisations\s+for org in data\.organizations:\s+query = """\s+CREATE \(o:Organization:EDGYEntity \{\s+id: \$id,\s+name: \$name,\s+sector_scian: \$sector_scian,\s+nb_employes: \$nb_employes,\s+region_ssq: coalesce\(\$region_ssq, \'\'\),\s+created_at: datetime\(\)\s+\}\)\s+"""\s+if db\.execute_write\(query, org\):\s+counts\["organizations"\] \+= 1'

new_block = '''# Organisations
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

# Méthode simple: chercher la ligne spécifique
lines = content.split('\n')
new_lines = []
i = 0
found = False

while i < len(lines):
    line = lines[i]
    
    # Chercher le début du bloc organisations
    if '# Organisations' in line and 'for org in data.organizations' in lines[i+1] if i+1 < len(lines) else False:
        # Trouver la fin du bloc (jusqu'à counts["organizations"])
        j = i
        while j < len(lines) and 'counts["organizations"]' not in lines[j]:
            j += 1
        j += 1  # Inclure la ligne counts
        
        # Remplacer par le nouveau bloc
        new_lines.append('    # Organisations')
        new_lines.append('    for org in data.organizations:')
        new_lines.append('        query = """')
        new_lines.append('        CREATE (o:Organization:EDGYEntity {')
        new_lines.append('            id: $id,')
        new_lines.append('            name: $name,')
        new_lines.append('            sector_scian: $sector_scian,')
        new_lines.append('            nb_employes: $nb_employes,')
        new_lines.append('            region_ssq: $region_ssq,')
        new_lines.append('            created_at: datetime()')
        new_lines.append('        })')
        new_lines.append('        """')
        new_lines.append('        params = {')
        new_lines.append('            "id": org.get("id", "ORG-" + str(int(__import__(\'time\').time()))),')
        new_lines.append('            "name": org.get("name", ""),')
        new_lines.append('            "sector_scian": org.get("sector_scian", ""),')
        new_lines.append('            "nb_employes": int(str(org.get("nb_employes", 0) or 0)),')
        new_lines.append('            "region_ssq": org.get("region_ssq", "")')
        new_lines.append('        }')
        new_lines.append('        if db.execute_write(query, params):')
        new_lines.append('            counts["organizations"] += 1')
        
        i = j
        found = True
        print("✅ Bloc organisations trouvé et remplacé!")
    else:
        new_lines.append(line)
        i += 1

if not found:
    print("⚠️ Bloc non trouvé, essai méthode 2...")
    # Méthode 2: remplacement direct
    content = content.replace(
        'region_ssq: coalesce($region_ssq, \'\'),',
        'region_ssq: $region_ssq,'
    )
    content = content.replace(
        'if db.execute_write(query, org):',
        '''params = {
            "id": org.get("id", "ORG-" + str(int(__import__('time').time()))),
            "name": org.get("name", ""),
            "sector_scian": org.get("sector_scian", ""),
            "nb_employes": int(str(org.get("nb_employes", 0) or 0)),
            "region_ssq": org.get("region_ssq", "")
        }
        if db.execute_write(query, params):'''
    )
    with open('safetygraph_api.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Correction appliquée (méthode 2)")
else:
    with open('safetygraph_api.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

print("\n🎉 Terminé! Relancez: python safetygraph_api.py")
