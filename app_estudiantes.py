import streamlit as st
import pandas as pd
import json
import os

# --- 1. CONFIGURACION DE PAGINA E INSTRUCCIONES ---
st.set_page_config(
    page_title="Portal de Consulta Estudiantil",
    layout="wide",
    initial_sidebar_state="collapsed"  # <-- ESTA ES LA PALABRA MÁGICA
)

# --- 2. ESTILOS CSS PERSONALIZADOS (MODO OSCURO INSTITUCIONAL) ---
# Inyección de CSS personalizado para un diseño Flat y corporativo
st.markdown("""
    <style>
    /* Diseño plano y bordes redondeados para la caja de texto (Buscador) */
    div[data-baseweb="input"] > div {
        border-radius: 8px !important;
        border: 1.5px solid #e0e0e0 !important;
        background-color: #f9fbfd !important;
        box-shadow: none !important;
        transition: all 0.3s ease-in-out;
    }
    
    /* Efecto al hacer clic en el buscador (Focus) */
    div[data-baseweb="input"] > div:focus-within {
        border-color: #4DB8FF !important;
        background-color: #ffffff !important;
        box-shadow: 0 0 8px rgba(77, 184, 255, 0.3) !important;
    }

    /* DISEÑO DEL BOTÓN PRINCIPAL ACTUALIZADO PARA QUE NO SE CORTE EL TEXTO */
    div.stButton > button {
        background-color: #002b49 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px 15px !important; 
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        width: 100% !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        font-size: 13px !important; 
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }

    /* EFECTO DE SALTAR (POPPING) AL PASAR EL MOUSE (HOVER) */
    div.stButton > button:hover {
        background-color: #004d80 !important; 
        transform: translateY(-5px) scale(1.03) !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2) !important;
    }
    
    /* Efecto al hacer CLIC (Active) para que se sienta que se presiona */
    div.stButton > button:active {
        transform: translateY(-1px) scale(0.99) !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }
    
    /* Estilizar las pestañas (Tabs) para que se vean más limpias */
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        color: #555555 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #002b49 !important;
        border-bottom-color: #4DB8FF !important;
        border-bottom-width: 3px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Se aplica un diseño corporativo sobrio: azul oscuro, blanco, gris claro y detalles celeste institucional.
# Se deshabilitan explícitamente los estilos predeterminados de alertas para evitar emojis de Streamlit.
CSS = """
<style>
/* Fondo principal y color de texto general */
.stApp {
    background-color: #001529; /* Azul institucional muy oscuro */
    color: #E2E8F0; /* Gris claro para legibilidad */
}

/* Panel lateral del administrador */
[data-testid="stSidebar"] {
    background-color: #002140;
    border-right: 1px solid #143559;
}

/* Tipografía formal para todo el sistema */
h1, h2, h3, h4, h5, p, span {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
h1, h2, h3 {
    color: #FFFFFF !important;
}

/* Ocultar elementos predeterminados que pueden contener emojis o un estilo indeseado */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Tarjeta principal del estudiante (Estilo Card) */
.student-card {
    background-color: #002A50;
    border-left: 6px solid #48CAE4; /* Detalle en azul claro */
    padding: 24px;
    border-radius: 6px;
    margin-bottom: 30px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
}
.student-name {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.student-detail {
    color: #90E0EF;
    font-size: 16px;
    margin-bottom: 6px;
    font-weight: 500;
}
.student-detail strong {
    color: #E2E8F0;
    margin-right: 5px;
}

/* Campos de entrada de texto generales */
.stTextInput>div>div>input {
    background-color: #003460;
    color: #FFFFFF;
    border: 1px solid #00509E;
    font-size: 16px;
}

/* Campo de entrada de Carnet Específico (Aumentar tamaño de números) */
div[data-testid="stTextInput"] input {
    font-size: 24px !important;
    font-weight: bold;
    text-align: center;
    letter-spacing: 2px;
}

/* Pestañas (Tabs) */
.stTabs [data-baseweb="tab-list"] {
    gap: 30px;
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 25px;
    color: #A0C4FF;
    font-size: 18px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    color: #FFFFFF;
    border-bottom: 3px solid #48CAE4;
    font-weight: 600;
}

/* Tablas y DataFrames */
[data-testid="stDataFrame"] > div {
    border-radius: 6px;
    border: 1px solid #1E3A5F;
}

/* Cajas de mensajes formales personalizados (Sin emojis) */
.msg-box {
    padding: 14px 18px;
    border-radius: 4px;
    margin-bottom: 20px;
    font-weight: 500;
    font-size: 15px;
}
.msg-success { background-color: #003B24; color: #E8F5E9; border-left: 4px solid #00E676; }
.msg-error { background-color: #4A0000; color: #FFEBEE; border-left: 4px solid #FF1744; }
.msg-info { background-color: #002B4D; color: #E1F5FE; border-left: 4px solid #00B0FF; }
.msg-warning { background-color: #5C4000; color: #FFF8E1; border-left: 4px solid #FFC400; }

/* Tablas HTML Personalizadas (Mejora visual profunda) */
.custom-table-container {
    overflow-x: auto;
    border-radius: 8px;
    border: 1px solid #1E3A5F;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    text-align: left;
    background-color: #002b49;
    color: #E2E8F0;
}
.custom-table thead tr {
    background-color: #001f36;
    color: #4DB8FF;
    border-bottom: 2px solid #48CAE4;
}
.custom-table th {
    padding: 15px 20px;
    font-weight: bold;
    text-transform: uppercase;
    white-space: nowrap;
}
.custom-table td {
    padding: 12px 20px;
    border-bottom: 1px solid #143559;
    white-space: nowrap;
}
.custom-table tbody tr:hover {
    background-color: #004578 !important;
}
.custom-table tbody tr:nth-of-type(even) {
    background-color: #002140;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --- 3. CONSTANTES Y RUTAS RELATIVAS ---
DATA_FILE = "datos_estudiantes.xlsx"
CONFIG_FILE = "config.json"
LOGO_FILE = "logo_unicen.png"
ADMIN_PASSWORD = "4834735012vrY" # Contraseña por defecto para el panel

# --- 4. FUNCIONES AUXILIARES ---
def formal_message(text, msg_type="info", container=st):
    """Muestra un mensaje estilizado garantizando la ausencia de emojis nativos de Streamlit."""
    container.markdown(f'<div class="msg-box msg-{msg_type}">{text}</div>', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data(filepath):
    """Carga de datos desde Excel asegurando limpieza y optimizando redimiento."""
    try:
        if os.path.exists(filepath):
            # Cargar todo como string para mantener consistencia y evitar errores numéricos en matrículas o carnets
            df = pd.read_excel(filepath, dtype=str)
            df.columns = [str(col).strip().upper() for col in df.columns]
            # Limpiar datos crudos
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            return df
    except Exception as e:
        return None
    return None

def load_config():
    """Recupera la configuración de columnas seleccionadas por el administrador."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_config(columns_list):
    """Guarda en JSON persistente las columnas que el estudiante puede ver."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(columns_list, f, ensure_ascii=False, indent=4)

def render_custom_table(df):
    """Renderiza un DataFrame como una tabla HTML altamente personalizada y estilizada."""
    if df.empty:
        return "<p style='color: #A0C4FF; font-style: italic;'>No hay registros disponibles.</p>"
    
    html = '<div class="custom-table-container"><table class="custom-table">'
    html += '<thead><tr>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    
    for _, row in df.iterrows():
        html += '<tr>'
        for val in row:
            html += f'<td>{val}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    return html

# --- 5. INTERFAZ ADMINISTRATIVA (SIDEBAR) ---
with st.sidebar:
    # Si existe logo, se muestra en el panel lateral o superior; en este caso en la parte superior del sidebar
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center;'>Panel de Administración</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #143559; margin-bottom: 20px;'>", unsafe_allow_html=True)

    admin_pass = st.text_input("Contraseña de Acceso", type="password")

    if admin_pass == ADMIN_PASSWORD:
        formal_message("Acceso concedido al panel de configuración.", msg_type="success")

        st.markdown("<br><h3>1. Actualizar Datos</h3>", unsafe_allow_html=True)
        formal_message("Cargue la base de datos actualizada en formato Excel.", msg_type="info")
        uploaded_file = st.file_uploader("Formato Excel (.xlsx, .xls)", type=["xlsx", "xls"])

        if uploaded_file is not None:
            if st.button("Reemplazar Base de Datos Actual"):
                try:
                    with open(DATA_FILE, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.cache_data.clear()
                    formal_message("El archivo base ha sido reemplazado correctamente.", msg_type="success")
                except Exception as e:
                    formal_message("Ocurrió un error al guardar el archivo.", msg_type="error")

        # Cargar los datos actuales para configurar permisos de visualización
        admin_df = load_data(DATA_FILE)

        st.markdown("<br><h3>2. Columnas Visibles</h3>", unsafe_allow_html=True)
        if admin_df is not None and not admin_df.empty:
            all_columns_available = admin_df.columns.tolist()
            current_visibility = load_config()

            # Filtrar columnas que puedan haber desaparecido en el reemplazo de Excel
            valid_visibility = [col for col in current_visibility if col in all_columns_available]

            selected_cols = st.multiselect(
                "Seleccione los datos habilitados para su despliegue a los estudiantes",
                options=all_columns_available,
                default=valid_visibility,
                help="Todas las columnas seleccionadas en esta lista podrán ser vistas por los estudiantes en la plataforma principal."
            )

            if st.button("Guardar Configuración de Permisos"):
                save_config(selected_cols)
                formal_message("Los permisos de privacidad de datos se actualizaron de manera correcta.", msg_type="success")
        else:
            formal_message("Sistema sin datos cargados actualmente. Suba un archivo Excel nuevo.", msg_type="warning")

    elif admin_pass != "":
        formal_message("Credenciales incorrectas.", msg_type="error")


# --- 6. INTERFAZ PRINCIPAL DEL ESTUDIANTE ---
st.markdown("<h1 style='text-align: center; color: #FFFFFF; font-size: 38px; margin-bottom: 5px;'>PORTAL DE CONSULTA ESTUDIANTIL</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #1E3A5F; margin-bottom: 40px;'>", unsafe_allow_html=True)

df = load_data(DATA_FILE)

if df is not None and not df.empty:
    
    # 6.1 Detectar columna de búsqueda de Carnet de forma inteligente
    col_carnet = None
    possible_carnet_names = ["CARNET", "CI", "C.I.", "DOCUMENTO"]
    
    for c in df.columns:
        if c.upper() in possible_carnet_names:
            col_carnet = c
            break
            
    # Fallback más flexible si no hay una exact match
    if not col_carnet:
        for c in df.columns:
            if "CARNET" in c.upper() or "CI" == c.upper():
                col_carnet = c
                break

    if not col_carnet:
        formal_message("Advertencia de estructura: No se pudo identificar una categoría de documento de identidad en los datos cargados. Se requiere una columna denominada 'CARNET' o 'CI'.", msg_type="error")
        st.stop()

    # 6.2 Buscador
    col_spacer_l, col_search, col_spacer_r = st.columns([1.5, 2, 1.5]) # Reduciendo el ancho del buscador (columna central)
    with col_search:
        st.markdown("<h3 style='text-align: center; margin-bottom: 15px;'>INGRESA TU NÚMERO DE CARNET</h3>", unsafe_allow_html=True)
        search_value = st.text_input("Ingrese su número de carnet", placeholder="Ejemplo: 9876543", label_visibility="collapsed").strip()
        
        button_col1, button_col2, button_col3 = st.columns([1, 1.5, 1])
        with button_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            # Aquí puedes cambiar el texto a "CONSULTAR HISTORIAL ACADEMICO" si lo deseas
            run_search = st.button("Buscar Información", use_container_width=True)

    # 6.3 Despliegue de Datos del Estudiante
    if run_search and search_value:
        st.markdown("<hr style='border: 1px solid #143559; margin-top: 40px; margin-bottom: 40px;'>", unsafe_allow_html=True)
        
        # Filtro de registros por el carnet provisto
        student_records = df[df[col_carnet] == search_value]

        if student_records.empty:
            col_spacer3, col_msg, col_spacer4 = st.columns([1, 2, 1])
            with col_msg:
                formal_message("No existen registros asociados a la acreditación proporcionada. Por favor, revise el documento ingresado o consulte en las oficinas administrativas.", msg_type="warning")
        else:
            visible_columns_config = load_config()

            if not visible_columns_config:
                formal_message("Sistema restringido. La administración aún no ha autorizado la visualización pública de datos.", msg_type="warning")
            else:
                # Extraer primer registro para constituir la tarjeta identificativa general
                first_record = student_records.iloc[0]

                # Componentes posibles para el nombre completo
                nombres = str(first_record.get('NOMBRES', '')).strip()
                paterno = str(first_record.get('PATERNO', '')).strip()
                materno = str(first_record.get('MATERNO', '')).strip()
                
                # Manejar valores faltantes 'nan' que vienen como string
                nombres = "" if nombres.lower() == "nan" else nombres
                paterno = "" if paterno.lower() == "nan" else paterno
                materno = "" if materno.lower() == "nan" else materno

                nombre_completo = " ".join([n for n in [nombres, paterno, materno] if n]).upper()
                if not nombre_completo:
                    nombre_completo = "REGISTRO ESTUDIANTIL VERIFICADO"

                carrera = str(first_record.get('CARRERA', 'Información no disponible')).upper()
                carrera = "NO DOCUMENTADO" if carrera.lower() == "nan" else carrera

                semestre = str(first_record.get('SEMESTRE', 'N/A')).upper()
                semestre = "N/A" if semestre.lower() == "nan" else semestre
                
                unicodigo = str(first_record.get('UNICODIGO', 'N/A')).upper()
                unicodigo = "N/A" if unicodigo.lower() == "nan" else unicodigo

                # Renderizar la tarjeta (Card) del estudiante
                st.markdown(f"""
                <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
                <div style="background-color: #002b49; padding: 25px; border-radius: 8px; border-left: 6px solid #4DB8FF; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                    <div>
                        <h2 style="color: white; margin: 0; padding-bottom: 12px; font-size: 24px; text-transform: uppercase; display: flex; align-items: center;">
                            <span class="material-icons" style="margin-right: 10px; font-size: 28px; color: #4DB8FF;">school</span> {nombre_completo}
                        </h2>
                        <p style="color: #4DB8FF; margin: 0; font-size: 14px; letter-spacing: 1px; display: flex; align-items: center;">
                            <span class="material-icons" style="margin-right: 6px; font-size: 18px;">import_contacts</span> <b>CARRERA:</b>&nbsp; <span style="color: white; margin-left: 4px;">{carrera}</span>
                        </p>
                        <p style="color: #4DB8FF; margin: 0; font-size: 14px; letter-spacing: 1px; padding-top: 8px; display: flex; align-items: center;">
                            <span class="material-icons" style="margin-right: 6px; font-size: 18px;">event</span> <b>SEMESTRE ACTUAL:</b>&nbsp; <span style="color: white; margin-left: 4px;">{semestre}</span>
                        </p>
                    </div>
                    <div style="text-align: right; padding-left: 20px;">
                        <p style="color: #4DB8FF; margin: 0; font-size: 12px; letter-spacing: 2px; display: flex; align-items: center; justify-content: flex-end;">
                            <span class="material-icons" style="margin-right: 6px; font-size: 16px;">badge</span> <b>UNICÓDIGO</b>
                        </p>
                        <h1 style="color: white; margin: 0; font-size: 42px; font-weight: bold; letter-spacing: 2px;">{unicodigo}</h1>
                    </div>
                </div>
                <br>
                """, unsafe_allow_html=True)

                # Definir palabras clave que distingan columnas de naturaleza financiera versus académica
                financie_keywords = ['PLAN', 'ECONOMICO', 'ADMISION', 'PAGO', 'CONTADO', 'REINTEGROS', 'MATRICULA', 'CUOTA', 'MONTO', 'FINANCIERA', 'DEUDA']
                
                # Filtrar columnas solicitadas que efectivamente existan en el DataFrame actual
                active_columns = [col for col in visible_columns_config if col in student_records.columns]
                
                # Clasificar dichas columnas
                col_financieras = [c for c in active_columns if any(k in c.upper() for k in financie_keywords)]
                col_academicas = [c for c in active_columns if c not in col_financieras]

                # Segmentación por pestañas
                tab_academico, tab_financiero = st.tabs(["Información Académica", "Estado Financiero"])

                with tab_academico:
                    if col_academicas:
                        st.markdown("<h3 style='margin-bottom: 15px;'>Detalle de Asignaturas y Calificaciones</h3>", unsafe_allow_html=True)
                        st.markdown(render_custom_table(student_records[col_academicas].drop_duplicates()), unsafe_allow_html=True)
                    else:
                        formal_message("No se han otorgado permisos en este momento para consultar su información académica. Favor consultar de nuevo más tarde.", msg_type="info")

                with tab_financiero:
                    if col_financieras:
                        st.markdown("<h3 style='margin-bottom: 15px;'>Detalle de Aranceles y Pagos</h3>", unsafe_allow_html=True)
                        st.markdown(render_custom_table(student_records[col_financieras].drop_duplicates()), unsafe_allow_html=True)
                    else:
                        formal_message("La información respecto al estado del plan económico se encuentra restringida bajo la presente configuración del departamento.", msg_type="info")

else:
    formal_message("El portal se encuentra en mantenimiento. La base de datos estudiantil no está disponible por el momento. Disculpe los inconvenientes.", msg_type="error")

