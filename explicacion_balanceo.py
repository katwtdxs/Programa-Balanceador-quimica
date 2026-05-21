##Módulo: explicacion_balanceo.py

"""
 <Este es el modulo que explica paso a paso CÓMO se balancea una ecuación química
 usando el método algebraico con Gauss-Jordan, de forma que
 cualquier estudiante entienda el proceso, no solo el resultado.

 Pasos que se explican:
   1. Identificar reactivos, productos y asignar incógnitas
   2. Plantear el sistema de ecuaciones (la matriz)
   3. Aplicar Gauss-Jordan operación por operación
   4. Leer la solución del sistema reducido
   5. Convertir a coeficientes enteros (MCM / MCD)
"""

# Importo las funciones de separación de ecuación desde el módulo traductor
# y las herramientas de álgebra matricial desde el módulo matrices
from traductor import Separar_ecuacion, conocer_cantidad_moles
from matrices  import construir_matriz, gauss_jordan, extraer_coeficientes, racionalizar_coeficientes



# Aqui se muestran los números sin ceros decimales inútiles o que no aportan un valor
#   2.0  →  "2"     |     1.5  →  "1.5"

def _fmt(n):
    # Si el número es entero (dentro del margen de error de punto flotante)
    # lo convierto a int antes de pasarlo a string para evitar el ".0" sobrante
    if abs(n - round(n)) < 1e-9:
        return str(int(round(n)))
    # Si tiene parte decimal significativa lo muestro con 4 decimales
    return f"{n:.4f}"



# En esta funcion se escribe la ecuacion con los coeficientes que se tienen de base
# Ejemplo de salida: "2H2 + O2 = 2H2O"
# Si el coeficiente es 1 no se imprime (convención química)

def _escribir_ecuacion(compuestos, coeficientes, num_reactivos):
    # Separo los términos en dos listas según si pertenecen al lado izquierdo o derecho
    lado_r, lado_p = [], []
    for i, comp in enumerate(compuestos):
        coef    = coeficientes[i]
        # Si el coeficiente es 1 no pongo prefijo numérico (convención química estándar)
        prefijo = "" if coef == 1 else str(coef)
        termino = f"{prefijo}{comp}"
        if i < num_reactivos:
            lado_r.append(termino)
        else:
            lado_p.append(termino)
    # Uno los términos con " + " y separo reactivos de productos con " = "
    return " + ".join(lado_r) + " = " + " + ".join(lado_p)



# ahora se imprime la matriz como tabla de texto
# donde las filas son representadas por elementos y las columnas por cada compuesto de la reaccion 

def _tabla_matriz(mat, elementos, compuestos):
    # Ancho fijo de cada celda para que las columnas queden alineadas
    ancho  = 10
    lineas = []

    # Cabecera con los nombres de los compuestos alineados a la derecha
    cab = f"{'':8s}|"
    for comp in compuestos:
        cab += f"{comp:>{ancho}}"
    lineas.append(cab)
    # Línea separadora entre la cabecera y el cuerpo de la tabla
    lineas.append("-" * (9 + ancho * len(compuestos)))

    # Una fila por cada elemento, con el nombre del elemento como encabezado de fila
    for i, elem in enumerate(elementos):
        fila = f"{elem:>7s} |"
        for val in mat[i]:
            # Formateo cada valor con _fmt para no mostrar ceros decimales innecesarios
            fila += f"{_fmt(val):>{ancho}}"
        lineas.append(fila)

    return "\n".join(lineas)


# Esta funcion devuelve una lista de tuplas (descripción, tabla_resultado)
# para que el usuario vea qué se hizo y cómo quedó la matriz reducida a su forma RREF.

