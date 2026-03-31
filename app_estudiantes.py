import streamlit as st
import pandas as pd
import os
import unicodedata

# --- 1. CONFIGURACION DE PAGINA E INSTRUCCIONES ---
st.set_page_config(
    page_title="Portal de Consulta Estudiantil - UNICEN",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. FUNCION DE NORMALIZACION DE TEXTO PARA BUSQUEDA (QUITAR ACENTOS) ---
def clean_accent_and_upper(text):
    if not isinstance(text, str): return ""
    text = text.strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

# --- 3. ESTILOS CSS PERSONALIZADOS (MODO PREMIUM UNICEN) ---
st.markdown("""
    <style>
    .stTextInput label p {
        color: #4DB8FF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }

    div[data-baseweb="input"] > div {
        border-radius: 12px !important;
        border: 1.5px solid #1E3A5F !important;
        background-color: #002140 !important;
        transition: all 0.3s ease-in-out;
    }
    div[data-baseweb="input"] > div:focus-within {
        border-color: #4DB8FF !important;
        background-color: #003460 !important;
        box-shadow: 0 0 12px rgba(77, 184, 255, 0.4) !important;
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #002b49 0%, #004578 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid #4DB8FF !important;
        padding: 14px 24px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        width: 100%;
        box-shadow: 0 0 15px rgba(77, 184, 255, 0.2) !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #4DB8FF 0%, #004578 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(77, 184, 255, 0.5) !important;
        color: #001529 !important;
    }
    
    .stApp { background-color: #001529; color: #E2E8F0; }
    [data-testid="stSidebar"] { background-color: #002140; border-right: 1px solid #143559; }
    h1, h2, h3, h4, p, span { font-family: 'Segoe UI', Inter, sans-serif; }
    
    .stTextInput>div>div>input { color: #FFFFFF !important; font-size: 18px !important; text-align: center; }
    
    .msg-box { padding: 16px 20px; border-radius: 8px; margin-bottom: 25px; font-weight: 600; text-align: center; }
    .msg-success { background-color: #003B24; color: #E8F5E9; border-left: 5px solid #00E676; }
    .msg-error { background-color: #4A0000; color: #FFEBEE; border-left: 5px solid #FF1744; }
    .msg-warning { background-color: #5C4000; color: #FFF8E1; border-left: 5px solid #FFC400; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 4. CONSTANTES ---
DATA_FILE = "datos_estudiantes.xlsx"
LOGO_FILE = "Logo.png" # El nombre es exacto ahora
ADMIN_PASSWORD = st.secrets["admin_password"] 

def formal_message(text, msg_type="info", container=st):
    container.markdown(f'<div class="msg-box msg-{msg_type}">{text}</div>', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data(filepath):
    try:
        if os.path.exists(filepath):
            df = pd.read_excel(filepath, dtype=str)
            df.columns = [str(col).strip().upper() for col in df.columns]
            df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
            return df
    except Exception: return None
    return None

# --- 5. LOGICA DE ACCESO SECRETO (MODO ADMIN) ---
query_params = st.query_params
show_admin = query_params.get("view") == "admin"

if show_admin:
    with st.sidebar:
        # Mostramos el logo también aquí para el admin
        if os.path.exists(LOGO_FILE): 
            st.image(LOGO_FILE, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center;'>Panel de Control</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #143559; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        admin_pass = st.text_input("Ingrese la Clave Maestra", type="password")
        
        if admin_pass == ADMIN_PASSWORD:
            formal_message("ADMINISTRADOR IDENTIFICADO", msg_type="success")
            st.markdown("<br><h3>Carga de Archivos</h3>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Actualizar Excel Estudiantil", type=["xlsx"])
            
            if uploaded_file and st.button("PROCESAR Y REEMPLAZAR"):
                try:
                    with open(DATA_FILE, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.cache_data.clear()
                    formal_message("BASE DE DATOS ACTUALIZADA.", msg_type="success")
                except PermissionError:
                    formal_message("ERROR: Archivo en uso por Excel.", msg_type="error")
                except Exception as e:
                    formal_message("Error inesperado al guardar.", msg_type="error")
        elif admin_pass != "": 
            formal_message("Clave Incorrecta", msg_type="error")

# --- 6. INTERFAZ PRINCIPAL DEL ESTUDIANTE (CON LOGO VISIBLE PARA TODOS) ---
# Usamos columnas para centrar el logo
col_logo_cent, _ = st.columns([1, 4]) # Lo ponemos a la izquierda o centro
with col_logo_cent:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, width=200) # Tamaño controlado

st.markdown("""
    <div style='text-align: center; margin-top: 0px; margin-bottom: 40px;'>
        <h1 style='font-size: 42px; font-weight: 900; letter-spacing: -1px; margin-bottom: 0;'>PORTAL DE CONSULTA ESTUDIANTIL</h1>
        <p style='color: #4DB8FF; font-size: 18px; letter-spacing: 2px; font-weight: 500;'>UNIVERSIDAD CENTRAL - UNICEN</p>
    </div>
""", unsafe_allow_html=True)

df = load_data(DATA_FILE)

if df is not None and not df.empty:
    col_carnet = next((c for c in df.columns if c in ["CARNET", "CI", "C.I.", "DOCUMENTO"]), None)
    col_nombres = next((c for c in df.columns if c in ["NOMBRES", "NOMBBRES", "NOMBRE", "ESTUDIANTE"]), None)
    col_apellidos = next((c for c in df.columns if c in ["APELLIDOS", "APELLIDO", "AP. PATERNO", "PATERNO"]), None)
    col_unicodigo = next((c for c in df.columns if "UNICODIGO" in c or "CODIGO" in c), None)

    if col_carnet and col_nombres and col_unicodigo:
        st.markdown("<div style='text-align: center; margin-bottom: 30px;'><h3 style='margin-bottom: 10px;'>INGRESE SUS DATOS PARA VALIDACIÓN</h3></div>", unsafe_allow_html=True)
        
        _, col_search_area, _ = st.columns([1, 1.8, 1])
        with col_search_area:
            search_carnet = st.text_input("INTRODUZCA SU NÚMERO DE CARNET / CI", placeholder="Ej: 9876543").strip()
            search_nombre = st.text_input("INTRODUZCA SU NOMBRE(S) (Sin tildes preferentemente)", placeholder="Ej: JUAN PABLO").strip()
            st.markdown("<br>", unsafe_allow_html=True)
            run_btn = st.button("VALIDAR Y MOSTRAR MI UNICÓDIGO")

        if run_btn:
            if not search_carnet or not search_nombre:
                formal_message("ALERTA: Debe completar ambos campos.", msg_type="warning")
            else:
                records_by_carnet = df[df[col_carnet] == search_carnet]
                if records_by_carnet.empty:
                    formal_message("NO ENCONTRADO: El carnet no existe.", msg_type="error")
                else:
                    search_nombre_clean = clean_accent_and_upper(search_nombre)
                    student_found = None
                    for _, row in records_by_carnet.iterrows():
                        db_name_clean = clean_accent_and_upper(str(row[col_nombres]))
                        if search_nombre_clean in db_name_clean:
                            student_found = row
                            break
                    
                    if student_found is not None:
                        nombre_val = str(student_found.get(col_nombres, '')).strip()
                        apellido_val = str(student_found.get(col_apellidos, '')).strip() if col_apellidos else ""
                        nombre_completo = f"{nombre_val} {apellido_val}".strip().upper()
                        carrera = str(student_found.get('CARRERA', 'NO DEFINIDA')).upper()
                        semestre = str(student_found.get('SEMESTRE', 'N/A')).upper()
                        unicodigo = str(student_found.get(col_unicodigo, 'N/A')).upper()

                        st.markdown(f"""
                        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
                        <div style="background-color: #002b49; border-radius: 16px; overflow: hidden; box-shadow: 0 25px 50px rgba(0,0,0,0.6); border: 1px solid #143559;">
                            <div style="background: linear-gradient(135deg, #001f36 0%, #004578 100%); padding: 35px; border-bottom: 4px solid #4DB8FF;">
                                <div style="display: flex; justify-content: space-between; align-items: top;">
                                    <div>
                                        <p style="color: #4DB8FF; font-size: 13px; font-weight: 800; margin-bottom: 5px; letter-spacing: 4px;">IDENTIDAD VERIFICADA</p>
                                        <h2 style="color: white; margin: 0; font-size: 30px; font-weight: 900; line-height: 1.1;">{nombre_completo}</h2>
                                    </div>
                                    <div style="text-align: right;"><span class="material-icons" style="font-size: 55px; color: #4DB8FF; opacity: 0.9;">verified</span></div>
                                </div>
                            </div>
                            <div style="padding: 40px; display: flex; flex-wrap: wrap; gap: 40px; align-items: center;">
                                <div style="flex: 1.2; min-width: 280px;">
                                    <div style="display: grid; grid-template-columns: 1fr; gap: 20px;">
                                        <div><p style="color: #4DB8FF; font-size: 11px; font-weight: 800;">CARRERA / FACULTAD</p><p style="color: white; font-size: 18px; font-weight: 600;">{carrera}</p></div>
                                        <div><p style="color: #4DB8FF; font-size: 11px; font-weight: 800;">SEMESTRE ACTUAL</p><p style="color: white; font-size: 18px; font-weight: 600;">{semestre}</p></div>
                                        <div><p style="color: #4DB8FF; font-size: 11px; font-weight: 800;">IDENTIFICACIÓN CI</p><p style="color: white; font-size: 18px; font-weight: 600;">{search_carnet}</p></div>
                                    </div>
                                </div>
                                <div style="flex: 1; min-width: 250px; background-color: rgba(0,0,0,0.3); border-radius: 12px; padding: 30px; text-align: center; border: 1px solid rgba(77, 184, 255, 0.2);">
                                    <p style="color: #4DB8FF; font-size: 14px; letter-spacing: 4px; font-weight: 900;">UNICÓDIGO</p>
                                    <h1 style="color: #00E676; font-size: 72px; font-weight: 900; text-shadow: 0 0 25px rgba(0, 230, 118, 0.5);">{unicodigo}</h1>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        formal_message("ACCESO DENEGADO: El nombre no coincide.", msg_type="error")
    else: formal_message("ERROR ESTRUCTURA: Falta columna crítica.", msg_type="error")
else: formal_message("MANTENIMIENTO: Base de datos no disponible.", msg_type="error")
