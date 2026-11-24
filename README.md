# 🍦 Heladería La Dulce — Sistema de Ventas & Predicciones Climáticas

Aplicación web interactiva desarrollada en **Python + Streamlit + Plotly + SQLite** con diseño estilo *Gelatería Artesanal Pastel*. Integra catálogo interactivo con carrito de compras, registro y checkout de pedidos, análisis histórico de ventas y un motor inteligente de predicciones según temperatura y hora del día.

---

## 🚀 Cómo ejecutar en cualquier PC

### Paso 1: Requisitos previos en el PC destino
- Tener instalado **Python 3.9 o superior** (descargable gratis desde [python.org](https://www.python.org/downloads/)).
  > *Importante al instalar Python:* Marcar la casilla **"Add Python to PATH"**.

---

### Paso 2: Ejecución Rápida en Windows (Doble Clic)
1. Descomprime la carpeta del proyecto en el nuevo PC.
2. Haz doble clic en el archivo **`iniciar_heladeria.bat`**.
3. El archivo instalará automáticamente las dependencias si no están instaladas y abrirá el navegador en:
   **`http://localhost:8501`**

---

### Paso 2 (Alternativa por Terminal):
Abre la consola (CMD o PowerShell) en la carpeta del proyecto y ejecuta:

```bash
# 1. Instalar librerías
pip install -r requirements.txt

# 2. Iniciar la aplicación
streamlit run app.py
```

---

## 🌐 Cómo compartirlo con otras personas

### Opción 1: Archivo ZIP / Memoria USB
1. Comprime toda esta carpeta `Heladeria` en un archivo `.zip`.
2. Envíalo por correo, Google Drive, WhatsApp o cópialo a una memoria USB.
3. En el otro computador, se descomprime y se ejecuta con `iniciar_heladeria.bat`.

### Opción 2: En la misma red Wi-Fi (Local comercial o casa)
Si ambos computadores o un celular están conectados a la misma red Wi-Fi:
1. En el PC donde corre la app, ejecuta en la consola `ipconfig` para conocer tu IPv4 (ej. `192.168.1.15`).
2. En el otro computador o teléfono abre el navegador y escribe:
   `http://192.168.1.15:8501`

### Opción 3: Publicarlo en Internet Gratis (Streamlit Community Cloud)
1. Sube estos archivos a un repositorio de **GitHub**.
2. Entra a [share.streamlit.io](https://share.streamlit.io) con tu cuenta de GitHub.
3. Selecciona el repositorio y el archivo `app.py`.
4. ¡Obtendrás un enlace web público accesible desde cualquier dispositivo del mundo sin necesidad de tener Python instalado!

---

## 📂 Archivos del Proyecto

```text
Heladeria/
├── app.py                 # Aplicación web completa y dashboard
├── database.py            # Base de datos SQLite (ventas, clima, horas)
├── heladeria.db           # Base de datos local autogestionada
├── requirements.txt       # Librerías Python necesarias
├── iniciar_heladeria.bat  # Ejecutable de 1 clic para Windows
└── README.md              # Guía de instalación y uso
```

---

## 🍧 Módulos y Funcionalidades

1. **🏠 Inicio / Menú:** Catálogo de 15 productos con categorías, precios, contadores `➕`/`➖` y barra flotante de pedido.
2. **🛒 Pedido:** Carrito interactivo con control de cantidades, registro de clima, temperatura y hora de venta con base de datos SQLite.
3. **📋 Historial:** KPIs de ventas totales, ticket promedio, gráficas de productos top y evolución cronológica.
4. **🌦️ Clima & Ventas:**
   - Análisis por clima y día de la semana.
   - Subpestaña horaria con gráfica de doble eje (ventas vs temperatura), mapas de calor y dispersión multivariable.
5. **🔮 Predicciones:**
   - **🌤️ Simulador Diario:** Proyección de ventas por clima y temperatura, nivel de demanda, curva horaria y tabla de planificación.
   - **📅 Planificador Semanal:** Proyección de ingresos a 7 días y día pico de ventas.
