from collections import defaultdict

# Alfabeto español de 27 caracteres, tal como pide el PDF
ALPHABET = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
ALPHABET_SIZE = len(ALPHABET)  # 27


def normalizar_texto(texto):
    """Convierte a mayúsculas, quita tildes (menos en la Ñ) y deja solo A-Z/Ñ."""
    texto = texto.upper()
    reemplazos = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U'}
    for original, plano in reemplazos.items():
        texto = texto.replace(original, plano)
    return ''.join(c for c in texto if c in ALPHABET)


def contar_frecuencias(texto):
    """Devuelve un diccionario {letra: cantidad de apariciones}."""
    frecuencias = {letra: 0 for letra in ALPHABET}
    for c in texto:
        if c in frecuencias:
            frecuencias[c] += 1
    return frecuencias


def calcular_ic(texto):
    """Índice de Coincidencia: IC = sum(f_i * (f_i - 1)) / (N * (N - 1))."""
    n = len(texto)
    if n <= 1:
        return 0.0
    frecuencias = contar_frecuencias(texto)
    suma = sum(f * (f - 1) for f in frecuencias.values())
    return suma / (n * (n - 1))


def cifrar_cesar(texto, b):
    """Cifra desplazando cada letra b posiciones. b puede ser negativo para descifrar."""
    resultado = []
    for c in texto:
        if c in ALPHABET:
            idx = ALPHABET.index(c)
            nuevo_idx = (idx + b) % ALPHABET_SIZE
            resultado.append(ALPHABET[nuevo_idx])
    return ''.join(resultado)


def descifrar_cesar(texto, b):
    return cifrar_cesar(texto, -b)


# Frecuencias de referencia del español (tabla del PDF), en porcentaje
FRECUENCIAS_ESPANOL = {
    'A': 12.53, 'B': 1.42, 'C': 4.68, 'D': 5.86, 'E': 13.68, 'F': 0.69,
    'G': 1.01, 'H': 0.70, 'I': 6.25, 'J': 0.44, 'K': 0.02, 'L': 4.97,
    'M': 3.15, 'N': 6.71, 'Ñ': 0.31, 'O': 8.68, 'P': 2.51, 'Q': 0.88,
    'R': 6.87, 'S': 7.98, 'T': 4.63, 'U': 3.93, 'V': 0.90, 'W': 0.01,
    'X': 0.22, 'Y': 0.90, 'Z': 0.52
}


def puntaje_chi_cuadrado(texto):
    """
    Compara las frecuencias observadas en 'texto' contra las frecuencias
    esperadas del español. Un puntaje MÁS BAJO significa que el texto
    se parece MÁS al español (menos diferencia con lo esperado).
    """
    n = len(texto)
    if n == 0:
        return float('inf')
    frecuencias = contar_frecuencias(texto)
    chi2 = 0.0
    for letra in ALPHABET:
        observado = frecuencias[letra]
        esperado = FRECUENCIAS_ESPANOL[letra] / 100 * n
        if esperado > 0:
            chi2 += (observado - esperado) ** 2 / esperado
    return chi2


def atacar_cesar(texto_cifrado):
    """
    Fuerza bruta: prueba las 27 rotaciones posibles y devuelve
    la que mejor coincide con las frecuencias del español.
    Retorna: (clave_encontrada, texto_descifrado, lista_de_todos_los_intentos)
    """
    resultados = []
    for k in range(ALPHABET_SIZE):
        candidato = descifrar_cesar(texto_cifrado, k)
        score = puntaje_chi_cuadrado(candidato)
        resultados.append({'clave': k, 'texto': candidato, 'score': score})

    mejor = min(resultados, key=lambda r: r['score'])
    return mejor['clave'], mejor['texto'], resultados


def inverso_modular(a, m=ALPHABET_SIZE):
    """Encuentra a^-1 tal que (a * a^-1) mod m == 1. Existe solo si mcd(a, m) == 1."""
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


def cifrar_afin(texto, a, b):
    """C = (a*m + b) mod 27. Requiere mcd(a, 27) = 1."""
    resultado = []
    for c in texto:
        if c in ALPHABET:
            m = ALPHABET.index(c)
            nuevo_idx = (a * m + b) % ALPHABET_SIZE
            resultado.append(ALPHABET[nuevo_idx])
    return ''.join(resultado)


def descifrar_afin(texto, a, b):
    """M = a^-1 * (C - b) mod 27."""
    a_inv = inverso_modular(a)
    if a_inv is None:
        raise ValueError(f"a={a} no tiene inverso modular respecto a {ALPHABET_SIZE} (no es coprimo)")
    resultado = []
    for c in texto:
        if c in ALPHABET:
            idx_c = ALPHABET.index(c)
            m = (a_inv * (idx_c - b)) % ALPHABET_SIZE
            resultado.append(ALPHABET[m])
    return ''.join(resultado)

