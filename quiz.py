##Módulo: Quiz.py

"""
Este modulo maneja toda la lógica del modo Quiz interactivo.
 El quiz funciona así:
   1. Se escoge una ecuación aleatoria (sin balancear) de un banco de preguntas
   2. El usuario escribe su respuesta (la ecuación balanceada)
   3. El sistema verifica si es correcta comparando los coeficientes
   4. Si está mal, da pistas progresivas
   5. Lleva la puntuación de la sesión
"""

# Importo random para elegir preguntas al azar del banco
import random
# Importo el parser de ecuaciones y el contador de átomos por compuesto
from traductor import Separar_ecuacion, conocer_cantidad_moles
# Importo el motor de cálculo de coeficientes para verificar la respuesta del usuario
from matrices import calcular_coeficientes



# Cada pregunta tiene 3 componentes:
#   - "sin_balancear": la ecuación tal como se le muestra al usuario
#   - "dificultad": "fácil", "media" o "difícil"
#   - "pistas": lista de ayudas que se van mostrando de a una

# Las pistas están ordenadas de más general a más específica,
# terminando siempre con la respuesta completa como último recurso
BANCO_PREGUNTAS = [

    # Aqui estan las preguntas con la dificultad "Facil"
    # Reacciones simples con pocos elementos y coeficientes bajos,
    # pensadas para introducir al usuario en el método de balanceo
    {
        "sin_balancear": "H2 + O2 = H2O",
        "dificultad": "Fácil",
        "pistas": [
            "Cuenta los átomos de H y O en cada lado.",
            "En el lado derecho hay 2 H y 1 O. En el izquierdo hay 2 H y 2 O.",
            "Necesitas 2 moléculas de H₂O para igualar el oxígeno.",
            "Respuesta: 2H₂ + O₂ = 2H₂O",
        ],
    },
    {
        "sin_balancear": "N2 + H2 = NH3",
        "dificultad": "Fácil",
        "pistas": [
            "El nitrógeno viene en pares (N₂) y el hidrógeno también (H₂).",
            "NH₃ tiene 1 N y 3 H. Para balancear N necesitas 2 NH₃.",
            "2 NH₃ tienen 6 H, entonces necesitas 3 H₂.",
            "Respuesta: N₂ + 3H₂ = 2NH₃",
        ],
    },
    {
        "sin_balancear": "Na + Cl2 = NaCl",
        "dificultad": "Fácil",
        "pistas": [
            "El Cl viene en pares (Cl₂) pero NaCl solo tiene 1 Cl.",
            "Necesitas 2 NaCl para usar los 2 Cl del Cl₂.",
            "Si tienes 2 NaCl necesitas 2 Na.",
            "Respuesta: 2Na + Cl2 = 2NaCl",
        ],
    },
    {
        "sin_balancear": "Fe + O2 = Fe2O3",
        "dificultad": "Fácil",
        "pistas": [
            "Fe₂O₃ tiene 2 átomos de Fe y 3 de O.",
            "El O₂ siempre viene en pares. ¿Cuántos O₂ necesitas para 3 O? No es entero…",
            "Prueba multiplicando: 4 Fe₂O₃ tiene 12 O → necesitas 6 O₂ y 4×2=8 Fe.",
            "Respuesta: 4Fe + 3O2 = 2Fe2O3",
        ],
    },

    # Aqui las de dificultad media
    # Reacciones con más elementos o coeficientes que requieren
    # un paso adicional de razonamiento para llegar al balance correcto
    {
        "sin_balancear": "CH4 + O2 = CO2 + H2O",
        "dificultad": "Media",
        "pistas": [
            "Es una combustión. Empieza balanceando el C y el H, deja el O para el final.",
            "CH₄ tiene 1 C → necesitas 1 CO₂. Tiene 4 H → necesitas 2 H₂O.",
            "Ahora cuenta el O del lado derecho: 1×2 + 2×1 = 4. Necesitas 2 O₂.",
            "Respuesta: CH4 + 2O2 = CO2 + 2H2O",
        ],
    },
    {
        "sin_balancear": "Al + HCl = AlCl3 + H2",
        "dificultad": "Media",
        "pistas": [
            "AlCl₃ necesita 3 Cl. ¿Cuántos HCl necesitas para tener 3 Cl?",
            "3 HCl tienen 3 H, pero el H₂ viene en pares. ¿Cuántos H₂ necesitas?",
            "3 H no es par. Multiplica todo por 2: necesitas 6 HCl y 2 Al.",
            "Respuesta: 2Al + 6HCl = 2AlCl3 + 3H2",
        ],
    },
    {
        "sin_balancear": "C3H8 + O2 = CO2 + H2O",
        "dificultad": "Media",
        "pistas": [
            "C₃H₈ tiene 3 C y 8 H. Empieza por el carbono: necesitas 3 CO₂.",
            "8 H necesitan 4 H₂O.",
            "Ahora el O del lado derecho: 3×2 + 4×1 = 10. Necesitas 5 O₂.",
            "Respuesta: C3H8 + 5O2 = 3CO2 + 4H2O",
        ],
    },
    {
        "sin_balancear": "KMnO4 + HCl = KCl + MnCl2 + H2O + Cl2",
        "dificultad": "Media",
        "pistas": [
            "Esta es más compleja. Fija el coeficiente de KMnO₄ = 2.",
            "2 KMnO₄ → 2 KCl + 2 MnCl₂. Eso da 2 K, 2 Mn.",
            "Los 8 O del KMnO₄ van al H₂O: necesitas 8 H₂O → 16 H → 16 HCl.",
            "Respuesta: 2KMnO4 + 16HCl = 2KCl + 2MnCl2 + 8H2O + 5Cl2",
        ],
    },

    # Y aqui las de dificultad alta o dificiles
    # Reacciones con moléculas grandes o varios elementos simultáneos
    # donde el balance no es intuitivo y requiere método algebraico
    {
        "sin_balancear": "C6H12O6 + O2 = CO2 + H2O",
        "dificultad": "Difícil",
        "pistas": [
            "Esta es la respiración celular. C₆H₁₂O₆ tiene 6 C, 12 H y 6 O.",
            "6 C → 6 CO₂. 12 H → 6 H₂O.",
            "El O del lado derecho: 6×2 + 6×1 = 18. La glucosa aporta 6, faltan 12 → 6 O₂.",
            "Respuesta: C6H12O6 + 6O2 = 6CO2 + 6H2O",
        ],
    },
    {
        "sin_balancear": "Fe2O3 + CO = Fe + CO2",
        "dificultad": "Difícil",
        "pistas": [
            "Fe₂O₃ tiene 2 Fe y 3 O. Empieza por el hierro: necesitas 2 Fe.",
            "El Fe₂O₃ tiene 3 O. Cada CO aporta 1 O para hacer CO₂.",
            "Necesitas 3 CO para quitarle los 3 O al Fe₂O₃, produciendo 3 CO₂.",
            "Respuesta: Fe2O3 + 3CO = 2Fe + 3CO2",
        ],
    },
]


