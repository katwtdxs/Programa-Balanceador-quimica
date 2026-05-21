##Módulo: Main.py
#Implementación estilo de interfaz: Karen González
"""
Archivo principal del Balanceador de Ecuaciones Químicas
Este es el punto de entrada de la aplicación, aquí se ensamblan 
todos los módulos y se construye la interfaz visual con Streamlit 
"""

# Se importa streamlit para la interfaz y pandas para mostrar tablas de datos
import streamlit as st
import pandas as pd

# Aquí importamos todas las funciones de los módulos propios del proyecto
# cada uno se encarga de una responsabilidad distinta dentro de la app
from traductor import Separar_ecuacion               # separa la ecuación en reactivos y productos
from matrices import calcular_coeficientes           # calcula los coeficientes por Gauss-Jordan
from Tipo_reaccion import clasificar_reaccion        # identifica el tipo de reacción química
from Calculo_molar import calculo_masa_molar         # calcula la masa molar de cada compuesto
from historial import guardar_en_historial, exportar_como_txt, exportar_como_pdf  # gestión del historial
from explicacion_balanceo import explicar_balanceo   # genera la explicación paso a paso del balanceo
from verificar_atomos import tabla_verificacion      # construye la tabla de conteo de átomos
from verificacion import ecuacion_ya_balanceada      # verifica si la ecuación ya viene balanceada
from validacion import validar_ecuacion              # valida el formato de la ecuación antes de procesarla
from explicacion_reacciones import obtener_explicacion  # obtiene la descripción del tipo de reacción
from tabla_periodica import buscar_elemento, obtener_color_categoria  # consulta de elementos químicos
from quiz import obtener_pregunta_aleatoria, verificar_respuesta      # lógica del quiz de balanceo

# Configuro la página de Streamlit con título, ícono y diseño centrado
# esto es lo primero que debe ejecutarse antes de cualquier otro elemento de la interfaz
st.set_page_config(
    page_title="Balanceador Químico ",
    page_icon="⚗",
    layout="centered",
)

# Acá inyecto todos los estilos CSS de la aplicación mediante un bloque markdown
# esto me permite personalizar completamente la apariencia de Streamlit
# ya que por defecto su diseño es muy genérico y no se adapta a lo que necesito
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@300;400;500;600&display=swap');

/* Importo las fuentes de Google: Playfair Display para títulos y Source Sans 3 para el cuerpo */

/* Defino las variables de color globales en :root para usarlas en todo el CSS */
/* así si necesito cambiar algún tono solo lo cambio en un lugar */
:root {
    --azul_1: #0b1827;   
    --azul_2: #0f2238;   
    --azul_3: #152d4a;
    --azul_4: #1d3d62;
    --azul_5: #28527e;
    --azul_6: #3a6fa0;
    --azul_7: #4a8bc4;
    --azul_8: #6aa5d8;
    --azul_9: #93c0e6;
    --azul_10: #bcd8f0;
    --azul_11:  #dceef9;
    --azul_12: #dce8f4;
    --azul_13: #8aadc8;
    --azul_14: #5a7a96;
    --azul_15: rgba(74,139,196,0.18);
    --azul_16: rgba(74,139,196,0.32);
    --azul_17: rgba(15,34,56,0.9);
    --azul_18: rgba(21,45,74,0.95);
    --azul_19: #4a8bc4;
    --azul_20: rgba(74,139,196,0.12);
}

/* Aplico el fondo oscuro y la tipografía base a todos los contenedores raíz de Streamlit */
/* uso !important en todo para que mis estilos sobreescriban los de Streamlit sin excepción */
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
    background-color: var(--azul_1) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    color: var(--azul_12) !important;
}

/* Oculto la barra de herramientas superior de Streamlit y el pie de página */
/* para que la app se vea más limpia y sin elementos que no controlo */
[data-testid="stHeader"] { display: none !important; }
[data-testid="stMainBlockContainer"] {
    max-width: 860px !important;
    padding: 2.5rem 2rem 4rem !important;
    margin: 0 auto !important;
}
footer { display: none !important; }

/* Estilos del encabezado principal de la aplicación */
/* lo centro horizontalmente y le agrego un separador inferior sutil */
.app-header {
    text-align: center;
    padding: 2.4rem 0 1.6rem;
    border-bottom: 1px solid var(--azul_15);
    margin-bottom: 2rem;
}
/* Etiqueta pequeña sobre el título (tipo "eyebrow label") */
/* usa espaciado de letras amplio y mayúsculas para darle un toque editorial */
.app-header .label {
    font-size: 0.72rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--azul_8);
    font-family: 'Source Sans 3', sans-serif;
    font-weight: 500;
    margin-bottom: 0.6rem;
}
/* Título principal con la fuente serif para contrastar con el resto del cuerpo sans-serif */
.app-header h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    color: var(--azul_11) !important;
    margin: 0 !important;
    line-height: 1.2 !important;
    letter-spacing: -0.01em !important;
}
/* Subtítulo debajo del h1, con tono más apagado para no competir visualmente */
.app-header .subtitle {
    font-size: 0.92rem;
    color: var(--azul_13);
    margin-top: 0.6rem;
}

