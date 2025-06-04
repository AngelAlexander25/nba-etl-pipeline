# nba_dashboard.py - Dashboard Streamlit para NBA
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

# Configuración de página
st.set_page_config(
    page_title="NBA Analytics Dashboard",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_nba_data():
    """Cargar datos desde SQLite"""
    try:
        conn = sqlite3.connect("data/nba_analytics.db")
        
        # Cargar datos principales
        players_df = pd.read_sql("SELECT * FROM nba_players", conn)
        team_stats = pd.read_sql("SELECT * FROM nba_team_stats", conn)
        position_stats = pd.read_sql("SELECT * FROM nba_position_stats", conn)
        top_performers = pd.read_sql("SELECT * FROM nba_top_performers", conn)
        
        conn.close()
        return players_df, team_stats, position_stats, top_performers
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None, None, None, None
    
def main():
    # Header
    st.title("🏀 NBA Analytics Dashboard")
    st.markdown("---")
    
    # Cargar datos
    players_df, team_stats, position_stats, top_performers = load_nba_data()
    
    if players_df is None:
        st.error("No se pudieron cargar los datos. Ejecuta primero el pipeline ETL.")
        st.stop()
    
    # Sidebar con filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de equipos
    teams = st.sidebar.multiselect(
        "Seleccionar Equipos",
        options=sorted(players_df['TEAM_ABBREVIATION'].unique()),
        default=sorted(players_df['TEAM_ABBREVIATION'].unique())[:5]
    )
    
    # Filtro de posiciones
    positions = st.sidebar.multiselect(
        "Seleccionar Posiciones",
        options=sorted(players_df['POSITION'].dropna().unique()),
        default=sorted(players_df['POSITION'].dropna().unique())
    )
    
    # Filtro de era
    eras = st.sidebar.multiselect(
        "Era de Baloncesto",
        options=players_df['BASKETBALL_ERA'].unique(),
        default=players_df['BASKETBALL_ERA'].unique()
    )
    
    # Aplicar filtros
    filtered_df = players_df[
        (players_df['TEAM_ABBREVIATION'].isin(teams)) &
        (players_df['POSITION'].isin(positions)) &
        (players_df['BASKETBALL_ERA'].isin(eras))
    ]
    
    # Métricas principales
    st.header("📊 Métricas Principales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Jugadores", f"{len(filtered_df):,}")
    
    with col2:
        avg_efficiency = filtered_df['EFFICIENCY'].mean()
        st.metric("⚡ Eficiencia Promedio", f"{avg_efficiency:.1f}")
    
    with col3:
        avg_points = filtered_df['PTS'].mean()
        st.metric("🏀 Puntos Promedio", f"{avg_points:.1f}")
    
    with col4:
        active_players = len(filtered_df[filtered_df['CAREER_STATUS'] == 'Active'])
        st.metric("🟢 Jugadores Activos", f"{active_players:,}")
    
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Distribución de Eficiencia")
        fig_hist = px.histogram(
            filtered_df, 
            x='EFFICIENCY', 
            nbins=30,
            title="Distribución de Eficiencia de Jugadores"
        )
        fig_hist.update_layout(xaxis_title="Eficiencia", yaxis_title="Número de Jugadores")
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("🏀 Estadísticas por Posición")
        pos_avg = filtered_df.groupby('POSITION')[['PTS', 'REB', 'AST']].mean().reset_index()
        fig_pos = px.bar(
            pos_avg.melt(id_vars='POSITION', var_name='Stat', value_name='Average'),
            x='POSITION', 
            y='Average', 
            color='Stat',
            title="Promedios por Posición",
            barmode='group'
        )
        st.plotly_chart(fig_pos, use_container_width=True)
    
    # Segunda fila de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Equipos por Eficiencia")
        team_efficiency = filtered_df.groupby('TEAM_ABBREVIATION')['EFFICIENCY'].mean().reset_index()
        team_efficiency = team_efficiency.sort_values('EFFICIENCY', ascending=False).head(10)
        
        fig_teams = px.bar(
            team_efficiency,
            x='TEAM_ABBREVIATION',
            y='EFFICIENCY',
            title="Eficiencia Promedio por Equipo"
        )
        st.plotly_chart(fig_teams, use_container_width=True)
    
    with col2:
        st.subheader("📏 Altura vs Peso por Posición")
        
        # CORREGIR: Filtrar datos válidos para el scatter plot
        scatter_data = filtered_df.dropna(subset=['HEIGHT_CM', 'WEIGHT_KG', 'EFFICIENCY'])
        
        if len(scatter_data) > 0:
            fig_scatter = px.scatter(
                scatter_data,
                x='HEIGHT_CM',
                y='WEIGHT_KG',
                color='POSITION',
                size='EFFICIENCY',
                hover_data=['PLAYER_FIRST_NAME', 'PLAYER_LAST_NAME'],
                title="Distribución Física por Posición"
            )
            fig_scatter.update_layout(xaxis_title="Altura (cm)", yaxis_title="Peso (kg)")
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No hay datos suficientes para mostrar el gráfico de dispersión")
    
    # Análisis de Draft
    st.header("🎯 Análisis de Draft")
    col1, col2 = st.columns(2)
    
    with col1:
        draft_data = filtered_df[filtered_df['DRAFT_YEAR'].notna()]
        if len(draft_data) > 0:
            draft_success = draft_data['DRAFT_SUCCESS'].value_counts().reset_index()
            
            fig_draft = px.pie(
                draft_success,
                values='count',
                names='DRAFT_SUCCESS',
                title="Distribución de Éxito en Draft"
            )
            st.plotly_chart(fig_draft, use_container_width=True)
        else:
            st.info("No hay datos de draft disponibles")
    
    with col2:
        if len(draft_data) > 0:
            draft_by_round = draft_data.groupby('DRAFT_ROUND')['EFFICIENCY'].mean().reset_index()
            
            fig_round = px.bar(
                draft_by_round,
                x='DRAFT_ROUND',
                y='EFFICIENCY',
                title="Eficiencia Promedio por Ronda de Draft"
            )
            st.plotly_chart(fig_round, use_container_width=True)
        else:
            st.info("No hay datos de draft por ronda disponibles")
    
    # Tabla de Top Performers
    st.header("🌟 Top Performers")
    
    # Filtrar top performers con datos válidos
    valid_performers = top_performers.dropna(subset=['EFFICIENCY'])
    if len(valid_performers) > 0:
        st.dataframe(
            valid_performers.head(20),
            use_container_width=True
        )
    else:
        st.info("No hay datos de top performers disponibles")
    
    # Análisis temporal
    with st.expander("📅 Análisis Temporal"):
        st.subheader("Evolución por Era")
        
        era_stats = filtered_df.groupby('BASKETBALL_ERA')[['PTS', 'REB', 'AST', 'EFFICIENCY']].mean().reset_index()
        
        if len(era_stats) > 0:
            fig_era = px.line(
                era_stats.melt(id_vars='BASKETBALL_ERA', var_name='Metric', value_name='Average'),
                x='BASKETBALL_ERA',
                y='Average',
                color='Metric',
                title="Evolución de Estadísticas por Era"
            )
            st.plotly_chart(fig_era, use_container_width=True)
        else:
            st.info("No hay suficientes datos para el análisis temporal")
    
    # Sección de insights
    st.header("🔍 Insights del Análisis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏆 Mejores Equipos")
        top_teams = filtered_df.groupby('TEAM_ABBREVIATION')['EFFICIENCY'].mean().nlargest(5)
        for team, eff in top_teams.items():
            st.write(f"**{team}**: {eff:.1f}")
    
    with col2:
        st.subheader("📈 Posiciones más Eficientes")
        top_positions = filtered_df.groupby('POSITION')['EFFICIENCY'].mean().nlargest(5)
        for pos, eff in top_positions.items():
            st.write(f"**{pos}**: {eff:.1f}")
    
    with col3:
        st.subheader("⭐ Era Dorada")
        top_eras = filtered_df.groupby('BASKETBALL_ERA')['EFFICIENCY'].mean().nlargest(3)
        for era, eff in top_eras.items():
            st.write(f"**{era}**: {eff:.1f}")

if __name__ == "__main__":
    main()