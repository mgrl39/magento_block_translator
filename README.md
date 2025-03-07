# 🚀 Magento Block Translator - Diff & Bulk Tool 🌍  

## 🔍 Descripción  

**Magento Block Translator - Diff & Bulk Tool** es una aplicación 🐍 desarrollada en **Python con PyQt5** que permite sustituir **marcadores específicos** en una plantilla HTML 🏗️ por valores provenientes de un archivo **CSV** 📄.  

### 🔥 ¿Qué hace exactamente?  

| 🛠️ **ACCIÓN** | 📜 **DESCRIPCIÓN** |
| -------- | ----------- |
| ✍️ **Sustitución de Marcadores** | La herramienta busca **marcadores** en la plantilla HTML (por ejemplo, `!@!CLAVE!@!`) y los **reemplaza** por el contenido correspondiente extraído del CSV. ⚠️ *Nota:* No traduce automáticamente, solo reemplaza los valores. Además, puedes **seleccionar idioma** tras la primera ejecución de `Generar y Comparar` 🌐. |
| 📊 **CSV con Varias Columnas** | El CSV debe tener la **primera columna** con la clave (que coincide con el marcador) y, a partir de la **segunda columna**, los valores de cada idioma 🗂️. Cada columna se resalta con un color diferente 🎨 para facilitar su lectura y edición. |
| 🔎 **Comparación de Diferencias (Diff)** | Se muestra un **diff unificado** que compara el **HTML original** con el generado, permitiéndote ver **exactamente** qué cambios se han realizado 🔍. |
| ⚡ **Generación Bulk** | Puedes generar archivos de salida para **un idioma específico** o para **todos los idiomas** definidos en el CSV en modo **bulk** 🚀📂. |
| 📜 **Historial y Configuración** | Guarda un **historial** de generaciones y permite configurar **parámetros clave**, como el separador CSV, el patrón de marcadores y el directorio de salida ⚙️. |

---

## 📦 Requisitos  

✅ **Python 3.x** 🐍  
✅ **PyQt5** 🎨  

---

## 🔧 Instalación y Ejecución  

1️⃣ **Clona el repositorio** 🛠️  

```bash
git clone https://github.com/mgrl39/magento_block_translator.git
cd magento_block_translator
```

2️⃣ **Instala las dependencias** 📦  

```bash
pip install PyQt5
```

3️⃣ **Ejecuta la aplicación** ▶️  

```bash
python main.py
```

---

## 📜 Licencia  

📝 Este proyecto se distribuye bajo la **licencia MIT** 📄. Consulta el archivo `LICENSE` para más detalles ⚖️.  