/* Contenedor de la lista de pestañas: fondo transparente con línea inferior como separador */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--azul_15) !important;
    gap: 0 !important;
    margin-bottom: 1.8rem !important;
}
/* Estilo base de cada pestaña inactiva */
/* el borde inferior transparente se vuelve visible al activarse o hacer hover */
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    padding: 0.6rem 1.2rem !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: var(--azul_14) !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    transition: color 0.2s, border-color 0.2s !important;
}
/* Pestaña activa: destaco el texto y pinto el borde inferior para indicar selección */
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--azul_9) !important;
    border-bottom-color: var(--azul_8) !important;
}
/* Hover en pestañas inactivas: aclaro el texto como retroalimentación visual */
[data-testid="stTabs"] [aria-selected="false"]:hover {
    color: var(--azul_12) !important;
}
/* Oculto el indicador animado por defecto de BaseWeb porque uso mi propio borde inferior */
div[data-baseweb="tab-highlight"] { display: none !important; }

/* Oculto las etiquetas de los inputs y selectboxes porque uso placeholders o texto propio */
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label { display: none !important; }

/* Campo de texto: fondo oscuro con borde sutil, tipografía coherente con el resto de la app */
[data-testid="stTextInput"] input {
    background: var(--azul_2) !important;
    border: 1px solid var(--azul_16) !important;
    border-radius: 8px !important;
    color: var(--azul_12) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.7rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
/* Al hacer focus resalto el borde y agrego un halo exterior para indicar el campo activo */
[data-testid="stTextInput"] input:focus {
    border-color: var(--azul_7) !important;
    box-shadow: 0 0 0 3px var(--azul_20) !important;
    outline: none !important;
}
/* El placeholder usa un tono más apagado para que no compita con el texto real del usuario */
[data-testid="stTextInput"] input::placeholder { color: var(--azul_14) !important; }

/* Botón genérico: fondo medio con borde y texto azul claro, bordes redondeados */
[data-testid="stButton"] > button {
    background: var(--azul_3) !important;
    border: 1px solid var(--azul_16) !important;
    border-radius: 8px !important;
    color: var(--azul_9) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}
/* Hover del botón genérico: aclaro fondo y borde para dar retroalimentación de interacción */
[data-testid="stButton"] > button:hover {
    background: var(--azul_4) !important;
    border-color: var(--azul_7) !important;
    color: var(--azul_10) !important;
}

/* El primer botón de cada sección recibe un estilo primario más prominente */
/* más peso visual para indicar que es la acción principal de esa vista */
[data-testid="stButton"]:first-of-type > button {
    background: var(--azul_4) !important;
    border-color: var(--azul_7) !important;
    color: var(--azul_11) !important;
    font-weight: 600 !important;
    padding: 0.65rem 2rem !important;
}
/* Hover del botón primario: fondo más brillante y texto blanco puro para mayor contraste */
[data-testid="stButton"]:first-of-type > button:hover {
    background: var(--azul_7) !important;
    color: #fff !important;
}

/* Botón de descarga: tratamiento más discreto que el botón normal */
/* se diferencia por ser más plano y ocupar todo el ancho disponible */
[data-testid="stDownloadButton"] > button {
    background: var(--azul_2) !important;
    border: 1px solid var(--azul_15) !important;
    border-radius: 8px !important;
    color: var(--azul_13) !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
/* Hover del botón de descarga: solo cambio borde y color del texto, sin tocar el fondo */
[data-testid="stDownloadButton"] > button:hover {
    border-color: var(--azul_7) !important;
    color: var(--azul_9) !important;
}

/* Selectbox: mismo lenguaje visual que el input de texto para unificar los controles del formulario */
[data-testid="stSelectbox"] > div > div {
    background: var(--azul_2) !important;
    border: 1px solid var(--azul_16) !important;
    border-radius: 8px !important;
    color: var(--azul_12) !important;
}

/* Contenedor base de todas las alertas: borde redondeado y línea sutil */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border: 1px solid var(--azul_15) !important;
}
/* Alerta de éxito: fondo verde muy oscuro con texto verde claro para buenas noticias */
.stSuccess {
    background: rgba(28, 58, 42, 0.5) !important;
    border-color: rgba(46, 132, 85, 0.4) !important;
    color: #7ecb9e !important;
}
/* Alerta informativa: azul oscuro semitransparente, coherente con la paleta general */
.stInfo {
    background: rgba(15, 40, 68, 0.6) !important;
    border-color: var(--azul_16) !important;
    color: var(--azul_10) !important;
}
/* Alerta de advertencia: tono ámbar muy oscuro para indicar precaución sin alarmar */
.stWarning {
    background: rgba(58, 44, 12, 0.5) !important;
    border-color: rgba(160, 110, 30, 0.4) !important;
    color: #e2b96a !important;
}
/* Alerta de error: rojo muy oscuro para errores graves, texto rojo claro legible */
.stError {
    background: rgba(58, 18, 18, 0.5) !important;
    border-color: rgba(160, 50, 50, 0.4) !important;
    color: #e28a8a !important;
}

/* Tarjeta de métrica: fondo elevado con borde para destacarla del fondo de la página */
[data-testid="stMetric"] {
    background: var(--azul_2) !important;
    border: 1px solid var(--azul_15) !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
}
/* Etiqueta de la métrica: tamaño pequeño y mayúsculas para que parezca un subtítulo de dato */
[data-testid="stMetric"] label {
    color: var(--azul_13) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
/* Valor de la métrica: fuente serif grande para darle jerarquía visual al número */
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--azul_10) !important;
    font-size: 1.6rem !important;
    font-family: 'Playfair Display', serif !important;
}

