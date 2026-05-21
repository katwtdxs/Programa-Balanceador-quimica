# Módulo: validacion.py

"""
Este es el modulo que se encarga de revisar que la ecuación química escrita por el usuario
sea válida antes de intentar balancearla, porque si no filtramos los errores aquí
los mensajes que salen más adelante son bastante confusos

Aquí se validan tres cosas:
Primero que los símbolos que se usen existan en la tabla periódica
Segundo que los paréntesis estén bien abiertos y cerrados
Y tercero que la ecuación tenga el formato correcto con reactivos, igual y productos
"""

import re

# Acá está la lista completa de elementos válidos de la tabla periódica
# El orden importa: van de mayor a menor longitud para que al recorrer la fórmula
# se detecte primero "Cl" y no se confunda con solo "C"
ELEMENTOS_VALIDOS = [
    "He", "Li", "Be", "Ne", "Na", "Mg", "Al", "Si", "Cl", "Ar",
    "Ca", "Sc", "Ti", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Zr", "Nb",
    "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb",
    "Te", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm",
    "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf",
    "Ta", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi",
    "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th", "Pa", "Np", "Pu",
    "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr",
    # Los de una sola letra van al final para no tapar a los de dos letras
    "H", "B", "C", "N", "O", "F", "P", "S", "K", "V", "Y", "I",
    "W", "U",
]

# Lo convertimos a set para que las búsquedas sean mucho más rápidas
SET_ELEMENTOS = set(ELEMENTOS_VALIDOS)


# Esta función revisa que los paréntesis de una fórmula estén bien balanceados
# Si está bien devuelve (True, "") y si no devuelve (False, mensaje explicando el problema)
# Por ejemplo Fe2(SO4)3 está bien, pero Fe2(SO4 o Fe2SO4)3 no
def _validar_parentesis(formula):

    # Usamos un contador que sube cuando abre y baja cuando cierra
    # si en algún momento baja de cero es porque se cerró sin haber abierto antes
    contador = 0

    for i, caracter in enumerate(formula):
        if caracter == "(":
            contador += 1
        elif caracter == ")":
            contador -= 1
            # Si el contador cae a negativo hay un cierre huérfano, reportamos la posición
            if contador < 0:
                return False, f"Paréntesis ')' en posición {i+1} sin un '(' que lo abra."

    # Si al terminar el contador sigue en positivo quedó algún paréntesis sin cerrar
    if contador > 0:
        return False, "Hay un '(' que nunca se cerró con ')'."

    return True, ""


# Esta función recorre la fórmula carácter por carácter y va extrayendo los símbolos
# de elementos que encuentra, devolviendo una lista con todos ellos
# Por ejemplo "Fe2(SO4)3" devuelve ["Fe", "S", "O"]
def _extraer_simbolos(formula):

    simbolos = []
    i = 0

    while i < len(formula):
        letra = formula[i]

        # Los símbolos siempre arrancan con mayúscula, esa es la señal para empezar a leer
        if letra.isupper():
            simbolo = letra
            i += 1

            # Si le sigue una o más minúsculas, también hacen parte del símbolo
            while i < len(formula) and formula[i].islower():
                simbolo += formula[i]
                i += 1

            simbolos.append(simbolo)

        else:
            # Si no es mayúscula es un número, paréntesis u otro carácter que ignoramos
            i += 1

    return simbolos


# Esta función toma los símbolos extraídos de una fórmula y verifica que cada uno
# exista de verdad en la tabla periódica
# Devuelve (True, "") si todos están bien, o (False, mensaje) listando los que no reconoció
def _validar_simbolos(formula):

    simbolos = _extraer_simbolos(formula)
    invalidos = []

    for s in simbolos:
        if s not in SET_ELEMENTOS:
            invalidos.append(s)

    if invalidos:
        # Quitamos duplicados para no repetir el mismo símbolo dos veces en el mensaje
        invalidos_unicos = list(dict.fromkeys(invalidos))
        return False, f"Símbolo(s) no reconocido(s): {', '.join(invalidos_unicos)}. Verifica que estén bien escritos."

    return True, ""


# Esta función verifica que la ecuación tenga la estructura básica correcta
# es decir que haya exactamente un "=" con cosas a ambos lados y los "+" bien puestos
# Devuelve (True, "") si el formato es correcto, o (False, mensaje) si algo está raro
def _validar_estructura_ecuacion(ecuacion):

    # Primero quitamos todos los espacios para analizar la cadena limpia
    ecuacion_limpia = ecuacion.replace(" ", "")

    # Separamos por "=" y verificamos que haya exactamente dos partes
    partes = ecuacion_limpia.split("=")
    if len(partes) != 2:
        return False, "La ecuación debe tener exactamente un signo '=' separando reactivos y productos."

    reactivos_str, productos_str = partes

    # Ambos lados tienen que tener algo, no puede estar vacío ninguno
    if not reactivos_str:
        return False, "No hay reactivos antes del '='."
    if not productos_str:
        return False, "No hay productos después del '='."

    # Ahora separamos cada lado por "+" para revisar que no haya signos de más
    reactivos = reactivos_str.split("+")
    productos  = productos_str.split("+")

    # Si algún compuesto queda vacío es porque había un "+" duplicado o mal puesto
    for r in reactivos:
        if not r:
            return False, "Hay un '+' extra o mal puesto en los reactivos."
    for p in productos:
        if not p:
            return False, "Hay un '+' extra o mal puesto en los productos."

    return True, ""


# Esta es la función principal del módulo, la que se llama desde afuera
# Recibe la ecuación completa como string y la revisa en tres pasos en orden
# Devuelve (True, []) si todo está bien, o (False, [lista de errores]) si algo falla
def validar_ecuacion(ecuacion):

    errores = []

    # Primero revisamos la estructura general porque si el formato está mal
    # no tiene sentido seguir revisando paréntesis ni símbolos
    ok, msg = _validar_estructura_ecuacion(ecuacion)
    if not ok:
        return False, [msg]

    # Separamos la ecuación en todos sus compuestos individuales para revisarlos uno a uno
    limpia = ecuacion.replace(" ", "")
    partes = limpia.split("=")
    todos_compuestos = partes[0].split("+") + partes[1].split("+")

    # Segundo revisamos que los paréntesis estén bien en cada compuesto
    for comp in todos_compuestos:
        ok, msg = _validar_parentesis(comp)
        if not ok:
            errores.append(f"Error en '{comp}': {msg}")

    # Tercero revisamos que todos los símbolos sean elementos reales de la tabla periódica
    for comp in todos_compuestos:
        ok, msg = _validar_simbolos(comp)
        if not ok:
            errores.append(f"Error en '{comp}': {msg}")

    if errores:
        return False, errores

    return True, []