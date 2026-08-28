from cipher_utils import cifrar_cesar, cifrar_afin, cifrar_vigenere, normalizar_texto, analizar_criptograma

textos_originales = {
    "César (k=5)": ("Habla sobre la historia de la criptografía desde la antigüedad, mencionando que la necesidad de ocultar mensajes ha existido siempre para proteger secretos militares y políticos.", "cesar"),
    "Afín (a=5,b=7)": ("Explica el análisis de frecuencias y cómo las letras como la E y la A son las más comunes en el idioma español, permitiendo romper cifrados monoalfabéticos con relativa facilidad.", "afin"),
    "Vigenère (NUBE)": ("Describe la máquina Enigma y cómo Alan Turing logró descifrarla en Bletchley Park, cambiando el curso de la Segunda Guerra Mundial gracias al uso de las primeras computadoras electromecánicas.", "vigenere"),
}

for nombre, (original, tipo) in textos_originales.items():
    normalizado = normalizar_texto(original)
    if tipo == "cesar":
        cifrado = cifrar_cesar(normalizado, 5)
    elif tipo == "afin":
        cifrado = cifrar_afin(normalizado, 5, 7)
    else:
        cifrado = cifrar_vigenere(normalizado, "NUBE")

    print(f"--- {nombre} ---")
    resultado = analizar_criptograma(cifrado)
    print("IC:", round(resultado['ic'], 4))
    print("Tipo detectado:", resultado['tipo_detectado'])
    print("Cifrado identificado:", resultado['cifrado_identificado'])
    print("Clave:", resultado['clave'])
    print("¿Descifrado correcto?:", resultado['texto_descifrado'] == normalizado)
    print()