/* Bloques de código: mismo fondo oscuro que los inputs para consistencia cromática */
[data-testid="stCodeBlock"] pre, code {
    background: var(--azul_2) !important;
    border: 1px solid var(--azul_15) !important;
    color: var(--azul_10) !important;
    border-radius: 8px !important;
    font-size: 0.96rem !important;
}

/* Tabla nativa de Streamlit: ancho completo sin separación entre bordes de celdas */
[data-testid="stTable"] table {
    width: 100% !important;
    border-collapse: collapse !important;
    font-size: 0.88rem !important;
}
/* Encabezados de la tabla: fondo ligeramente más claro que el cuerpo, texto azul y mayúsculas */
[data-testid="stTable"] thead th {
    background: var(--azul_3) !important;
    color: var(--azul_9) !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1rem !important;
    border-bottom: 1px solid var(--azul_16) !important;
}
/* Celdas del cuerpo de la tabla con separador inferior para distinguir las filas */
[data-testid="stTable"] tbody td {
    color: var(--azul_12) !important;
    padding: 0.55rem 1rem !important;
    border-bottom: 1px solid var(--azul_15) !important;
}
/* Al pasar el cursor por una fila la resalto sutilmente para facilitar la lectura */
[data-testid="stTable"] tbody tr:hover td {
    background: var(--azul_20) !important;
}

/* Expander: mismo lenguaje de tarjeta que el resto de contenedores de la app */
[data-testid="stExpander"] {
    background: var(--azul_2) !important;
    border: 1px solid var(--azul_15) !important;
    border-radius: 8px !important;
}
/* Texto del summary del expander: tamaño reducido para no competir con el contenido interior */
[data-testid="stExpander"] summary {
    color: var(--azul_13) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}

/* Separador horizontal: línea fina semitransparente sin el borde por defecto del navegador */
hr { border: none; border-top: 1px solid var(--azul_15); margin: 1.6rem 0; }