def _gauss_jordan_con_pasos(matriz_in, elementos, compuestos):

    # Hago una copia profunda de la matriz para no modificar la original
    # que todavía necesito intacta en otros pasos de la explicación
    mat = [fila[:] for fila in matriz_in]
    n_f = len(mat)
    n_c = len(mat[0]) if mat else 0
    # ops acumula las tuplas (descripción_textual, snapshot_de_la_matriz)
    ops = []

    # Función interna que toma una "foto" del estado actual de la matriz
    # la llamo después de cada operación para registrar cómo quedó
    def snap():
        return _tabla_matriz(mat, elementos, compuestos)

    # fila_pivote avanza cada vez que se procesa una columna con éxito
    fila_pivote = 0

    for col in range(n_c):

        # Busco la primera fila (desde fila_pivote hacia abajo) que tenga
        # un valor distinto de cero en esta columna para usarla como pivote
        fila_nz = None
        for f in range(fila_pivote, n_f):
            if abs(mat[f][col]) > 1e-9:
                fila_nz = f
                break

        # Si no encontre ningún valor no nulo esta columna es libre (variable libre)
        # y la salto sin hacer nada
        if fila_nz is None:
            continue

        # Solo intercambio si la fila con el valor no nulo no es ya la fila pivote
        if fila_nz != fila_pivote:
            mat[fila_pivote], mat[fila_nz] = mat[fila_nz], mat[fila_pivote]
            ops.append((
                f"F{fila_pivote+1} ↔ F{fila_nz+1} "
                f"(subir la fila con valor no nulo en la columna {col+1})",
                snap()
            ))

        # Divido toda la fila entre su pivote para que ese elemento quede exactamente en 1
        pivote = mat[fila_pivote][col]
        if abs(pivote - 1.0) > 1e-9:
            mat[fila_pivote] = [x / pivote for x in mat[fila_pivote]]
            ops.append((
                f"F{fila_pivote+1} ÷ {_fmt(pivote)} "
                f"(convertir el pivote de la columna {col+1} en 1)",
                snap()
            ))

        # Recorro todas las filas distintas a la pivote y les resto el múltiplo
        # adecuado para que esa columna quede en 0 en todas ellas (forma RREF)
        for f in range(n_f):
            if f == fila_pivote:
                continue
            factor = mat[f][col]
            # Si ya es prácticamente cero no hay nada que hacer
            if abs(factor) < 1e-9:
                continue
            mat[f] = [mat[f][j] - factor * mat[fila_pivote][j] for j in range(n_c)]
            # Construyo el signo de la operación para la descripción legible
            signo  = f"- {_fmt(abs(factor))}" if factor > 0 else f"+ {_fmt(abs(factor))}"
            ops.append((
                f"F{f+1} = F{f+1} {signo}·F{fila_pivote+1} "
                f"(poner 0 en la columna {col+1}, fila {f+1})",
                snap()
            ))

        fila_pivote += 1

    return ops

# Y se plantea la funcion explicar_balanceo

