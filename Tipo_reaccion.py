# Parte hecha por: Julian Ruiz
##Módulo: Tipo_reacción.py

# Importo las funciones del traductor para parsear compuestos y separar ecuaciones
from traductor import conocer_cantidad_moles, Separar_ecuacion



# Estas funciones inspeccionan la composición elemental de un
# compuesto para que las reglas de clasificación sean legibles

def contar_elementos(compuesto):
    # Devuelve el conjunto de símbolos elementales presentes en el compuesto
    # uso conocer_cantidad_moles porque ya sabe cómo parsear fórmulas como Al2(SO4)3
    return set(conocer_cantidad_moles(compuesto).keys())

def es_elemento_puro(compuesto):
    # Un elemento puro tiene exactamente un tipo de átomo (ej: Na, O2, Fe)
    return len(contar_elementos(compuesto)) == 1

def es_compuesto(compuesto):
    # Un compuesto tiene más de un tipo de átomo (ej: NaCl, H2O, Al2O3)
    return len(contar_elementos(compuesto)) > 1

def es_hidrocarburo(compuesto):
    # Un hidrocarburo solo contiene C y H, y debe tener carbono obligatoriamente
    # uso issubset para permitir que también sea solo C (carbono puro no cuenta, pero el filtro de C lo excluye)
    elems = contar_elementos(compuesto)
    return elems.issubset({"C", "H"}) and "C" in elems

def contiene_oxigeno_molecular(lista):
    # Verifico si O2 está en la lista de reactivos como molécula independiente
    # esto es clave para distinguir combustiones de otras reacciones con oxígeno
    return "O2" in lista


# Cada función recibe las listas de reactivos y productos
# y devuelve True si la reacción encaja con ese tipo


def es_combustion(reactivos, productos):
    # Determina si la reacción corresponde a una combustión.
    # Para serlo necesita: O2 como reactivo, un hidrocarburo, y producir CO2 y H2O
    if not contiene_oxigeno_molecular(reactivos):
        return False

    # Verifico que al menos uno de los reactivos sea un hidrocarburo
    hidrocarburo = any(es_hidrocarburo(r) for r in reactivos)

    # Verifico que los productos incluyan CO2 y H2O (subproductos clásicos de la combustión)
    produce_CO2 = any("CO2" in p for p in productos)
    produce_H2O = any("H2O" in p for p in productos)

    return hidrocarburo and produce_CO2 and produce_H2O


def es_sintesis(reactivos, productos):
    """
        Reacción de síntesis:

            A + B → AB
    """
    # En una síntesis varios reactivos se combinan en menos productos
    # la señal más simple es que hay más reactivos que productos
    return len(reactivos) > len(productos)


def es_descomposicion(reactivos, productos):
    """
        Reacción de descomposición:

            AB → A + B
    """
    # En una descomposición un reactivo se rompe en varios productos
    # la señal más simple es que hay menos reactivos que productos
    return len(reactivos) < len(productos)


def es_sustitucion_simple(reactivos, productos):
    """
        Reacción de sustitución simple:

            A + BC → AC + B
    """
    # En los reactivos debe haber al menos un elemento puro y al menos un compuesto
    react_elemento = any(es_elemento_puro(r) for r in reactivos)
    react_compuesto = any(es_compuesto(r) for r in reactivos)

    # En los productos también debe aparecer tanto un elemento libre como un compuesto
    # esto confirma que el elemento desplazó a otro dentro del compuesto
    prod_elemento = any(es_elemento_puro(p) for p in productos)
    prod_compuesto = any(es_compuesto(p) for p in productos)

    return react_elemento and react_compuesto and prod_elemento and prod_compuesto


def es_doble_sustitucion(reactivos, productos):
    """
        Reacción de doble sustitución:

            AB + CD → AD + CB
    """
    # La doble sustitución requiere exactamente 2 reactivos y 2 productos
    if len(reactivos) != 2 or len(productos) != 2:
        return False

    # Todos los participantes deben ser compuestos (ningún elemento puro)
    # porque los iones de ambos compuestos intercambian parejas
    return all(es_compuesto(x) for x in reactivos + productos)


# Aqui se define la funcion principal de este modulo
def clasificar_reaccion(ecuacion):
    """
    Recibe una ecuación química como string
    y devuelve el tipo de reacción.
    """
    # Separo la ecuación en sus dos listas antes de aplicar las reglas
    reactivos, productos = Separar_ecuacion(ecuacion)

    # Evalúo los tipos en orden de especificidad: combustión primero porque
    # también satisfaría síntesis o sustitución si no la filtrara antes
    if es_combustion(reactivos, productos):
        return "Combustion"

    if es_sintesis(reactivos, productos):
        return "Sintesis"

    if es_descomposicion(reactivos, productos):
        return "Descomposicion"

    if es_sustitucion_simple(reactivos, productos):
        return "Sustitucion simple"

    if es_doble_sustitucion(reactivos, productos):
        return "Doble sustitucion"

    # Si ninguna regla aplica devuelvo "Desconocida" para no romper el flujo principal
    return "Desconocida"