def obtener_pregunta_aleatoria(dificultad=None):
    """
    Devuelve una pregunta aleatoria del banco.
    Si se especifica dificultad ("Fácil", "Media", "Difícil"),
    filtra solo las de ese nivel.

    Devuelve el diccionario completo de la pregunta.
    """
    if dificultad:
        # Filtro el banco dejando solo las preguntas del nivel pedido
        opciones = [p for p in BANCO_PREGUNTAS if p["dificultad"] == dificultad]
    else:
        # Sin filtro: cualquier pregunta del banco es válida
        opciones = BANCO_PREGUNTAS

    # Si el filtro no encontró nada (nivel sin preguntas disponibles)
    # caigo al banco completo para no devolver nunca una lista vacía
    if not opciones:
        opciones = BANCO_PREGUNTAS

    return random.choice(opciones)


def _contar_atomos(compuestos, coeficientes):
    """
    Función interna que cuenta los átomos de un lado de la ecuación,
    multiplicando cada compuesto por su coeficiente.
    """
    conteo = {}
    for comp, coef in zip(compuestos, coeficientes):
        # conocer_cantidad_moles devuelve un dict {elemento: cantidad_en_una_molécula}
        # multiplico por el coeficiente para obtener el total en ese lado de la ecuación
        for elemento, cantidad in conocer_cantidad_moles(comp).items():
            conteo[elemento] = conteo.get(elemento, 0) + cantidad * coef
    return conteo


