# Magento Block Translator - Diff & Bulk Tool

## Descripción

Magento Block Translator - Diff & Bulk Tool es una aplicación desarrollada en Python con PyQt5 que permite sustituir marcadores específicos en una plantilla HTML por valores provenientes de un archivo CSV.

**¿Qué hace exactamente?**

| ACCIONES | DESCRIPCIÓN |
| -------- | ----------- |
| **Sustitución de Marcadores:**  | La herramienta busca marcadores en la plantilla HTML (por ejemplo, `!@!CLAVE!@!`) y los reemplaza por el contenido correspondiente extraído del CSV. *Nota:* La herramienta no realiza traducciones automáticas, sino que simplemente sustituye cada marcador por el valor asociado en el CSV. A la vez, el programa permite seleccionar lengua después de darle por primera vez a `Generar y Comparar`. |
| **CSV con Varias Columnas** | El archivo CSV debe tener la primera columna con la clave (que coincide con el marcador) y, a partir de la segunda columna, los valores para cada idioma. Cada columna se resalta en el editor con un color diferente, facilitando su lectura y edición. |
| **Comparación de Diferencias (Diff)** | Se muestra un diff unificado que compara el HTML original con el generado, permitiéndote ver exactamente qué cambios se han realizado. |
| **Generación Bulk** | Puedes generar archivos de salida para un idioma específico o para todos los idiomas definidos en el CSV (modo bulk). |
| **Historial y Configuración:** | La aplicación guarda un historial de las generaciones realizadas y permite configurar parámetros básicos, como el separador CSV, el patrón de marcadores y el directorio de salida. |

## Requisitos

- Python 3.x  
- PyQt5

## Instalación y Ejecución

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/mgrl39/magento_block_translator.git
   cd magento_block_translator
   ```

2. **Instala las dependencias:**

   Instala PyQt5 usando pip:
   ```bash
   pip install PyQt5
   ```

3. **Ejecuta la aplicación:**

   Simplemente ejecuta el archivo principal:
   ```bash
   python main.py
   ```

## Licencia
Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles
