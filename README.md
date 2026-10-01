# 🕵️ Esteganografía LSB con análisis Chi-cuadrado

Aplicación de escritorio en **Python** que permite **ocultar**, **extraer** y **analizar** mensajes de texto dentro de imágenes mediante la técnica **LSB (Least Significant Bit)**. Incluye un módulo de detección estadística basado en el ataque **Chi-cuadrado (χ²)** de Westfeld y Pfitzmann (1999).

> Proyecto académico para la materia **ELC107 – Criptografía y Seguridad**
> Universidad Autónoma Gabriel René Moreno · Facultad de Ingeniería en Ciencias de la Computación y Telecomunicaciones · Ingeniería Informática

---

## 📋 Tabla de contenido

- [Características](#-características)
- [Marco teórico](#-marco-teórico)
- [Análisis Chi-cuadrado](#-análisis-chi-cuadrado)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Cómo funciona](#-cómo-funciona)
- [Consideraciones importantes](#-consideraciones-importantes)
- [Referencias](#-referencias)

---

## ✨ Características

- **Ocultar mensajes** de texto en imágenes PNG o BMP, con vista previa y validación de capacidad.
- **Extraer mensajes** previamente ocultados por la aplicación.
- **Analizar imágenes** con el ataque Chi-cuadrado para estimar si podrían contener un mensaje LSB.
- **Análisis progresivo** sobre ventanas crecientes de bytes (256, 512, 1024, …), útil porque el mensaje suele ocupar solo el inicio de la imagen.
- **Exportar informes** del análisis en **PDF** o **TXT**.
- **Interfaz gráfica** con Tkinter organizada en tres pestañas.
- El cálculo estadístico (incluyendo el p-valor) está implementado **sin librerías externas de estadística**.

---

## 📚 Marco teórico

La **esteganografía** consiste en ocultar información dentro de otro archivo o mensaje de forma que no sea fácilmente detectable. A diferencia de la criptografía, donde es evidente que existen datos protegidos, aquí el objetivo es que nadie sospeche que el archivo contiene algo adicional.

Ambas técnicas son **complementarias**: se puede cifrar primero el mensaje y luego ocultarlo en un archivo portador, logrando una doble capa de protección.

### Medios portadores habituales

Imágenes · Vídeo · Audio · Documentos · Tráfico de red · Código binario

### Un poco de historia

- **Antigua Grecia:** según Heródoto, se tatuaban mensajes en la cabeza rapada de esclavos y se esperaba a que creciera el cabello.
- **Tintas invisibles:** como el clásico experimento del zumo de limón.
- **1499:** Johannes Trithemius escribe *Steganographia*, el primer libro conocido sobre el tema.
- **Siglo XVI:** Girolamo Cardano inventa la «rejilla de Cardano».
- **Guerras mundiales:** uso para transmitir información confidencial.
- **Actualidad:** esteganografía digital en imágenes, audio, vídeo y redes.

### La técnica LSB

Cada canal de color de un píxel se almacena como un byte (0–255). Modificar el **bit menos significativo** cambia el valor como máximo en 1 unidad, un cambio imperceptible para el ojo humano. Ahí es donde se inserta la información oculta.

```
Byte original:   1 0 0 1 1 1 0 1   (157)
Bit del mensaje:               0
Byte modificado: 1 0 0 1 1 1 0 0   (156)
```

---

## 📊 Análisis Chi-cuadrado

Adaptado por **Westfeld y Pfitzmann (1999)** como ataque estadístico contra el reemplazo LSB.

### Fundamento

Los valores de byte se agrupan en **pares de valores (PoV)** que solo difieren en su último bit: `(0,1), (2,3), …, (254,255)`.

- En una imagen **natural**, las frecuencias de los dos valores de un par suelen ser distintas.
- Al insertar un mensaje LSB (bits casi aleatorios), las frecuencias dentro de cada par **tienden a igualarse**. Esa es la huella que busca la prueba.

### Cálculo

Para cada par `(2k, 2k+1)` con frecuencias `n₀` y `n₁`:

```
χ² (par) = (n₀ − n₁)² / (2 · (n₀ + n₁))
χ²       = Σ χ² (par)
gl       = (pares usados) − 1
```

Solo se usan los pares con frecuencia esperada ≥ 5. El **p-valor** se obtiene con la función gamma incompleta regularizada `Q(gl/2, χ²/2)`.

### Interpretación

| p-valor | Significado |
|---|---|
| ≥ 0,95 | Pares casi perfectamente equilibrados → **compatible con LSB** |
| < 0,05 | Sin el equilibrio esperado → **no hay indicios de reemplazo LSB** |
| Intermedio | **Inconcluso** |

### Análisis progresivo

Si el mensaje ocupa solo el inicio de la imagen, analizar todo de una vez diluiría el efecto. Por eso se analizan ventanas que empiezan en el primer byte y **duplican su tamaño** en cada paso; se conserva la de **mayor p-valor**.

### Limitaciones

Es un **indicio estadístico**, no una prueba definitiva: una imagen sin mensaje puede tener pares equilibrados de forma natural, y la prueba no detecta otros métodos de ocultación ni mensajes muy cortos.

---

## 🗂️ Estructura del proyecto

```
.
├── main.py                        # Punto de entrada
├── requirements.txt               # Dependencias
└── assets/
    ├── images.png
    └── images_c.png
└── claseBitWise/
    └── claseBitWise.py            # Operaciones a nivel de bit
└── claseEstego/
    ├── ClaseFoto.py               # Carga de imagen, inserción y extracción
    ├── AnalizadorChiCuadrado.py   # Ataque estadístico χ²
    ├── GeneradorInforme.py        # Exportación a PDF / TXT
    └── InterfazGrafica.py         # Interfaz Tkinter
```

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Llama a `iniciar_aplicacion()`. |
| `ClaseBitwise.py` | Manipula bits individuales de un byte con máscaras. |
| `ClaseFoto.py` | Carga la imagen, inserta y extrae el mensaje. |
| `AnalizadorChiCuadrado.py` | Histograma, χ², p-valor y análisis progresivo. |
| `GeneradorInforme.py` | Genera el informe en PDF (ReportLab) o TXT. |
| `InterfazGrafica.py` | Interfaz con tres pestañas (`ttk.Notebook`). |

---

## ⚙️ Instalación

**Requisitos:** Python 3.8 o superior (Tkinter viene incluido con la mayoría de instalaciones de Python).

```bash
# 1. Clonar el repositorio
git clone https://github.com/vladimuji/elc107_esteganografia_lsb_chi_cuadrado.git
cd tu-repositorio

# 2. (Opcional) Crear un entorno virtual
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

**Dependencias:**

```
Pillow>=9.0.0
reportlab>=4.0.0
```

---

## 🚀 Uso

```bash
python main.py
```

Se abrirá la ventana con tres pestañas:

### 1. Ocultar mensaje
1. Selecciona una imagen PNG o BMP.
2. Escribe el mensaje.
3. Pulsa **Insertar mensaje**.
4. Pulsa **Guardar imagen** (en PNG o BMP).

La aplicación valida que el mensaje no esté vacío, que sus caracteres quepan en un byte (código ≤ 255, incluye tildes y ñ) y que quepa en la imagen.

### 2. Extraer mensaje
1. Selecciona la imagen con el mensaje oculto.
2. Pulsa **Extraer mensaje**.

### 3. Analizar imagen
1. Selecciona la imagen.
2. Pulsa **Ejecutar análisis Chi-cuadrado**.
3. Revisa el estadístico, los grados de libertad, el p-valor y la interpretación.
4. Exporta el resultado con **Guardar informe PDF** o **Exportar resumen TXT**.

<!-- Puedes agregar capturas de pantalla aquí:
![Ocultar mensaje](docs/ocultar.png)
![Extraer mensaje](docs/extraer.png)
![Analizar imagen](docs/analizar.png)
-->

---

## 🔬 Cómo funciona

### Representación de la imagen

Al abrir la imagen con Pillow y convertirla a RGB, se obtiene una secuencia de bytes sin comprimir: cada píxel ocupa 3 bytes (`R, G, B, R, G, B, …`) recorridos fila por fila. El programa guarda esa secuencia en `lista_pixeles` y trabaja directamente sobre ella. El byte en la posición `i` pertenece al píxel `i // 3` y al canal `i % 3`.

### Clase `Bitwise`

Recibe una cadena de 8 bits y la manipula con máscaras. La posición 1 es el bit menos significativo.

| Método | Descripción |
|---|---|
| `set_bit1(pos)` | Fuerza un bit a 1 (máscara + `OR`). |
| `set_bit0(pos)` | Fuerza un bit a 0 (máscara invertida + `AND`). |
| `get_bit(pos)` | Lee un bit (`AND` + desplazamiento). |
| `mostrar()` | Imprime los 8 bits. |
| `bit_a_numero()` | Reconstruye el valor decimal. |

### Clase `Foto`

- **`texto_a_bits`**: convierte cada carácter a 8 bits (`"E"` → `01000101`). La interfaz agrega un carácter nulo `\x00` al final como **marca de fin**.
- **`encriptar`**: verifica la capacidad y, para cada bit del mensaje, fuerza el LSB del byte correspondiente a 0 o 1. Luego reconstruye la imagen con `Image.frombytes`.
- **`desencriptar`**: lee el LSB de cada byte, agrupa de 8 en 8, convierte a carácter y se detiene al encontrar `\x00`.

### Capacidad

Se oculta **1 bit por byte**, es decir, 3 bits por píxel:

```
capacidad (caracteres) = (ancho × alto × 3) / 8
```

Una imagen de 1000 × 1000 px admite unos **375.000 caracteres**.

### Clase `AnalizadorChiCuadrado`

| Método | Descripción |
|---|---|
| `analizar(imagen, limite_bytes)` | Histograma de 256 posiciones y evaluación (opcionalmente sobre los primeros N bytes). |
| `_evaluar(...)` | Calcula χ², grados de libertad, p-valor e interpretación. |
| `_gamma_q(a, x)` | Gamma incompleta regularizada: serie si `x < a + 1`, fracción continua en caso contrario. |
| `analizar_progresivo(imagen)` | Ventanas crecientes con histograma acumulativo; devuelve la de mayor p-valor. |
| `formatear_p_valor(...)` | Formato del p-valor y casos extremos. |

### Clase `GeneradorInforme`

- `export_summary()`: escribe un resumen en `.txt`.
- `generate_pdf()`: genera un PDF con ReportLab, con saltos de línea y de página automáticos.

Ambos incluyen la advertencia de que el resultado es un indicio y no una confirmación.

---

## ⚠️ Consideraciones importantes

- **Formato sin pérdida:** guarda siempre en **PNG o BMP**. En formatos con pérdida (JPG) la compresión altera los últimos bits y el mensaje se destruye.
- **Sin cifrado:** el mensaje se oculta en claro. Cualquiera que sepa que hay LSB puede extraerlo. Para mayor seguridad, cífralo antes.
- **Marca de fin:** la extracción se detiene en el byte nulo; en una imagen sin mensaje devolverá caracteres sin sentido.
- **Solo caracteres de un byte:** códigos ≤ 255.
- **El análisis χ² es orientativo:** debe interpretarse junto con otras técnicas.

---

## 📖 Referencias

- Westfeld, A. y Pfitzmann, A. (1999). *Attacks on Steganographic Systems*. Information Hiding, Lecture Notes in Computer Science, vol. 1768. Springer.

---

## 📄 Licencia

Proyecto con fines académicos. Agrega aquí la licencia de tu preferencia (por ejemplo, MIT).