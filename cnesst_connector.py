"""
CNESST Data Connector - EDGY-AgenticX5
======================================
Connecteur pour charger et traiter les données réelles CNESST
793K+ lésions professionnelles (2017-2023)

Auteur: Mario Genest - GenAISafety/Preventera
"""

import pandas as pd
import sqlite3
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CNESSTConnector:
    """Connecteur pour accéder aux données CNESST réelles"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.cnesst_dir = self.data_dir / "cnesst"
        self.db_path = self.data_dir / "safetyagentic_behaviorx.db"
        self._cached_data: Optional[pd.DataFrame] = None
        self._stats_cache: Dict = {}
        
    def get_available_files(self) -> List[Dict]:
        """Liste les fichiers CSV CNESST disponibles"""
        files = []
        if self.cnesst_dir.exists():
            for f in self.cnesst_dir.glob("lesions-*.csv"):
                files.append({
                    "filename": f.name,
                    "year": self._extract_year(f.name),
                    "size_mb": round(f.stat().st_size / (1024*1024), 2),
                    "path": str(f)
                })
        return sorted(files, key=lambda x: x["year"])
    
    def _extract_year(self, filename: str) -> int:
        """Extrait l'année du nom de fichier"""
        import re
        match = re.search(r'(\d{4})', filename)
        return int(match.group(1)) if match else 0
    
    def load_year(self, year: int) -> pd.DataFrame:
        """Charge les données d'une année spécifique"""
        patterns = [
            f"lesions-{year}.csv",
            f"lesions-{year} (1).csv"
        ]
        
        for pattern in patterns:
            filepath = self.cnesst_dir / pattern
            if filepath.exists():
                logger.info(f"Chargement {filepath}...")
                try:
                    df = pd.read_csv(filepath, encoding='utf-8', low_memory=False)
                    logger.info(f"✅ {len(df)} enregistrements chargés pour {year}")
                    return df
                except UnicodeDecodeError:
                    df = pd.read_csv(filepath, encoding='latin-1', low_memory=False)
                    logger.info(f"✅ {len(df)} enregistrements chargés pour {year} (latin-1)")
                    return df
        
        logger.warning(f"⚠️ Fichier non trouvé pour {year}")
        return pd.DataFrame()
    
    def load_all_years(self, years: List[int] = None) -> pd.DataFrame:
        """Charge toutes les années (ou une sélection)"""
        if self._cached_data is not None and years is None:
            return self._cached_data
        
        if years is None:
            years = [2017, 2018, 2019, 2020, 2021, 2022, 2023]
        
        all_data = []
        for year in years:
            df = self.load_year(year)
            if not df.empty:
                df['year'] = year
                all_data.append(df)
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            if years is None or len(years) == 7:
                self._cached_data = combined
            logger.info(f"✅ Total: {len(combined)} enregistrements combinés")
            return combined
        
        return pd.DataFrame()
    
    def get_summary_statistics(self) -> Dict:
        """Calcule les statistiques globales"""
        if "summary" in self._stats_cache:
            return self._stats_cache["summary"]
        
        files = self.get_available_files()
        total_records = 0
        years_data = []
        
        for f in files:
            try:
                # Compter les lignes sans charger tout le fichier
                with open(f["path"], 'r', encoding='utf-8', errors='ignore') as file:
                    count = sum(1 for _ in file) - 1  # -1 pour l'en-tête
                total_records += count
                years_data.append({
                    "year": f["year"],
                    "incidents": count,
                    "size_mb": f["size_mb"]
                })
            except Exception as e:
                logger.error(f"Erreur comptage {f['filename']}: {e}")
        
        stats = {
            "total_incidents": total_records,
            "years_available": [f["year"] for f in files],
            "years_count": len(files),
            "total_size_mb": sum(f["size_mb"] for f in files),
            "by_year": years_data,
            "source": "CNESST - Données Québec",
            "last_update": datetime.now().isoformat()
        }
        
        self._stats_cache["summary"] = stats
        return stats
    
    def get_sector_statistics(self, scian_prefix: str = None) -> Dict:
        """Statistiques par secteur SCIAN"""
        df = self.load_all_years()
        if df.empty:
            return {"error": "Aucune donnée disponible"}
        
        # Identifier la colonne SCIAN (peut varier selon les fichiers)
        scian_col = None
        for col in ['SECTEUR_SCIAN', 'SCIAN', 'sector_scian', 'CODE_SCIAN']:
            if col in df.columns:
                scian_col = col
                break
        
        if scian_col is None:
            # Essayer de deviner
            for col in df.columns:
                if 'SCIAN' in col.upper() or 'SECTEUR' in col.upper():
                    scian_col = col
                    break
        
        if scian_col is None:
            return {
                "error": "Colonne SCIAN non trouvée",
                "columns_available": list(df.columns)[:20]
            }
        
        if scian_prefix:
            df = df[df[scian_col].astype(str).str.startswith(str(scian_prefix))]
        
        stats = df[scian_col].value_counts().head(20).to_dict()
        
        return {
            "column_used": scian_col,
            "filter": scian_prefix,
            "total_filtered": len(df),
            "top_sectors": stats
        }
    
    def get_columns_info(self) -> Dict:
        """Retourne les informations sur les colonnes disponibles"""
        df = self.load_year(2023)  # Charger une année pour voir la structure
        if df.empty:
            df = self.load_year(2022)
        
        if df.empty:
            return {"error": "Impossible de charger les données"}
        
        return {
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "sample_row": df.iloc[0].to_dict() if len(df) > 0 else {},
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    
    def query_incidents(
        self,
        year: int = None,
        sector: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Requête flexible sur les incidents"""
        if year:
            df = self.load_year(year)
        else:
            df = self.load_all_years()
        
        if df.empty:
            return []
        
        if sector:
            # Filtrer par secteur
            for col in df.columns:
                if 'SCIAN' in col.upper() or 'SECTEUR' in col.upper():
                    df = df[df[col].astype(str).str.contains(str(sector), na=False)]
                    break
        
        # Limiter et convertir
        df_limited = df.head(limit)
        
        # Nettoyer les NaN pour JSON
        df_limited = df_limited.fillna("")
        
        return df_limited.to_dict('records')
    
    def get_yearly_trends(self) -> Dict:
        """Tendances par année"""
        stats = self.get_summary_statistics()
        
        trends = {
            "years": [],
            "incidents": [],
            "growth_rate": []
        }
        
        by_year = stats.get("by_year", [])
        for i, year_data in enumerate(by_year):
            trends["years"].append(year_data["year"])
            trends["incidents"].append(year_data["incidents"])
            
            if i > 0:
                prev = by_year[i-1]["incidents"]
                current = year_data["incidents"]
                growth = ((current - prev) / prev * 100) if prev > 0 else 0
                trends["growth_rate"].append(round(growth, 2))
            else:
                trends["growth_rate"].append(0)
        
        return trends


# ============================================================
# API ENDPOINTS POUR FASTAPI
# ============================================================

def create_cnesst_routes(app, connector: CNESSTConnector):
    """Ajoute les routes CNESST à l'application FastAPI"""
    
    @app.get("/cnesst/status")
    async def cnesst_status():
        """Statut de la connexion CNESST"""
        files = connector.get_available_files()
        return {
            "status": "connected" if files else "no_data",
            "files_count": len(files),
            "years": [f["year"] for f in files],
            "total_size_mb": sum(f["size_mb"] for f in files)
        }
    
    @app.get("/cnesst/summary")
    async def cnesst_summary():
        """Statistiques résumées CNESST"""
        return connector.get_summary_statistics()
    
    @app.get("/cnesst/columns")
    async def cnesst_columns():
        """Structure des données CNESST"""
        return connector.get_columns_info()
    
    @app.get("/cnesst/sectors")
    async def cnesst_sectors(prefix: str = None):
        """Statistiques par secteur"""
        return connector.get_sector_statistics(prefix)
    
    @app.get("/cnesst/trends")
    async def cnesst_trends():
        """Tendances annuelles"""
        return connector.get_yearly_trends()
    
    @app.get("/cnesst/incidents")
    async def cnesst_incidents(
        year: int = None,
        sector: str = None,
        limit: int = 100
    ):
        """Requête sur les incidents"""
        incidents = connector.query_incidents(year, sector, limit)
        return {
            "count": len(incidents),
            "limit": limit,
            "filters": {"year": year, "sector": sector},
            "data": incidents
        }
    
    return app


# ============================================================
# SCRIPT DE TEST
# ============================================================

if __name__ == "__main__":
    # Test du connecteur
    connector = CNESSTConnector(data_dir="data")
    
    print("\n" + "="*60)
    print("🔍 TEST CNESST CONNECTOR")
    print("="*60)
    
    # 1. Fichiers disponibles
    files = connector.get_available_files()
    print(f"\n📁 Fichiers disponibles: {len(files)}")
    for f in files:
        print(f"   - {f['year']}: {f['filename']} ({f['size_mb']} Mo)")
    
    # 2. Statistiques globales
    print("\n📊 Statistiques globales:")
    stats = connector.get_summary_statistics()
    print(f"   Total incidents: {stats.get('total_incidents', 'N/A'):,}")
    print(f"   Années: {stats.get('years_available', [])}")
    print(f"   Taille totale: {stats.get('total_size_mb', 0):.1f} Mo")
    
    # 3. Structure des données
    print("\n📋 Colonnes disponibles:")
    cols = connector.get_columns_info()
    if "columns" in cols:
        print(f"   {len(cols['columns'])} colonnes")
        print(f"   Premières: {cols['columns'][:10]}...")
    
    # 4. Tendances
    print("\n📈 Tendances annuelles:")
    trends = connector.get_yearly_trends()
    for i, year in enumerate(trends.get("years", [])):
        incidents = trends.get("incidents", [])[i]
        growth = trends.get("growth_rate", [])[i]
        print(f"   {year}: {incidents:,} incidents ({growth:+.1f}%)")
    
    print("\n" + "="*60)
    print("✅ Test terminé avec succès!")
    print("="*60)