def resolver_afin_por_dos_puntos(c1, p1, c2, p2):
    """
    Dado que sabemos (o suponemos) que la letra en texto plano p1 se cifra como c1,
    y p2 se cifra como c2, resuelve el sistema:
        c1 = a*p1 + b (mod 27)
        c2 = a*p2 + b (mod 27)
    Devuelve (a, b) o None si no hay solución válida (a debe ser coprimo con 27).
    """
    diff_p = (p1 - p2) % ALPHABET_SIZE
    inv_diff_p = inverso_modular(diff_p)
    if inv_diff_p is None:
        return None  # p1 - p2 no es invertible, no se puede resolver este par

    a = ((c1 - c2) * inv_diff_p) % ALPHABET_SIZE
    if inverso_modular(a) is None:
        return None  # a no es coprimo con 27, clave inválida

    b = (c1 - a * p1) % ALPHABET_SIZE
    return a, b


def atacar_afin(texto_cifrado):
    """
    Ataque por análisis de frecuencias: toma las 2 letras más frecuentes del
    criptograma y asume que corresponden a E y A (las más frecuentes del español),
    probando ambos posibles emparejamientos. Devuelve la mejor solución según
    el puntaje chi-cuadrado.
    """
    frecuencias = contar_frecuencias(texto_cifrado)
    letras_ordenadas = sorted(frecuencias.items(), key=lambda x: x[1], reverse=True)
    top_letras = [letra for letra, cant in letras_ordenadas if cant > 0][:2]

    if len(top_letras) < 2:
        return None, None, None, []

    idx_E = ALPHABET.index('E')
    idx_A = ALPHABET.index('A')
    c1 = ALPHABET.index(top_letras[0])
    c2 = ALPHABET.index(top_letras[1])

    candidatos = []
    # Caso 1: la letra más frecuente del cifrado = E, la segunda = A
    sol = resolver_afin_por_dos_puntos(c1, idx_E, c2, idx_A)
    if sol:
        candidatos.append(sol)
    # Caso 2: la letra más frecuente del cifrado = A, la segunda = E
    sol = resolver_afin_por_dos_puntos(c1, idx_A, c2, idx_E)
    if sol:
        candidatos.append(sol)

    resultados = []
    for a, b in candidatos:
        try:
            candidato_texto = descifrar_afin(texto_cifrado, a, b)
            score = puntaje_chi_cuadrado(candidato_texto)
            resultados.append({'a': a, 'b': b, 'texto': candidato_texto, 'score': score})
        except ValueError:
            continue

    if not resultados:
        return None, None, None, []

    mejor = min(resultados, key=lambda r: r['score'])
    return mejor['a'], mejor['b'], mejor['texto'], resultados

def cifrar_vigenere(texto, clave):
    """Cada letra se desplaza según la letra correspondiente de la clave, repetida."""
    clave = normalizar_texto(clave)
    resultado = []
    for i, c in enumerate(texto):
        if c in ALPHABET:
            desplazamiento = ALPHABET.index(clave[i % len(clave)])
            idx = ALPHABET.index(c)
            nuevo_idx = (idx + desplazamiento) % ALPHABET_SIZE
            resultado.append(ALPHABET[nuevo_idx])
    return ''.join(resultado)


def descifrar_vigenere(texto, clave):
    clave = normalizar_texto(clave)
    resultado = []
    for i, c in enumerate(texto):
        if c in ALPHABET:
            desplazamiento = ALPHABET.index(clave[i % len(clave)])
            idx = ALPHABET.index(c)
            nuevo_idx = (idx - desplazamiento) % ALPHABET_SIZE
            resultado.append(ALPHABET[nuevo_idx])
    return ''.join(resultado)




def encontrar_repeticiones(texto, longitud_secuencia=3):
    """Encuentra secuencias repetidas y las distancias entre sus apariciones."""
    posiciones = defaultdict(list)
    for i in range(len(texto) - longitud_secuencia + 1):
        secuencia = texto[i:i + longitud_secuencia]
        posiciones[secuencia].append(i)

    distancias = []
    for secuencia, pos_list in posiciones.items():
        if len(pos_list) > 1:
            for j in range(1, len(pos_list)):
                distancias.append(pos_list[j] - pos_list[0])
    return distancias


def estimar_longitudes_clave(texto, max_longitud=15):
    """
    Usa Kasiski: calcula el MCD de las distancias entre secuencias repetidas
    y devuelve las longitudes de clave candidatas más probables (factores comunes).
    """
    distancias = encontrar_repeticiones(texto, 3)
    if not distancias:
        distancias = encontrar_repeticiones(texto, 2)  # fallback si no hay trigramas repetidos

    conteo_factores = defaultdict(int)
    for d in distancias:
        for L in range(2, max_longitud + 1):
            if d % L == 0:
                conteo_factores[L] += 1

    candidatos = sorted(conteo_factores.items(), key=lambda x: x[1], reverse=True)
    return [L for L, _ in candidatos[:5]] if candidatos else list(range(2, 6))


def dividir_en_columnas(texto, longitud_clave):
    """Divide el texto en L subtextos, cada uno cifrado con César por una letra fija de la clave."""
    columnas = ['' for _ in range(longitud_clave)]
    for i, c in enumerate(texto):
        columnas[i % longitud_clave] += c
    return columnas