/* Eyebrow label reutilizable: pequeño, en mayúsculas y con color de acento */
/* lo uso antes de los títulos de sección para dar contexto antes del h2 */
.section-eyebrow {
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--azul_7);
    font-weight: 600;
    margin-bottom: 0.3rem;
}
/* Título de sección reutilizable: serif, destacado, para encabezar cada bloque de contenido */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--azul_11);
    margin-bottom: 1.2rem;
}
/* Tarjeta de resultado: contenedor elevado donde muestro cada dato del balanceo */
.result-card {
    background: var(--azul_2);
    border: 1px solid var(--azul_16);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
/* Etiqueta interna de la tarjeta de resultado: idéntico al eyebrow label pero más compacto */
.result-card .rc-label {
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--azul_14);
    margin-bottom: 0.35rem;
    font-weight: 500;
}
/* Valor dentro de la tarjeta: texto claro con altura mínima para que la tarjeta no colapse si está vacío */
.result-card .rc-value {
    font-size: 1.05rem;
    color: var(--azul_12);
    font-family: 'Source Sans 3', sans-serif;
    font-weight: 500;
    min-height: 1.4rem;
    word-break: break-word;
}
/* Variante destacada del valor: más grande y brillante, la uso para la ecuación balanceada */
.result-card .rc-value.highlight {
    color: var(--azul_10);
    font-weight: 600;
    font-size: 1.1rem;
}
/* Contenedor de la tabla de verificación de átomos: oculta el desbordamiento para respetar las esquinas */
.atom-table-wrap {
    background: var(--azul_2);
    border: 1px solid var(--azul_15);
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}
/* La tabla interna ocupa todo el ancho del contenedor sin separación entre bordes */
.atom-table-wrap table { width: 100%; border-collapse: collapse; }
/* Encabezados de la tabla de átomos: fondo más claro, texto azul con mayúsculas */
.atom-table-wrap thead th {
    background: var(--azul_3);
    color: var(--azul_9);
    font-size: 0.74rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 600;
    padding: 0.6rem 0.9rem;
    text-align: left;
    border-bottom: 1px solid var(--azul_16);
}
/* Celdas del cuerpo de la tabla de átomos con separador inferior entre filas */
.atom-table-wrap tbody td {
    padding: 0.55rem 0.9rem;
    border-bottom: 1px solid var(--azul_15);
    font-size: 0.88rem;
    color: var(--azul_12);
    vertical-align: middle;
}
/* La última fila no necesita separador inferior porque el borde del contenedor ya lo delimita */
.atom-table-wrap tbody tr:last-child td { border-bottom: none; }
/* Caja de texto de explicación del balanceo: espacio amplio con altura mínima para no colapsar */
.explanation-box {
    background: var(--azul_2);
    border: 1px solid var(--azul_15);
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    min-height: 160px;
    color: var(--azul_13);
    font-size: 0.93rem;
    line-height: 1.8;
}
/* Píldora de masa molar: etiqueta en línea compacta para mostrar compuesto + valor en una sola línea */
.masa-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--azul_3);
    border: 1px solid var(--azul_15);
    border-radius: 6px;
    padding: 0.35rem 0.8rem;
    margin: 0.2rem;
    font-size: 0.88rem;
    color: var(--azul_12);
}
/* El nombre del compuesto en la píldora se muestra en azul brillante para diferenciarlo del valor */
.masa-pill strong { color: var(--azul_9); font-weight: 600; }
/* La unidad g/mol se muestra más pequeña y apagada porque es información secundaria */
.masa-pill span { color: var(--azul_14); font-size: 0.82rem; }
/* Texto de ayuda bajo el input: pequeño y tenue para no competir con el placeholder */
.input-hint {
    font-size: 0.82rem;
    color: var(--azul_14);
    margin-top: 0.4rem;
    text-align: center;
}
/* Caja de pregunta del quiz: borde izquierdo grueso como acento visual que la distingue de las tarjetas normales */
.quiz-question-box {
    background: var(--azul_2);
    border: 1px solid var(--azul_16);
    border-left: 3px solid var(--azul_7);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin: 1rem 0;
}
/* Entrada del historial: tarjeta compacta con tipografía monoespaciada para resaltar las ecuaciones */
.hist-entry {
    background: var(--azul_2);
    border: 1px solid var(--azul_15);
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    font-size: 0.88rem;
    font-family: 'Source Sans 3', monospace;
}
/* Oculto los textos de instrucción internos de Streamlit (small y clases instruction) */
/* que aparecen automáticamente debajo de ciertos widgets y no quiero que se vean */
small, [class*="instruction"], [class*="Instruction"] {
    display: none !important;
}
/* Ecuación original en el historial: azul brillante y negrita para identificarla de un vistazo */
.hist-entry .he-eq { color: var(--azul_9); font-weight: 600; margin-bottom: 0.2rem; }
/* Ecuación balanceada: tono claro estándar, diferenciada de la original por el símbolo → */
.hist-entry .he-bal { color: var(--azul_12); margin-bottom: 0.15rem; }
/* Metadatos (tipo y fecha): tamaño reducido y color apagado porque son datos de apoyo */
.hist-entry .he-meta { color: var(--azul_14); font-size: 0.78rem; }
</style>
""", unsafe_allow_html=True)


# Aqui defino el encabezado
# Divido el encabezado en dos columnas: una pequeña para la imagen y una grande para el título
gato, titulo_principal = st.columns([1, 3])

with gato:
    # Muestro la imagen decorativa del gato que le da personalidad a la app
    st.image("https://i.pinimg.com/736x/83/81/24/83812467a64518774d9f595efe4adc9b.jpg", use_container_width=True)

with titulo_principal:
    # Renderizo el título principal con la clase CSS definida arriba en el bloque de estilos
    st.markdown("""
    <div class="app-header" style="text-align:left; border-bottom:none; padding-top:1rem">
        <h1>Balanceador de Ecuaciones Químicas ꉂ(˵˃ ᗜ ˂˵)⋆˚꩜｡</h1>
        <div class="subtitle">꒷꒦︶꒷꒦︶ ๋ ࣭ ⭑꒷꒦</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Pestañas ──
# Creo las 4 pestañas principales de la app, cada una con su sección correspondiente
pestanas = st.tabs(["(⸝⸝> ᴗ•⸝⸝) Balanceador", "(˶˃𐃷˂˶) Tabla Periódica", "(⸝⸝๑﹏๑⸝⸝) Quiz", "₍^. .^₎⟆ Historial"])


# Y aqui esta la primera pestaña que es el balanceador

