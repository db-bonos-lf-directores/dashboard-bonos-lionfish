import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# Configuración de página
st.set_page_config(
    page_title="Calculador de Bonos Director de Unidad | Grupo Lionfish",
    page_icon="📊",
    layout="wide"
)

# Encabezado con Logo y Título
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    try:
        st.image("logo.jpeg", width=200)
    except:
        st.write("📷 **[Grupo Lionfish]**")

with col_titulo:
    st.title("Calculador de Bonos Director de Unidad")
    st.caption("Grupo Lionfish — Evaluación Trimestral de Rentabilidad y Desempeño")

st.markdown("---")

# Conexión persistente a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargar historial guardado
try:
    df_historial = conn.read(ttl=5)
except Exception:
    df_historial = pd.DataFrame()

# Barra lateral - Filtros de Sucursal y Periodo
st.sidebar.header("⚙️ Configuración General")
sucursal = st.sidebar.selectbox("Sucursal", ["Plaza Alameda Otay", "Sucursal Río", "Sucursal Terraza"])
ano = st.sidebar.selectbox("Año Fiscal", [2026, 2025])
trimestre = st.sidebar.selectbox("Trimestre a Evaluar", ["3er Trimestre (Q3)", "1er Trimestre (Q1)", "2do Trimestre (Q2)", "4to Trimestre (Q4)"])
director_nombre = st.sidebar.text_input("Director de Unidad", "Alejandro Carrillo")
porcentaje_bolsa = st.sidebar.slider("% Bolsa A Repartir sobre Utilidad (%)", 1.0, 10.0, 5.0, 0.5) / 100.0

col_input, col_dash = st.columns([1, 1.3])

with col_input:
    st.subheader("📝 Captura de Resultados Trimestrales")
    
    st.markdown("### 💰 1. Desempeño Financiero (MXN)")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        venta_proy = st.number_input("Venta Proyectada ($ MXN)", value=15200000.0, step=100000.0, format="%.2f")
        venta_real = st.number_input("Venta Real ($ MXN)", value=14500000.0, step=100000.0, format="%.2f")
    with col_f2:
        utilidad_proy_pct = st.number_input("Utilidad Proyectada (% del Total)", value=18.0, step=0.5) / 100.0
        utilidad_real_pct = st.number_input("Utilidad Real (% del Total)", value=18.0, step=0.5) / 100.0

    utilidad_monto_real = venta_real * utilidad_real_pct
    
    st.markdown("---")
    st.markdown("### 🎯 2. Evaluación de KPIs (25.00% c/u)")
    
    # KPI 1: Ventas
    alcance_ventas = (venta_real / venta_proy) if venta_proy > 0 else 0
    kpi1_cumple = 1.0 if alcance_ventas >= 0.95 else 0.0
    st.markdown(f"**KPI 1: Ventas** (Meta: ≥ 95.00% del Presupuesto) — Alcance: **{alcance_ventas*100:.2f}%** → {'✅ Cumplido (25.00%)' if kpi1_cumple else '❌ No Cumplido (0.00%)'}")

    # KPI 2: Rotación
    col_k2_1, col_k2_2 = st.columns(2)
    with col_k2_1:
        rot_meta = st.number_input("Meta Rotación (% Máximo)", value=2.5, step=0.1) / 100.0
    with col_k2_2:
        rot_real = st.number_input("Rotación Real (% Alcanzado)", value=2.5, step=0.1) / 100.0
    kpi2_cumple = 1.0 if rot_real <= rot_meta else 0.0
    
    # KPI 3: Mystery Shopper
    col_k3_1, col_k3_2 = st.columns(2)
    with col_k3_1:
        ms_meta = st.number_input("Meta Mystery Shopper (% Mínimo)", value=90.0, step=1.0) / 100.0
    with col_k3_2:
        ms_real = st.number_input("Mystery Shopper Real (% Alcanzado)", value=92.0, step=1.0) / 100.0
    kpi3_cumple = 1.0 if ms_real >= ms_meta else 0.0

    # KPI 4: Auditoría BINNACLE
    col_k4_1, col_k4_2 = st.columns(2)
    with col_k4_1:
        aud_meta = st.number_input("Meta Auditoría Binnacle (% Mínimo)", value=95.0, step=1.0) / 100.0
    with col_k4_2:
        aud_real = st.number_input("Auditoría Real (% Alcanzado)", value=89.0, step=1.0) / 100.0
    kpi4_cumple = 1.0 if aud_real >= aud_meta else 0.0