def atacar_vigenere(texto_cifrado, max_longitud=15, umbral_ic=0.06):
    """
    1. Prueba cada longitud de clave candidata de 2 a max_longitud.
    2. Para cada L, calcula el IC PROMEDIO de las L columnas (más confiable
       que comparar chi-cuadrado entre longitudes distintas, porque columnas
       más cortas sesgan el chi-cuadrado de forma injusta).
    3. Escoge la longitud MÁS PEQUEÑA cuyo IC promedio supere el umbral
       (los múltiplos de la longitud real también dan IC alto, pero la
       longitud real es la mínima que lo logra).
    4. Con esa longitud, resuelve cada columna como un César independiente.
    """
    resultados_por_longitud = []
    for L in range(2, max_longitud + 1):
        columnas = dividir_en_columnas(texto_cifrado, L)
        ics = [calcular_ic(col) for col in columnas]
        ic_promedio = sum(ics) / len(ics)
        resultados_por_longitud.append({'longitud': L, 'ic_promedio': ic_promedio})

    candidatas = [r for r in resultados_por_longitud if r['ic_promedio'] >= umbral_ic]
    if candidatas:
        mejor_longitud = min(candidatas, key=lambda r: r['longitud'])['longitud']
    else:
        # Si nada supera el umbral, nos quedamos con la de mayor IC promedio
        mejor_longitud = max(resultados_por_longitud, key=lambda r: r['ic_promedio'])['longitud']

    columnas = dividir_en_columnas(texto_cifrado, mejor_longitud)
    clave_letras = []
    for columna in columnas:
        k, _, _ = atacar_cesar(columna)
        clave_letras.append(ALPHABET[k])

    clave_encontrada = ''.join(clave_letras)
    texto_descifrado = descifrar_vigenere(texto_cifrado, clave_encontrada)

    return clave_encontrada, texto_descifrado, resultados_por_longitud


def analizar_criptograma(texto_cifrado_crudo):
    """
    Esta es la función maestra del código: normaliza el texto, calcula el IC, decide si el cifrado
    es monoalfabético o polialfabético según el umbral, y aplica el ataque
    correspondiente (César/Afín por chi-cuadrado, o Vigenère por Kasiski).
    Por último, devuelve un diccionario con todo el detalle para mostrar en pantalla.
    """

    texto_limpio = normalizar_texto(texto_cifrado_crudo)
    ic = calcular_ic(texto_limpio)
    frecuencias = contar_frecuencias(texto_limpio)
    frecuencia_max = max(frecuencias.values()) if any(frecuencias.values()) else 1

    resultado = {
        'texto_normalizado': texto_limpio,
        'longitud': len(texto_limpio),
        'ic': ic,
        'frecuencias': frecuencias,
        'kasiski': None,
        'frecuencia_max': frecuencia_max,
    }

    UMBRAL_MONO = 0.06

    if ic >= UMBRAL_MONO:
        resultado['tipo_detectado'] = 'Monoalfabético (César o Afín)'

        k_cesar, texto_cesar, resultados_cesar = atacar_cesar(texto_limpio)
        score_cesar = min(r['score'] for r in resultados_cesar)

        a_afin, b_afin, texto_afin, resultados_afin = atacar_afin(texto_limpio)
        score_afin = min((r['score'] for r in resultados_afin), default=float('inf'))

        if score_afin < score_cesar:
            resultado['cifrado_identificado'] = 'Afín'
            resultado['clave'] = f'a={a_afin}, b={b_afin}'
            resultado['texto_descifrado'] = texto_afin
        else:
            resultado['cifrado_identificado'] = 'César'
            resultado['clave'] = f'k={k_cesar}'
            resultado['texto_descifrado'] = texto_cesar
    else:
        resultado['tipo_detectado'] = 'Polialfabético (Vigenère)'
        resultado['cifrado_identificado'] = 'Vigenère'
        clave, texto_descifrado, resultados_por_longitud = atacar_vigenere(texto_limpio)
        resultado['clave'] = clave
        resultado['texto_descifrado'] = texto_descifrado

        distancias = encontrar_repeticiones(texto_limpio, 3)
        resultado['kasiski'] = {
            'distancias': distancias[:15],
            'total_repeticiones': len(distancias),
            'ic_por_longitud': sorted(resultados_por_longitud, key=lambda r: r['longitud']),
            'longitud_elegida': len(clave),
        }

    return resultado


def cifrar_texto_generico(texto, tipo, **params):
    """
    Cifra un texto según el tipo especificado. Útil para el modo 'Validación
    de código' que pide el PDF: meter el Texto Original y comparar contra
    el Texto Cifrado de la guía.
    tipo: 'cesar' | 'afin' | 'vigenere'
    """
    texto_limpio = normalizar_texto(texto)
    if tipo == 'cesar':
        return texto_limpio, cifrar_cesar(texto_limpio, params['k'])
    elif tipo == 'afin':
        return texto_limpio, cifrar_afin(texto_limpio, params['a'], params['b'])
    elif tipo == 'vigenere':
        return texto_limpio, cifrar_vigenere(texto_limpio, params['clave'])
    else:
        raise ValueError('Tipo de cifrado no reconocido')