def verificar_respuesta(ecuacion_correcta, respuesta_usuario):
    """
    Compara la respuesta del usuario con la ecuación correcta.

    La comparación NO es textual: no importa si el usuario escribe
    "2H2+O2=2H2O" o "2 H2 + O2 = 2 H2O". Lo que importa es que
    los coeficientes sean matemáticamente equivalentes.

    Estrategia:
      1. Parseamos ambas ecuaciones
      2. Comparamos el conteo de átomos en cada lado

    Devuelve una tupla (bool, mensaje):
      - (True,  "¡Correcto!")  si la respuesta está bien
      - (False, "explicación") si está mal
    """

    try:
        # Parseo la ecuación escrita por el usuario para extraer reactivos y productos
        reactivos_u, productos_u = Separar_ecuacion(respuesta_usuario)

        # Calculo los coeficientes balanceados de la respuesta del usuario
        # uso los mismos cinco valores que devuelve calcular_coeficientes pero solo necesito los dos primeros
        coef_u, compuestos_u, _, _, _ = calcular_coeficientes(reactivos_u, productos_u)

        # Separo la lista de compuestos en reactivos y productos según cuántos reactivos hay
        n_react_u = len(reactivos_u)
        atomos_react_u = _contar_atomos(compuestos_u[:n_react_u], coef_u[:n_react_u])
        atomos_prod_u  = _contar_atomos(compuestos_u[n_react_u:], coef_u[n_react_u:])

        # Recorro todos los elementos que aparecen en cualquier lado de la ecuación
        # y verifico que el conteo coincida en ambos lados (ley de conservación de masa)
        todos_elementos = set(atomos_react_u) | set(atomos_prod_u)
        for elem in todos_elementos:
            if atomos_react_u.get(elem, 0) != atomos_prod_u.get(elem, 0):
                # En cuanto encuentro un elemento desbalanceado corto y reporto cuál es
                return False, f"La ecuación no está balanceada. El elemento **{elem}** no coincide en ambos lados."

        # Si todos los elementos coinciden, la respuesta es matemáticamente correcta
        return True, "¡Correcto! La ecuación está perfectamente balanceada. 🎉"

    except Exception as e:
        # Capturo cualquier error de parseo o cálculo y lo muestro como mensaje amigable
        # así el usuario sabe que el problema es de formato y no de química
        return False, f"No pude leer tu respuesta. Verifica el formato (usa '=' y '+'). Detalle: {e}"


def generar_retroalimentacion(atomos_react, atomos_prod):
    """
    Dado el conteo de átomos en reactivos y productos,
    genera un mensaje explicando qué elementos no coinciden.

    Útil para mostrarle al usuario exactamente dónde está el error.
    """
    # Ordeno los elementos alfabéticamente para que la lista sea predecible y legible
    todos = sorted(set(atomos_react) | set(atomos_prod))
    lineas = []

    for elem in todos:
        r = atomos_react.get(elem, 0)
        p = atomos_prod.get(elem, 0)
        # Muestro un ✅ si el elemento ya está balanceado, o ❌ con los valores concretos si no lo está
        if r == p:
            lineas.append(f"✅ **{elem}**: {r} = {p}  (bien)")
        else:
            lineas.append(f"❌ **{elem}**: {r} (reactivos) ≠ {p} (productos)")

    return "\n".join(lineas)