with pestanas[0]:
    
    st.markdown("<div class='section-eyebrow'>Calcula</div><div class='section-title'>Balancea la ecuación</div>", unsafe_allow_html=True)


    # Centro el campo de texto usando columnas, la del medio es la que contiene el input
    # las columnas de los extremos son solo relleno visual para que no quede tan ancho
    input_1, input_2, input_3 = st.columns([0.5, 6, 0.5])
    with input_2:
        st.markdown("<p style='color:var(--azul_13);font-size:1rem;margin-bottom:1.2rem'>Al momento de ingresar una ecuación separa los reactivos y productos con (=) y usa (+) entre compuestos (Asegurate que ingreses ecuaciones sin coeficientes para evitar errores)</p>", unsafe_allow_html=True)
        # Recibo la ecuación escrita por el usuario, con label oculto para que solo se vea el placeholder
        ecuacion = st.text_input(
            "eq", label_visibility="collapsed",
            placeholder="Ej: Al(OH)3 + H2SO4 = Al2(SO4)3 + H2O",
            key="eq_input"
        )

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # De igual forma centro el botón en la columna del medio para que quede alineado con el input
    boton_1, boton_2, boton_3 = st.columns([2, 2, 2])
    with boton_2:
        analizar = st.button("Analizar ecuación", use_container_width=True)

    # Aqui se muestra el output o los resultados del balanceo
    # Inicializo las variables de resultado vacías antes de procesar
    # así evito errores si el usuario no ha analizado nada todavía
    ecuacion_balanceada = ""
    tipo_reaccion       = ""
    datos_tabla         = None
    b_explicación       = []
    dict_masas          = {}

    # Solo proceso la ecuación si el usuario presionó el botón de analizar
    if analizar:
        # Primero verifico que el campo no esté vacío, sino no tiene sentido continuar
        if not ecuacion.strip():
            st.warning("Escribe una ecuación primero.")
        else:
            # Valido el formato de la ecuación antes de intentar balancearla
            # así le muestro errores claros al usuario si escribió algo mal
            es_valida, errores = validar_ecuacion(ecuacion)
            if not es_valida:
                st.error("Ecuación inválida: " + " · ".join(errores))
            else:
                try:
                    # Separo la ecuación en sus listas de reactivos y productos
                    reactivos, productos        = Separar_ecuacion(ecuacion)

                    # Calculo los coeficientes usando la matriz estequiométrica y Gauss-Jordan
                    coef_calculados, list_compuestos, _, _, _ = calcular_coeficientes(reactivos, productos)
                    numero_reactivos            = len(reactivos)

                    # Construyo la representación textual de la ecuación balanceada
                    # si un coeficiente es 1 no lo muestro, ya que por convención química se omite
                    compuestos_coef             = [
                        comp if coef_calculados[i] == 1 else f"{coef_calculados[i]}{comp}"
                        for i, comp in enumerate(list_compuestos)
                    ]
                    ecuacion_balanceada         = " + ".join(compuestos_coef[:numero_reactivos]) + " = " + " + ".join(compuestos_coef[numero_reactivos:])

                    # Clasifico el tipo de reacción y obtengo su nombre completo para mostrarlo
                    tipo_reaccion_raw           = clasificar_reaccion(ecuacion)
                    dict_treaccion              = obtener_explicacion(tipo_reaccion_raw)
                    tipo_reaccion               = f" {dict_treaccion['nombre_completo']}"

                    # Genero la tabla de verificación de átomos, la explicación y las masas molares
                    datos_tabla                 = tabla_verificacion(reactivos, productos, coef_calculados, list_compuestos)
                    b_explicación               = explicar_balanceo(ecuacion)
                    dict_masas                  = {comp: calculo_masa_molar(comp) for comp in list_compuestos}

                    # Guardo la ecuación en el historial para que el usuario pueda consultarla después
                    guardar_en_historial(ecuacion, ecuacion_balanceada, tipo_reaccion_raw)

                    # Si la ecuación ya venía balanceada le aviso al usuario con un mensaje informativo
                    ya_balanceada, _            = ecuacion_ya_balanceada(ecuacion)
                    if ya_balanceada:
                        st.info("ℹ  La ecuación ya estaba balanceada.")
                except Exception as e:
                    st.error(f"Error al procesar: {e}")

    # Solo muestro los resultados si hay una ecuación balanceada que mostrar
    if ecuacion_balanceada:
        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("<div class='section-eyebrow'>Resultado</div><div class='section-title'>Ecuación balanceada</div>", unsafe_allow_html=True)

        # Muestro la ecuación balanceada y el tipo de reacción en tarjetas de resultado
        st.markdown(f"""
        <div class="result-card">
          <div class="rc-label">Ecuación</div>
          <div class="rc-value highlight">{ecuacion_balanceada}</div>
        </div>
        <div class="result-card">
          <div class="rc-label">Tipo de reacción</div>
          <div class="rc-value">{tipo_reaccion}</div>
        </div>
        """, unsafe_allow_html=True)

        # Muestro las masas molares de cada compuesto como píldoras visuales
        if dict_masas:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<div class='section-eyebrow'>Cálculo</div><div class='section-title'>Masas molares</div>", unsafe_allow_html=True)
            st.markdown("<p style='color:var(--azul_13);font-size:1rem;margin-bottom:1.2rem'>Las masas molares de cada compuesto son las siguientes:</p>", unsafe_allow_html=True)
            pills = "".join(
                f"<span class='masa-pill'><strong>{c}</strong><span>{m} g/mol</span></span>"
                for c, m in dict_masas.items()
            )
            st.markdown(f"<div style='display:flex;flex-wrap:wrap;gap:4px'>{pills}</div>", unsafe_allow_html=True)

        # Muestro la descripción del tipo de reacción dentro de un expander para no saturar la pantalla
        if analizar and tipo_reaccion:
            try:
                tipo_reaccion_raw2 = clasificar_reaccion(ecuacion)
                info2              = obtener_explicacion(tipo_reaccion_raw2)
                with st.expander("Ver descripción del tipo de reacción"):
                    st.markdown(f"**¿Qué es?**\n\n{info2['descripcion']}")
                    st.markdown(f"**¿Cómo identificarla?**\n\n{info2['como_identificarla']}")
                    st.markdown(f"**Ejemplo clásico:** `{info2['ejemplo']}`")
                    st.markdown(f"**Fun fact! ₍₍⚞(˶>ᗜ<˶)⚟⁾⁾:** {info2['curiosidad']}")
            except:
                pass

        # Aqui se puede hacer visualizacion de la tabla de átomos
        # Que permite evaluar el balanceo
        if datos_tabla:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<div class='section-eyebrow'>Verificación</div><div class='section-title'>Conteo de átomos</div>", unsafe_allow_html=True)

            # Esta función construye el HTML de la tabla de conteo de átomos
            # recibe el modo "antes" o "despues" para saber qué columnas del diccionario usar
            def render_tabla(datos, modo):
                col_r    = datos["antes_reactivos"] if modo == "antes" else datos["despues_reactivos"]
                col_p    = datos["antes_productos"]  if modo == "antes" else datos["despues_productos"]
                elementos = datos["elementos"]

                # Calculo el máximo para referencia, aunque actualmente no se usa en la barra de progreso
                max_v    = max([col_r.get(e, 0) for e in elementos] + [col_p.get(e, 0) for e in elementos] + [1])
                titulo   = "Antes del balanceo (coef. = 1)" if modo == "antes" else "Después del balanceo"
                filas    = ""

                # Construyo cada fila de la tabla comparando los átomos en reactivos y productos
                # el ícono verde indica que están balanceados, el rojo que no
                for elem in elementos:
                    r, p        = col_r.get(elem, 0), col_p.get(elem, 0)
                    igual       = "✓" if r == p else "✗"
                    color_igual = "#4a9e6e" if r == p else "#c05050"
                    filas      += f"""
                    <tr>
                      <td><strong style="color:var(--azul_9)">{elem}</strong></td>
                      <td><span style="font-weight:600;color:#dce8f4">{r}</span></td>
                      <td><span style="font-weight:600;color:#dce8f4">{p}</span></td>
                      <td style="text-align:center;color:{color_igual};font-weight:700;font-size:0.9rem">{igual}</td>
                    </tr>"""
                return f"""
                <div class="atom-table-wrap" style="margin-bottom:1rem">
                  <div style="padding:0.6rem 0.9rem 0;font-size:0.74rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--azul_14);font-weight:600">{titulo}</div>
                  <table>
                    <thead><tr>
                      <th>Elemento</th><th>Reactivos</th><th>Productos</th>
                      <th style="text-align:center">¿Igual?</th>
                    </tr></thead>
                    <tbody>{filas}</tbody>
                  </table>
                </div>"""

            # Muestro la tabla antes y después del balanceo para que el usuario compare visualmente
            st.markdown(render_tabla(datos_tabla, "antes"),   unsafe_allow_html=True)
            st.markdown(render_tabla(datos_tabla, "despues"), unsafe_allow_html=True)

        # Muestro los bloques de explicación del balanceo uno por uno
        if b_explicación:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<div class='section-eyebrow'>Paso a paso</div><div class='section-title'>Explicación del balanceo</div>", unsafe_allow_html=True)
            for bloque in b_explicación:
                st.markdown(bloque)

        # Se establecen los botones de descarga del historial en TXT y PDF
        # si no hay historial los botones quedan deshabilitados para no generar archivos vacíos
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='section-eyebrow'>Exportar</div>", unsafe_allow_html=True)
        boton_exportar1, boton_exportar2 = st.columns(2)
        with boton_exportar1:
            datos_txt = exportar_como_txt()
            st.download_button(
                "↓  Descargar historial TXT",
                data=datos_txt if datos_txt else b"Sin historial",
                file_name="historial_balanceo.txt",
                mime="text/plain",
                disabled=datos_txt is None,
                use_container_width=True,
            )
        with boton_exportar2:
            datos_pdf = exportar_como_pdf()
            st.download_button(
                "↓  Descargar historial PDF",
                data=datos_pdf if datos_pdf else b"Sin historial",
                file_name="historial_balanceo.pdf",
                mime="application/pdf",
                disabled=datos_pdf is None,
                use_container_width=True,
            )


