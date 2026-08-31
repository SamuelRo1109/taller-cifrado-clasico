# Taller de Cifrado Clásico

Aplicación web que realiza criptoanálisis automático de cifrados clásicos (César, Afín y Vigenère): calcula el Índice de Coincidencia, cuenta frecuencias de letras, identifica el tipo de cifrado y aplica el ataque correspondiente para recuperar el texto original y la clave — sin conocerla de antemano.

**Sitio en producción:** http://www.rodriguezchavez.site

## Qué hace

Dado un criptograma, la aplicación:

1. Normaliza el texto (mayúsculas, sin tildes ni signos de puntuación, alfabeto A-Z/Ñ de 27 caracteres).
2. Calcula el **Índice de Coincidencia (IC)** para determinar si el cifrado es monoalfabético o polialfabético.
3. Cuenta la **frecuencia de cada letra** en el criptograma.
4. Aplica el ataque correspondiente:
   - **César** — fuerza bruta sobre las 27 rotaciones posibles, evaluadas por chi-cuadrado contra las frecuencias del español.
   - **Afín** — resuelve el sistema de ecuaciones a partir de las dos letras más frecuentes, probando ambas asignaciones posibles (E/A).
   - **Vigenère** — método de Kasiski (búsqueda de trigramas repetidos) más análisis de Índice de Coincidencia por columna para determinar la longitud de la clave, y ataque César independiente por columna.
5. Entrega el texto descifrado y la clave encontrada.

Incluye además un modo de **cifrado/validación**, para cifrar un texto original con parámetros conocidos y comparar el resultado contra un criptograma de referencia.

## Stack

- **Backend:** Python 3.11, Flask
- **Frontend:** HTML, CSS, JavaScript (sin frameworks)
- **Despliegue:** AWS EC2 (Amazon Linux 2023), Gunicorn como servidor WSGI, nginx como reverse proxy, sin certificado SSL (HTTP puerto 80)
- **DNS:** registro tipo A (sin CNAME) sobre dominio propio

## Estructura del proyecto
├── app.py # Rutas Flask y manejo de formularios
├── cipher_utils.py # Lógica de cifrado, criptoanálisis y ataques
├── requirements.txt
├── templates/
│ └── index.html
└── static/
├── css/style.css
└── js/script.js


## Ejecutar en local

```bash
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate        # Linux / macOS
.\venv\Scripts\Activate.ps1     # Windows (PowerShell)

pip install -r requirements.txt
python app.py
```

Abrir `http://127.0.0.1:5000`.

## Validación

La lógica de cifrado y criptoanálisis fue validada contra los tres retos de ejemplo del taller (César, Afín, Vigenère), confirmando en cada caso: cálculo correcto del IC, identificación automática del tipo de cifrado, y recuperación exacta de la clave y el texto original sin conocerlos de antemano.