def explicar_balanceo(ecuacion: str) -> list:
    """
    Que recibe una ecuación química ("H2+O2=H2O") y devuelve una
    lista de strings Markdown con la explicación pedagógica del
    proceso de balanceo, paso a paso.

    Cada elemento de la lista es un bloque para st.markdown().
    """

    pasos  = []
    SEP    = "---"   # separador horizontal que uso entre cada paso en Markdown
    # Uso letras del alfabeto como nombres de las incógnitas (a, b, c...)
    # si la ecuación tiene más de 26 compuestos caigo a x0, x1, x2...
    letras = list("abcdefghijklmnopqrstuvwxyz")



    # Y lo primero que hace es determinar reactivos, productos y las incognitas
    # Separo la ecuación en sus dos lados y combino las listas para recorrerlas juntas
    reactivos, productos = Separar_ecuacion(ecuacion)
    num_reactivos        = len(reactivos)
    compuestos_todos     = reactivos + productos

    # Genero la tabla Markdown que muestra cada compuesto, su rol y la letra asignada
    pasos.append(
        "### Paso 1 — Reactivos, productos e incógnitas\n\n"
        "Separamos la ecuación y le asignamos una **letra (incógnita)** "
        "a cada compuesto. Esas letras serán los coeficientes que "
        "queremos encontrar.\n\n"
        f"**Ecuación ingresada:** `{ecuacion}`\n\n"
        f"| Compuesto | Rol | Incógnita |\n"
        f"|-----------|-----|-----------|\n"
        + "\n".join(
            f"| {comp} | {'Reactivo' if i < num_reactivos else 'Producto'} "
            f"| **{letras[i] if i < len(letras) else 'x'+str(i)}** |"
            for i, comp in enumerate(compuestos_todos)
        )
    )
    pasos.append(SEP)



    # Aqui se plantea el sistema de ecuaciones a resolver
    # Construyo la matriz estequiométrica original con todos los conteos de átomos
    matriz_orig, elementos, compuestos = construir_matriz(reactivos, productos)
    num_compuestos = len(compuestos)

    # Recorro fila por fila (elemento por elemento) para armar la expresión simbólica
    # de cada ecuación de conservación de masa antes de mostrarla al usuario
    ecuaciones_escritas = []
    for i, elem in enumerate(elementos):
        terminos = []
        for j in range(num_compuestos):
            val = matriz_orig[i][j]
            # Si el coeficiente es cero ese compuesto no contiene este elemento, lo salto
            if abs(val) < 1e-9:
                continue
            var   = letras[j] if j < len(letras) else f"x{j}"
            coef  = _fmt(abs(val))
            signo = "+" if val > 0 else "−"
            # Si el coeficiente es 1 no lo escribo delante de la variable (convención)
            parte = var if coef == "1" else f"{coef}{var}"
            terminos.append(f"{signo} {parte}")
        # Uno los términos y quito el "+" sobrante al inicio de la expresión
        expr = " ".join(terminos).lstrip("+ ").strip()
        ecuaciones_escritas.append(f"- **{elem}:** &nbsp; {expr} = 0")

    # Agrego el texto explicativo junto con las ecuaciones y la tabla de la matriz inicial
    pasos.append(
        "### Paso 2 — Plantear el sistema de ecuaciones\n\n"
        "Por la **ley de conservación de la masa**, los átomos de cada "
        "elemento deben ser iguales a ambos lados. Eso nos da una "
        "ecuación por elemento.\n\n"
        "Pasamos todo al mismo lado (productos con signo negativo) "
        "para obtener ecuaciones **= 0**:\n\n"
        + "\n".join(ecuaciones_escritas)
        + "\n\n"
        "Todas estas ecuaciones juntas forman la siguiente **matriz**:\n\n"
        "```\n" + _tabla_matriz(matriz_orig, elementos, compuestos) + "\n```\n\n"
        "> Cada **fila** es un elemento. Cada **columna** es un compuesto. "
        "El valor indica cuántos átomos de ese elemento hay en ese compuesto "
        "(negativo si es producto)."
    )
    pasos.append(SEP)


    # Aqui se da la reducción por Gauss Jordan
    # Primero muestro la introducción teórica del método antes de listar las operaciones
    pasos.append(
        "# Paso 3 — Reducción por Gauss Jordan\n\n"
        "Ahora resolvemos la matriz con el **método de Gauss Jordan**. "
        "El objetivo es transformarla en su forma escalonada reducida "
        "**(RREF)**, donde cada columna pivote tiene un **1** y el "
        "resto de esa columna son **0s**.\n\n"
        "Solo se permiten tres tipos de operaciones sobre las filas:\n\n"
        "| Operación | ¿Qué hace? |\n"
        "|-----------|------------|\n"
        "| **Intercambio** | Cambia el orden de dos filas |\n"
        "| **Escalado** | Divide una fila por un número para obtener pivote = 1 |\n"
        "| **Eliminación** | Resta un múltiplo de una fila a otra para poner un 0 |\n\n"
        "A continuación se muestra **cada operación** y cómo queda "
        "la matriz después de aplicarla:"
    )

    # Ejecuto el Gauss Jordan instrumentado que registra cada operación con su snapshot
    operaciones = _gauss_jordan_con_pasos(matriz_orig, elementos, compuestos)

    # Si no se generó ninguna operación es porque la matriz ya estaba reducida de entrada
    if not operaciones:
        pasos.append("_La matriz ya estaba reducida; no se necesitaron operaciones._")
    else:
        # Agrego un bloque por operación con su descripción y el estado de la matriz
        for i, (desc, tabla) in enumerate(operaciones, 1):
            pasos.append(
                f"**Operación {i}:** {desc}\n\n"
                f"```\n{tabla}\n```"
            )
    pasos.append(SEP)


    # Ahora se plantea el proceso para leer la solucion
    # Aplico el Gauss-Jordan definitivo (sin registro de pasos) para obtener la RREF final
    # y extraigo los coeficientes como números de punto flotante
    matriz_rref = gauss_jordan(matriz_orig)
    coef_float  = extraer_coeficientes(matriz_rref, num_compuestos)

    # Genero el texto con el valor de cada incógnita acompañado del nombre del compuesto
    sol_texto = "\n".join(
        f"- **{letras[j] if j < len(letras) else 'x'+str(j)}** ({comp}) = {_fmt(coef_float[j])}"
        for j, comp in enumerate(compuestos)
    )

    pasos.append(
        "# Paso 4 — Leer la solución\n\n"
        "Con la matriz en RREF el sistema queda resuelto, pero tiene "
        "**infinitas soluciones** porque hay una variable libre "
        "(los coeficientes se pueden escalar todos por el mismo número "
        "y la ecuación sigue balanceada).\n\n"
        "Para fijar una solución concreta tomamos la convención de "
        "asignarle **1** al último coeficiente y despejamos los demás.\n\n"
        "**Valores obtenidos:**\n\n"
        + sol_texto
    )
    pasos.append(SEP)

    # Y finalmente se convierten los flotantes a enteros mínimos usando MCM y MCD internamente
    # y armo la ecuación final en texto para mostrársela al usuario
    coef_enteros        = racionalizar_coeficientes(coef_float)
    ecuacion_balanceada = _escribir_ecuacion(compuestos, coef_enteros, num_reactivos)

    # Lista con los coeficientes enteros finales, uno por compuesto
    coef_fin_texto = "\n".join(
        f"- **{letras[j] if j < len(letras) else 'x'+str(j)}** ({comp}) = **{coef_enteros[j]}**"
        for j, comp in enumerate(compuestos)
    )

    pasos.append(
        "### Paso 5 — Convertir a coeficientes enteros\n\n"
        "Los coeficientes estequiométricos deben ser **enteros positivos**. "
        "Para convertir los decimales o fracciones obtenidos:\n\n"
        "1. Se aproxima cada decimal a una fracción **p/q**.\n"
        "2. Se multiplica todo por el **MCM** de los denominadores "
        "→ todos pasan a ser enteros.\n"
        "3. Se divide todo entre el **MCD** del conjunto "
        "→ se obtienen los valores mínimos posibles.\n\n"
        "**Coeficientes finales:**\n\n"
        + coef_fin_texto
        + f"\n\n**Ecuación balanceada:**\n\n`{ecuacion_balanceada}`"
    )

    # Devuelvo la lista completa de bloques Markdown listos para st.markdown()
    return pasos