# La segunda pestaña de la interfaz esta atribuida a la tabla periodica

with pestanas[1]:
    st.markdown("<div class='section-eyebrow'>Consulta</div><div class='section-title'>Tabla periódica</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--azul_13);font-size:1rem;margin-bottom:1.2rem'>Puedes buscar un elemento en nuestra tabla periódica por medio del símbolo (Fe, O) o el nombre en español/inglés.</p>", unsafe_allow_html=True)

    # Recibo el término de búsqueda del usuario, puede ser símbolo o nombre del elemento
    busqueda = st.text_input("elem", label_visibility="collapsed",
                             placeholder="Ejemplo: Fe · Hierro · Calcium · O")

    # Solo busco si el usuario escribió algo, sino no tiene sentido consultar
    if busqueda.strip():
        elemento = buscar_elemento(busqueda.strip())
        if elemento is None:
            st.error(f"No se encontró ningún elemento con '{busqueda}'.")
        else:
            # Obtengo el color asociado a la categoría del elemento para la tarjeta visual
            color = obtener_color_categoria(elemento["categoria"])
            st.markdown("<hr>", unsafe_allow_html=True)

            # Divido la vista en dos columnas: la izquierda muestra la tarjeta visual del elemento
            # y la derecha muestra la tabla de propiedades detalladas
            ladoizq_tperiodica, ladoder_tperiodica = st.columns([1, 2])
            with ladoizq_tperiodica:
                # Tarjeta visual del elemento con su símbolo, número atómico y masa molar
                st.markdown(f"""
                <div style="background:{color};border-radius:12px;padding:1.6rem 1rem;
                            text-align:center;font-family:'Source Sans 3',sans-serif">
                  <div style="font-size:0.75rem;opacity:0.75;font-weight:600;letter-spacing:0.1em;
                              text-transform:uppercase;margin-bottom:0.3rem;color:white">
                    Z = {elemento['numero']}
                  </div>
                  <div style="font-size:3.6rem;font-weight:700;line-height:1;color:white;
                              font-family:'Playfair Display',serif">
                    {elemento['simbolo']}
                  </div>
                  <div style="font-size:1rem;margin-top:0.5rem;color:white;font-weight:500">
                    {elemento['nombre']}
                  </div>
                  <div style="font-size:0.85rem;opacity:0.8;margin-top:0.2rem;color:white">
                    {elemento['masa']} g/mol
                  </div>
                </div>""", unsafe_allow_html=True)
            with ladoder_tperiodica:
                # Tabla con las propiedades del elemento organizadas en filas de propiedad/valor
                st.markdown(f"<div class='section-title' style='font-size:1.2rem;margin-bottom:0.8rem'>{elemento['nombre']}</div>", unsafe_allow_html=True)
                st.table(pd.DataFrame({
                    "Propiedad": ["Número atómico", "Masa atómica", "Grupo", "Período", "Categoría"],
                    "Valor": [
                        elemento["numero"], f"{elemento['masa']} g/mol",
                        elemento["grupo"], elemento["periodo"], elemento["categoria"]
                    ],
                }).set_index("Propiedad"))