# Regla de Escalones de Utilidad (Gatekeeper)
def calc_desbloqueo(util_pct):
    u = round(util_pct * 100, 2)
    if u < 13.0: return 0.0
    elif u < 14.0: return 0.0
    elif u < 15.0: return 0.20
    elif u < 16.0: return 0.40
    elif u < 17.0: return 0.60
    elif u < 18.0: return 0.80
    else: return 1.00

pct_desbloqueo_bolsa = calc_desbloqueo(utilidad_real_pct)
bolsa_utilidad_total = utilidad_monto_real * porcentaje_bolsa
bono_autorizado = bolsa_utilidad_total * pct_desbloqueo_bolsa

score_kpis = (kpi1_cumple * 0.25) + (kpi2_cumple * 0.25) + (kpi3_cumple * 0.25) + (kpi4_cumple * 0.25)
bono_final_recibir = bono_autorizado * score_kpis

with col_dash:
    st.subheader("📈 Resultado & Resumen de Bono")

    m1, m2, m3 = st.columns(3)
    m1.metric("Utilidad Real ($ MXN)", f"${utilidad_monto_real:,.2f} MXN", f"{utilidad_real_pct*100:.2f}% de Utilidad")
    m2.metric("Bolsa Autorizada ($ MXN)", f"${bono_autorizado:,.2f} MXN", f"{pct_desbloqueo_bolsa*100:.0f}% Desbloqueada")
    m3.metric("Bono a Recibir ($ MXN)", f"${bono_final_recibir:,.2f} MXN", f"{score_kpis*100:.0f}% de KPIs Cumplidos")

    st.markdown("---")

    # Termómetro visual
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = utilidad_real_pct * 100,
        number = {'suffix': "% Utilidad"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "<b>Margen de Utilidad Real (%) & Desbloqueo de Bolsa</b>"},
        gauge = {
            'axis': {'range': [10, 20], 'ticksuffix': "%"},
            'bar': {'color': "#2563EB"},
            'steps': [
                {'range': [10, 13], 'color': '#FEE2E2'},
                {'range': [13, 14], 'color': '#FEF3C7'},
                {'range': [14, 18], 'color': '#E0F2FE'},
                {'range': [18, 20], 'color': '#DCFCE7'}
            ],
            'threshold': {'line': {'color': "green", 'width': 4}, 'value': 18.0}
        }
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Botón para GUARDAR en Google Sheets
    if st.button("💾 GUARDAR EVALUACIÓN EN GOOGLE DRIVE", use_container_width=True, type="primary"):
        nueva_evaluacion = pd.DataFrame([{
            "Fecha Registro": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Sucursal": sucursal,
            "Año": ano,
            "Trimestre": trimestre,
            "Director": director_nombre,
            "Venta Real ($ MXN)": venta_real,
            "Utilidad Real (%)": f"{utilidad_real_pct*100:.2f}%",
            "Utilidad Real ($ MXN)": utilidad_monto_real,
            "% Desbloqueo Bolsa": f"{pct_desbloqueo_bolsa*100:.0f}%",
            "Bono Autorizado ($ MXN)": bono_autorizado,
            "% KPIs Cumplidos": f"{score_kpis*100:.0f}%",
            "Bono Final a Recibir ($ MXN)": bono_final_recibir
        }])
        
        try:
            if not df_historial.empty:
                df_updated = pd.concat([df_historial, nueva_evaluacion], ignore_index=True)
            else:
                df_updated = nueva_evaluacion
                
            conn.update(data=df_updated)
            st.success("✅ ¡Evaluación registrada permanentemente en Google Drive!")
        except Exception as err:
            st.error(f"Error al guardar: {err}")

st.markdown("---")
st.subheader("📋 Historial de Evaluaciones Guardadas")
if not df_historial.empty:
    st.dataframe(df_historial, hide_index=True, use_container_width=True)
else:
    st.info("Aún no hay evaluaciones guardadas. Al hacer clic en 'Guardar Evaluación', la información se archivará en la nube de Google Drive.")
