import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de página
st.set_page_config(
    page_title="Dashboard de Bonos - Director de Unidad | Grupo Lionfish",
    page_icon="📊",
    layout="wide"
)

# Título del Dashboard
st.title("📊 Dashboard & Calculador de Bono - Director de Unidad")
st.caption("Grupo Lionfish — Evaluación Trimestral de Rendimiento y Utilidad")
st.markdown("---")

# Barra lateral - Filtros de Sucursal y Periodo
st.sidebar.header("⚙️ Configuración")
sucursal = st.sidebar.selectbox("Sucursal", ["Plaza Alameda Otay", "Sucursal Río", "Sucursal Terraza"])
ano = st.sidebar.selectbox("Año Fiscal", [2026, 2025])
trimestre = st.sidebar.selectbox("Trimestre a Evaluar", ["3er Trimestre (Q3)", "1er Trimestre (Q1)", "2do Trimestre (Q2)", "4to Trimestre (Q4)"])
director_nombre = st.sidebar.text_input("Director de Unidad", "Alejandro Carrillo")
porcentaje_bolsa = st.sidebar.slider("% Bolsa A Repartir sobre Utilidad", 1.0, 10.0, 5.0, 0.5) / 100.0

col_input, col_dash = st.columns([1, 1.3])

with col_input:
    st.subheader("📝 Captura de Resultados Trimestrales")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        venta_proy = st.number_input("Venta Proyectada ($)", value=15200000.0, step=100000.0)
        venta_real = st.number_input("Venta Real ($)", value=14500000.0, step=100000.0)
    with col_f2:
        utilidad_proy_pct = st.number_input("Utilidad Proyectada (%)", value=18.0, step=0.5) / 100.0
        utilidad_real_pct = st.number_input("Utilidad Real (%)", value=18.0, step=0.5) / 100.0

    utilidad_monto_real = venta_real * utilidad_real_pct
    
    st.markdown("---")
    st.markdown("### 🎯 Evaluación de KPIs (25% c/u)")
    
    # KPI 1: Ventas
    alcance_ventas = (venta_real / venta_proy) if venta_proy > 0 else 0
    kpi1_cumple = 1.0 if alcance_ventas >= 0.95 else 0.0
    st.markdown(f"**KPI 1: Ventas** (Meta: ≥95%) — Alcance: **{alcance_ventas*100:.2f}%** → {'✅ Cumplido (25%)' if kpi1_cumple else '❌ No Cumplido (0%)'}")

    # KPI 2: Rotación
    col_k2_1, col_k2_2 = st.columns(2)
    with col_k2_1:
        rot_meta = st.number_input("Meta Rotación (%)", value=2.5, step=0.1) / 100.0
    with col_k2_2:
        rot_real = st.number_input("Rotación Real (%)", value=2.5, step=0.1) / 100.0
    kpi2_cumple = 1.0 if rot_real <= rot_meta else 0.0
    
    # KPI 3: Mystery Shopper
    col_k3_1, col_k3_2 = st.columns(2)
    with col_k3_1:
        ms_meta = st.number_input("Meta Mystery Shopper (%)", value=90.0, step=1.0) / 100.0
    with col_k3_2:
        ms_real = st.number_input("Mystery Shopper Real (%)", value=92.0, step=1.0) / 100.0
    kpi3_cumple = 1.0 if ms_real >= ms_meta else 0.0

    # KPI 4: Auditoría Binnacle
    col_k4_1, col_k4_2 = st.columns(2)
    with col_k4_1:
        aud_meta = st.number_input("Meta Auditoría Binnacle (%)", value=95.0, step=1.0) / 100.0
    with col_k4_2:
        aud_real = st.number_input("Auditoría Real (%)", value=89.0, step=1.0) / 100.0
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
    m1.metric("Utilidad Real", f"${utilidad_monto_real:,.2f}", f"{utilidad_real_pct*100:.1f}%")
    m2.metric("Bolsa Autorizada", f"${bono_autorizado:,.2f}", f"{pct_desbloqueo_bolsa*100:.0f}% Desbloqueada")
    m3.metric("Bono a Recibir", f"${bono_final_recibir:,.2f}", f"{score_kpis*100:.0f}% KPIs")

    st.markdown("---")

    # Termómetro visual de Utilidad
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = utilidad_real_pct * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "<b>Margen de Utilidad (%) & Desbloqueo de Bolsa</b>"},
        gauge = {
            'axis': {'range': [10, 20]},
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

    # Tabla interactiva
    kpi_df = pd.DataFrame([
        {"KPI": "1. Ventas", "Meta": "≥95%", "Real": f"{alcance_ventas*100:.1f}%", "Estatus": "✅ Cumplido" if kpi1_cumple else "❌ No Cumplido", "Monto": f"${bono_autorizado*0.25*kpi1_cumple:,.2f}"},
        {"KPI": "2. Rotación", "Meta": f"≤{rot_meta*100:.1f}%", "Real": f"{rot_real*100:.1f}%", "Estatus": "✅ Cumplido" if kpi2_cumple else "❌ No Cumplido", "Monto": f"${bono_autorizado*0.25*kpi2_cumple:,.2f}"},
        {"KPI": "3. Mystery Shopper", "Meta": f"≥{ms_meta*100:.0f}%", "Real": f"{ms_real*100:.1f}%", "Estatus": "✅ Cumplido" if kpi3_cumple else "❌ No Cumplido", "Monto": f"${bono_autorizado*0.25*kpi3_cumple:,.2f}"},
        {"KPI": "4. Auditoría Binnacle", "Meta": f"≥{aud_meta*100:.0f}%", "Real": f"{aud_real*100:.1f}%", "Estatus": "✅ Cumplido" if kpi4_cumple else "❌ No Cumplido", "Monto": f"${bono_autorizado*0.25*kpi4_cumple:,.2f}"},
    ])
    st.dataframe(kpi_df, hide_index=True, use_container_width=True)