# La tercera pestaña es para interactuar con el quiz
# Esta funcionalidad tiene como sentido retroalimentar sobre el balanceo realizado

with pestanas[2]:
    st.markdown("<div class='section-eyebrow'>Práctica</div><div class='section-title'>Quiz de balanceo</div>", unsafe_allow_html=True)

    # Inicializo las variables del quiz en el session_state si aún no existen
    # esto es necesario porque Streamlit recarga el script completo en cada interacción
    for k, v in [("quiz_pregunta", None), ("quiz_pista", 0),
                 ("quiz_puntos", 0), ("quiz_intentos", 0), ("quiz_respondida", False)]:
        if k not in st.session_state:
            st.session_state[k] = v

    # Selector de dificultad y botón para generar una nueva pregunta en la misma fila
    dificultad_quiz, boton_quiz = st.columns([3, 1])
    with dificultad_quiz:
        dificultad = st.selectbox("dif", label_visibility="collapsed",
                                  options=["Cualquiera", "Fácil", "Media", "Difícil"],
                                  key="quiz_dif")
    with boton_quiz:
        # Al presionar el botón obtengo una nueva pregunta según el nivel seleccionado
        # y reinicio el estado de pistas y respuesta para la nueva ronda
        if st.button("Nueva →", use_container_width=True):
            nivel = None if dificultad == "Cualquiera" else dificultad
            st.session_state.quiz_pregunta  = obtener_pregunta_aleatoria(nivel)
            st.session_state.quiz_pista     = 0
            st.session_state.quiz_respondida = False

    # Solo muestro las métricas si el usuario ya ha intentado al menos una pregunta
    if st.session_state.quiz_intentos > 0:
        pct = int(st.session_state.quiz_puntos / st.session_state.quiz_intentos * 100)
        medidaq_1, medidaq_2, medidaq_3 = st.columns(3)
        medidaq_1.metric("Correctas", st.session_state.quiz_puntos)
        medidaq_2.metric("Intentos",  st.session_state.quiz_intentos)
        medidaq_3.metric("Precisión", f"{pct}%")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Si no hay pregunta activa le pido al usuario que genere una nueva
    if st.session_state.quiz_pregunta is None:
        st.markdown("<div style='text-align:center;color:var(--azul_14)'>Presiona <strong style=\"color:var(--azul_9)\">Nueva</strong> para comenzar una pregunta</div>", unsafe_allow_html=True)
    else:
        # Muestro la pregunta actual en su caja visual con el nivel de dificultad
        p = st.session_state.quiz_pregunta
        st.markdown(f"""
        <div class="quiz-question-box">
          <div style="font-size:0.74rem;letter-spacing:0.12em;text-transform:uppercase;
                      color:var(--azul_7);font-weight:600;margin-bottom:0.5rem">
            Nivel · {p['dificultad']}
          </div>
          <div style="font-family:'Source Sans 3',monospace;font-size:1.05rem;
                      color:var(--azul_12);font-weight:500">
            {p['sin_balancear']}
          </div>
          <div style="font-size:0.8rem;color:var(--azul_14);margin-top:0.4rem">
            Balancea esta ecuación
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Si ya la respondió correctamente muestro el mensaje de éxito y no dejo editar
        if st.session_state.quiz_respondida:
            st.success("¡Correcto! Genera una nueva pregunta para continuar.")
        else:
            respuesta = st.text_input("resp", label_visibility="collapsed",
                                      placeholder="Ej: 2H2 + O2 = 2H2O", key="quiz_resp")
            cv, cp = st.columns(2)
            with cv:
                # Verifico la respuesta del usuario usando el módulo de quiz
                # sumo al contador de intentos siempre, y al de puntos solo si acertó
                if st.button("Verificar", use_container_width=True):
                    if not respuesta.strip():
                        st.warning("Escribe tu respuesta.")
                    else:
                        respuesta_correcta, mensajev = verificar_respuesta(p["sin_balancear"], respuesta)
                        st.session_state.quiz_intentos += 1
                        if respuesta_correcta:
                            st.success(mensajev)
                            st.session_state.quiz_puntos    += 1
                            st.session_state.quiz_respondida = True
                        else:
                            st.error(f"Incorrecto: {mensajev}")
            with cp:
                # Voy mostrando las pistas de una en una cada vez que el usuario las solicita
                if st.button("Pedir pista", use_container_width=True):
                    idx = st.session_state.quiz_pista
                    if idx < len(p["pistas"]):
                        st.info(f"Pista {idx+1}: {p['pistas'][idx]}")
                        st.session_state.quiz_pista += 1
                    else:
                        st.warning("No hay más pistas disponibles.")

            # Muestro todas las pistas ya pedidas para que el usuario no las pierda al recargar
            if st.session_state.quiz_pista > 0:
                for i in range(st.session_state.quiz_pista):
                    st.markdown(f"<div style='font-size:0.85rem;color:var(--azul_14);margin-top:0.3rem'>💡 Pista {i+1}: {p['pistas'][i]}</div>", unsafe_allow_html=True)


# Por ultimo se establece la pestaña del historial

with pestanas[3]:
    st.markdown("<div class='section-eyebrow'>Registro</div><div class='section-title'>Historial de ecuaciones</div>", unsafe_allow_html=True)

    # Intento leer el archivo de historial, si no existe simplemente muestro un mensaje vacío
    try:
        with open("historial.txt", "r", encoding="utf-8") as f:
            raw = f.read().strip()
        if not raw:
            st.markdown("<div style='text-align:center;padding:2rem;color:var(--azul_14)'>No hay entradas registradas todavía.</div>", unsafe_allow_html=True)
        else:
            # Separo las entradas usando la línea de guiones que actúa como delimitador entre registros
            entradas = raw.split("----------------------------------------")
            for entrada in entradas:
                entrada = entrada.strip()
                if not entrada:
                    continue

                # Parseo cada línea de la entrada convirtiéndola en un diccionario clave:valor
                # uso split con límite 1 para no romper los valores que también contengan dos puntos (como la hora)
                lineas = {
                    l.split(":")[0].strip(): ":".join(l.split(":")[1:]).strip()
                    for l in entrada.splitlines() if ":" in l
                }
                eq    = lineas.get("Ecuacion", "")
                bal   = lineas.get("Balanceada", "")
                tipo  = lineas.get("Tipo", "")
                fecha = lineas.get("Fecha", "")

                # Solo muestro la tarjeta si tiene al menos la ecuación original o la balanceada
                if eq or bal:
                    st.markdown(f"""
                    <div class="hist-entry">
                      <div class="he-eq">{eq}</div>
                      <div class="he-bal">→ {bal}</div>
                      <div class="he-meta">{tipo}  ·  {fecha}</div>
                    </div>
                    """, unsafe_allow_html=True)
    except FileNotFoundError:
        # Si el archivo no existe todavía es porque no se ha balanceado ninguna ecuación
        st.markdown("<div style='text-align:center;padding:2rem;color:var(--azul_14)'>No hay entradas registradas todavía.</div>", unsafe_allow_html=True)

    # Botones de exportación del historial al final de la pestaña
    st.markdown("<hr>", unsafe_allow_html=True)
    boton_exportar1, boton_exportar2 = st.columns(2)
    with boton_exportar1:
        datos_txt = exportar_como_txt()
        st.download_button("↓  Descargar TXT", data=datos_txt if datos_txt else b"Sin historial",
                           file_name="historial_balanceo.txt", mime="text/plain",
                           disabled=datos_txt is None, use_container_width=True)
    with boton_exportar2:
        datos_pdf = exportar_como_pdf()
        st.download_button("↓  Descargar PDF", data=datos_pdf if datos_pdf else b"Sin historial",
                           file_name="historial_balanceo.pdf", mime="application/pdf",
                           disabled=datos_pdf is None, use_container_width=True)
