# export_web_data.py - Exportar datos del ETL para la web
import sqlite3
import pandas as pd
import json
import os
from datetime import datetime

def export_nba_data_for_web():
    """Exportar datos procesados del ETL a formato JSON para la web"""
    
    try:
        print("🏀 Exportando datos NBA para dashboard web...")
        
        # Verificar que existe la base de datos
        if not os.path.exists("data/nba_analytics.db"):
            print("❌ No se encontró la base de datos del ETL")
            print("📋 Ejecuta primero: python nba_pipeline.py")
            return False
        
        # Conectar a la base de datos del ETL
        conn = sqlite3.connect("data/nba_analytics.db")
        
        # Cargar datos principales (ajustado para evitar errores de columnas)
        query = """
        SELECT 
            PLAYER_FIRST_NAME,
            PLAYER_LAST_NAME,
            TEAM_ABBREVIATION,
            POSITION,
            PTS,
            REB,
            AST,
            EFFICIENCY,
            BASKETBALL_ERA,
            CAREER_STATUS
        FROM nba_players 
        WHERE EFFICIENCY IS NOT NULL 
        AND PTS IS NOT NULL
        ORDER BY EFFICIENCY DESC
        LIMIT 500
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"✅ Cargados {len(df)} registros de jugadores")
        
        if len(df) == 0:
            print("❌ No se encontraron datos válidos")
            return False
        
        # Convertir a formato web-friendly
        web_data = []
        for _, player in df.iterrows():
            web_data.append({
                "PLAYER_FIRST_NAME": str(player['PLAYER_FIRST_NAME']),
                "PLAYER_LAST_NAME": str(player['PLAYER_LAST_NAME']),
                "TEAM_ABBREVIATION": str(player['TEAM_ABBREVIATION']),
                "POSITION": str(player['POSITION']),
                "PTS": float(player['PTS']) if pd.notna(player['PTS']) else 0,
                "REB": float(player['REB']) if pd.notna(player['REB']) else 0,
                "AST": float(player['AST']) if pd.notna(player['AST']) else 0,
                "EFFICIENCY": float(player['EFFICIENCY']) if pd.notna(player['EFFICIENCY']) else 0,
                "BASKETBALL_ERA": str(player['BASKETBALL_ERA']),
                "CAREER_STATUS": str(player['CAREER_STATUS'])
            })
        
        # Crear archivo JavaScript con los datos
        js_content = f"""// Datos NBA generados automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
const NBA_DATA = {json.dumps(web_data, indent=2)};

// Función para cargar datos en el dashboard
function loadNBADataFromFile() {{
    return NBA_DATA;
}}

console.log('📊 Datos NBA cargados:', NBA_DATA.length, 'jugadores');
"""
        
        # Guardar archivo JavaScript
        with open('nba_data.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"✅ Datos exportados a 'nba_data.js'")
        print(f"📊 Total de jugadores: {len(web_data)}")
        
        # Estadísticas del export
        teams = len(set(p['TEAM_ABBREVIATION'] for p in web_data))
        positions = len(set(p['POSITION'] for p in web_data))
        eras = len(set(p['BASKETBALL_ERA'] for p in web_data))
        active_players = len([p for p in web_data if p['CAREER_STATUS'] == 'Active'])
        
        print(f"🏀 Equipos: {teams}")
        print(f"📍 Posiciones: {positions}")
        print(f"📅 Eras: {eras}")
        print(f"🟢 Jugadores activos: {active_players}")
        
        # Mostrar algunos datos de ejemplo
        print("\n📋 Muestra de datos exportados:")
        for i, player in enumerate(web_data[:3]):
            print(f"  {i+1}. {player['PLAYER_FIRST_NAME']} {player['PLAYER_LAST_NAME']} ({player['TEAM_ABBREVIATION']}) - Eficiencia: {player['EFFICIENCY']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exportando datos: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🌐 NBA Dashboard - Exportación para Web")
    print("=" * 50)
    
    # Exportar datos
    if export_nba_data_for_web():
        print("\n🎉 ¡Exportación completada exitosamente!")
        print("\n📋 Archivos generados:")
        print("  ✅ nba_data.js - Datos para el dashboard web")
        print("\n🚀 Próximos pasos:")
        print("  1. Crea 'index.html' con el código del dashboard")
        print("  2. Modifica la línea para usar datos reales")
        print("  3. Sube ambos archivos a GitHub Pages")
    else:
        print("\n💥 Falló la exportación")
        print("🔍 Verifica que hayas ejecutado 'python nba_pipeline.py' primero")