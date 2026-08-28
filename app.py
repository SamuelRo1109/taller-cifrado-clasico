from flask import Flask, render_template, request
from cipher_utils import analizar_criptograma, cifrar_texto_generico

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    modo = request.form.get('modo', 'descifrar')

    resultado = None
    texto_ingresado = ''

    resultado_cifrado = None
    texto_original_ingresado = ''
    tipo_cifrado_seleccionado = 'cesar'
    param_k = 3
    param_a = 5
    param_b = 8
    param_clave = 'CLAVE'

    if request.method == 'POST':
        if modo == 'descifrar':
            texto_ingresado = request.form.get('criptograma', '')
            if texto_ingresado.strip():
                resultado = analizar_criptograma(texto_ingresado)

        elif modo == 'cifrar':
            texto_original_ingresado = request.form.get('texto_original', '')
            tipo_cifrado_seleccionado = request.form.get('tipo_cifrado', 'cesar')

            if texto_original_ingresado.strip():
                try:
                    if tipo_cifrado_seleccionado == 'cesar':
                        param_k = int(request.form.get('param_k', 3))
                        texto_norm, texto_cifrado = cifrar_texto_generico(
                            texto_original_ingresado, 'cesar', k=param_k)
                    elif tipo_cifrado_seleccionado == 'afin':
                        param_a = int(request.form.get('param_a', 5))
                        param_b = int(request.form.get('param_b', 8))
                        texto_norm, texto_cifrado = cifrar_texto_generico(
                            texto_original_ingresado, 'afin', a=param_a, b=param_b)
                    else:
                        param_clave = request.form.get('param_clave', 'CLAVE')
                        texto_norm, texto_cifrado = cifrar_texto_generico(
                            texto_original_ingresado, 'vigenere', clave=param_clave)

                    resultado_cifrado = {
                        'texto_normalizado': texto_norm,
                        'texto_cifrado': texto_cifrado,
                    }
                except ValueError as e:
                    resultado_cifrado = {'error': str(e)}

    return render_template(
        'index.html',
        modo=modo,
        resultado=resultado,
        texto_ingresado=texto_ingresado,
        resultado_cifrado=resultado_cifrado,
        texto_original_ingresado=texto_original_ingresado,
        tipo_cifrado_seleccionado=tipo_cifrado_seleccionado,
        param_k=param_k, param_a=param_a, param_b=param_b, param_clave=param_clave,
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)