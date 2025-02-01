import csv
import signal
import difflib
import json
import os
import sys
import time
from datetime import datetime

from PyQt5 import QtWidgets, QtCore, QtGui

# ==================== Resaltador para CSV ====================
class CSVHighlighter(QtGui.QSyntaxHighlighter):
    """
    Resalta cada columna de un archivo CSV con un color distinto, utilizando
    el separador configurado.
    """
    def __init__(self, parent, separator=";"):
        super().__init__(parent)
        self.sep = separator
        # Lista de colores para las columnas
        colors = ["#FF4500", "#2E8B57", "#1E90FF", "#8A2BE2", "#FF1493", "#00CED1", "#B22222", "#FF8C00"]
        self.col_formats = []
        for color in colors:
            fmt = QtGui.QTextCharFormat()
            fmt.setForeground(QtGui.QColor(color))
            self.col_formats.append(fmt)
        # Formato para el separador (en gris)
        self.sep_format = QtGui.QTextCharFormat()
        self.sep_format.setForeground(QtGui.QColor("gray"))
    
    def highlightBlock(self, text):
        sep = self.sep
        token_start = 0
        col_index = 0
        i = 0
        while i < len(text):
            if text.startswith(sep, i):
                fmt = self.col_formats[col_index % len(self.col_formats)]
                self.setFormat(token_start, i - token_start, fmt)
                # Resaltar el separador
                self.setFormat(i, len(sep), self.sep_format)
                i += len(sep)
                token_start = i
                col_index += 1
            else:
                i += 1
        # Resaltar el último token
        if token_start < len(text):
            fmt = self.col_formats[col_index % len(self.col_formats)]
            self.setFormat(token_start, len(text) - token_start, fmt)

# ==================== Resaltador de Sintaxis para PHTML ====================
class PhtmlHighlighter(QtGui.QSyntaxHighlighter):
    """
    Resalta:
      - Etiquetas HTML (azul y en negrita)
      - Bloques PHP (anaranjado)
      - Comentarios HTML (verde)
      - Marcadores personalizados (por ejemplo: !@!CLAVE!@!, en color amarillo)
    """
    def __init__(self, parent, marker_pattern="!@![A-Z0-9_]+!@!"):
        super().__init__(parent)
        self.marker_pattern = marker_pattern
        self.rules = []
        
        # Etiquetas HTML
        tagFormat = QtGui.QTextCharFormat()
        tagFormat.setForeground(QtGui.QColor("#569CD6"))
        tagFormat.setFontWeight(QtGui.QFont.Bold)
        tagPattern = QtCore.QRegExp("</?\\b[^>]+>")
        self.rules.append((tagPattern, tagFormat))
        
        # Bloques PHP
        phpFormat = QtGui.QTextCharFormat()
        phpFormat.setForeground(QtGui.QColor("#CE9178"))
        phpPattern = QtCore.QRegExp("<\\?php.*?\\?>")
        phpPattern.setMinimal(True)
        self.rules.append((phpPattern, phpFormat))
        
        # Comentarios HTML
        commentFormat = QtGui.QTextCharFormat()
        commentFormat.setForeground(QtGui.QColor("#6A9955"))
        commentPattern = QtCore.QRegExp("<!--[^>]*-->")
        self.rules.append((commentPattern, commentFormat))
        
        # Marcadores personalizados
        markerFormat = QtGui.QTextCharFormat()
        markerFormat.setForeground(QtGui.QColor("#DCDCAA"))
        markerFormat.setFontWeight(QtGui.QFont.Bold)
        markerPattern = QtCore.QRegExp(self.marker_pattern)
        self.rules.append((markerPattern, markerFormat))
    
    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            index = pattern.indexIn(text, 0)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)
        self.setCurrentBlockState(0)

# ==================== Resaltador de Sintaxis para Diff ====================
class DiffHighlighter(QtGui.QSyntaxHighlighter):
    """
    Resalta en un diff:
      - Líneas que empiezan con '+' (verde).
      - Líneas que empiezan con '-' (rojo).
      - Líneas de metadatos (empiezan con @@) (azul).
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.rules = []
        
        plusFormat = QtGui.QTextCharFormat()
        plusFormat.setForeground(QtGui.QColor("green"))
        plusPattern = QtCore.QRegExp("^\\+.*")
        self.rules.append((plusPattern, plusFormat))
        
        minusFormat = QtGui.QTextCharFormat()
        minusFormat.setForeground(QtGui.QColor("red"))
        minusPattern = QtCore.QRegExp("^\\-.*")
        self.rules.append((minusPattern, minusFormat))
        
        metaFormat = QtGui.QTextCharFormat()
        metaFormat.setForeground(QtGui.QColor("blue"))
        metaPattern = QtCore.QRegExp("^@@.*")
        self.rules.append((metaPattern, metaFormat))
    
    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            index = pattern.indexIn(text, 0)
            while index >= 0:
                length = pattern.matchedLength()
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)
        self.setCurrentBlockState(0)

# ==================== Diálogo de Información ====================
class InfoDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Información del Programa")
        self.resize(600, 400)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        info_text = """
        <h2>Magento Block Translator - Diff & Bulk Tool</h2>
        <p>
        Esta aplicación permite:
        <ul>
            <li>Cargar una plantilla HTML con marcadores especiales (ej. <code>!@!CLAVE!@!</code>).</li>
            <li>Cargar un archivo CSV con traducciones para diferentes idiomas.</li>
            <li>Generar salidas traducidas reemplazando los marcadores por sus correspondientes traducciones.</li>
            <li>Comparar la plantilla original con la salida generada mediante un diff unificado.</li>
            <li>Generar archivos HTML para cada idioma seleccionado o en modo bulk (todos los idiomas).</li>
        </ul>
        </p>
        <p>
        <b>Nota Importante:</b> Es fundamental que el archivo CSV mantenga la misma cantidad de columnas en todas las filas, ya que se basa en posiciones fijas para asociar las traducciones con sus claves.
        Si se detecta que algunas filas tienen un número diferente de columnas, la aplicación avisará y se podrá optar por continuar, aunque esto podría provocar errores en las traducciones.
        </p>
        <p>
        Además, el editor CSV muestra cada columna en un color diferente, utilizando el separador configurado, para facilitar su lectura y edición.
        </p>
        <p>
        Para más información y para acceder al código fuente, visita mi repositorio en GitHub:
        <a href="https://github.com/mgrl39/magento_block_translator" style="color: #1E90FF;">https://github.com/mgrl39/magento_block_translator</a>
        </p>
        <p>
        <i>Desarrollado con PyQt5 y Python.</i>
        </p>
        """
        text_edit = QtWidgets.QTextBrowser()
        text_edit.setHtml(info_text)
        text_edit.setOpenExternalLinks(True)
        layout.addWidget(text_edit)
        
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

# ==================== Diálogo de Ajustes ====================
class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, current_settings):
        super().__init__(parent)
        self.setWindowTitle("Ajustes")
        self.resize(400, 200)
        self.settings = current_settings.copy()
        
        layout = QtWidgets.QFormLayout(self)
        self.sep_edit = QtWidgets.QLineEdit(self.settings.get("csv_separator", ";"))
        layout.addRow("Separador CSV:", self.sep_edit)
        
        self.marker_edit = QtWidgets.QLineEdit(self.settings.get("marker_pattern", "!@![A-Z0-9_]+!@!"))
        layout.addRow("Patrón de Marcador:", self.marker_edit)
        
        self.output_dir_edit = QtWidgets.QLineEdit(self.settings.get("output_dir", os.getcwd()))
        output_btn = QtWidgets.QPushButton("Examinar...")
        output_btn.clicked.connect(self.select_output_dir)
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.output_dir_edit)
        h_layout.addWidget(output_btn)
        layout.addRow("Directorio Salida:", h_layout)
        
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def select_output_dir(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Selecciona Directorio de Salida", self.output_dir_edit.text())
        if dir:
            self.output_dir_edit.setText(dir)
    
    def accept(self):
        self.settings["csv_separator"] = self.sep_edit.text() or ";"
        self.settings["marker_pattern"] = self.marker_edit.text() or "!@![A-Z0-9_]+!@!"
        self.settings["output_dir"] = self.output_dir_edit.text() or os.getcwd()
        super().accept()

# ==================== Ventana Principal ====================
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magento Block Translator - Diff & Bulk Tool")
        self.resize(1300, 900)
        QtWidgets.QApplication.setStyle("Fusion")
        
        # Configuración predeterminada (se puede guardar/cargar)
        self.config = {
            "csv_separator": ";",
            "marker_pattern": "!@![A-Z0-9_]+!@!",
            "output_dir": os.getcwd()
        }
        self.history = []  # Lista de registros de generación
        
        self.init_ui()
        self.create_menu()
    
    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        
        # Pestañas principales: Edición, Comparación Diff y Historial
        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.create_edit_tab()
        self.create_diff_tab()
        self.create_history_tab()
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        open_html_act = QtWidgets.QAction("Abrir HTML...", self)
        open_html_act.triggered.connect(self.menu_open_html)
        file_menu.addAction(open_html_act)
        
        open_csv_act = QtWidgets.QAction("Abrir CSV...", self)
        open_csv_act.triggered.connect(self.menu_open_csv)
        file_menu.addAction(open_csv_act)
        
        save_config_act = QtWidgets.QAction("Guardar Configuración...", self)
        save_config_act.triggered.connect(self.menu_save_config)
        file_menu.addAction(save_config_act)
        
        load_config_act = QtWidgets.QAction("Cargar Configuración...", self)
        load_config_act.triggered.connect(self.menu_load_config)
        file_menu.addAction(load_config_act)
        
        file_menu.addSeparator()
        exit_act = QtWidgets.QAction("Salir", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)
        
        # Menú Ajustes
        settings_menu = menubar.addMenu("&Ajustes")
        edit_settings_act = QtWidgets.QAction("Editar Ajustes...", self)
        edit_settings_act.triggered.connect(self.edit_settings)
        settings_menu.addAction(edit_settings_act)
        
        # Menú Ayuda / Información
        help_menu = menubar.addMenu("&Ayuda")
        info_act = QtWidgets.QAction("Acerca de", self)
        info_act.triggered.connect(self.show_info)
        help_menu.addAction(info_act)
    
    def create_edit_tab(self):
        self.edit_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.edit_tab)
        
        # Grupo: Plantilla HTML
        group_html = QtWidgets.QGroupBox("Plantilla HTML (Block de Magento)")
        html_layout = QtWidgets.QVBoxLayout(group_html)
        self.html_editor = QtWidgets.QPlainTextEdit()
        self.html_editor.setFont(QtGui.QFont("Consolas", 10))
        html_layout.addWidget(self.html_editor)
        self.html_highlighter = PhtmlHighlighter(self.html_editor.document(), self.config["marker_pattern"])
        layout.addWidget(group_html)
        
        # Grupo: CSV de Traducciones
        group_csv = QtWidgets.QGroupBox("Traducciones (CSV)")
        csv_layout = QtWidgets.QVBoxLayout(group_csv)
        self.csv_editor = QtWidgets.QPlainTextEdit()
        self.csv_editor.setFont(QtGui.QFont("Consolas", 10))
        csv_layout.addWidget(self.csv_editor)
        # Asignar resaltador CSV para colorear columnas
        self.csv_highlighter = CSVHighlighter(self.csv_editor.document(), self.config["csv_separator"])
        
        # CSV de ejemplo
        sample_csv = (
            "clave" + self.config["csv_separator"] + "es" + self.config["csv_separator"] + "en" +
            self.config["csv_separator"] + "fr" + self.config["csv_separator"] + "it" + self.config["csv_separator"] + "pt\n" +
            "TEXTO_EMAIL" + self.config["csv_separator"] +
            "Enviar un email" + self.config["csv_separator"] +
            "Send an email" + self.config["csv_separator"] +
            "Envoyez un email" + self.config["csv_separator"] +
            "Invia una mail" + self.config["csv_separator"] +
            "Enviar um e-mail\n"
        )
        self.csv_editor.setPlainText(sample_csv)
        layout.addWidget(group_csv)
        
        # Controles: Selección de idioma y opciones Bulk
        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.addWidget(QtWidgets.QLabel("Idioma:"))
        self.lang_combo = QtWidgets.QComboBox()
        controls_layout.addWidget(self.lang_combo)
        
        self.bulk_check = QtWidgets.QCheckBox("Generar Bulk (todos los idiomas)")
        controls_layout.addWidget(self.bulk_check)
        
        self.generate_btn = QtWidgets.QPushButton("Generar y Comparar")
        self.generate_btn.clicked.connect(self.generate_and_compare)
        controls_layout.addWidget(self.generate_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        self.tabs.addTab(self.edit_tab, "Edición")
    
    def create_diff_tab(self):
        self.diff_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.diff_tab)
        
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        layout.addWidget(splitter)
        
        # Editor: Plantilla Original
        group_orig = QtWidgets.QGroupBox("Plantilla Original")
        orig_layout = QtWidgets.QVBoxLayout(group_orig)
        self.diff_original = QtWidgets.QPlainTextEdit()
        self.diff_original.setReadOnly(True)
        self.diff_original.setFont(QtGui.QFont("Consolas", 10))
        orig_layout.addWidget(self.diff_original)
        
        # Editor: Salida Generada
        group_gen = QtWidgets.QGroupBox("Salida Generada")
        gen_layout = QtWidgets.QVBoxLayout(group_gen)
        self.diff_generated = QtWidgets.QPlainTextEdit()
        self.diff_generated.setReadOnly(True)
        self.diff_generated.setFont(QtGui.QFont("Consolas", 10))
        gen_layout.addWidget(self.diff_generated)
        
        # Editor: Diff Unificado
        group_diff = QtWidgets.QGroupBox("Diferencias (Diff)")
        diff_layout = QtWidgets.QVBoxLayout(group_diff)
        self.diff_view = QtWidgets.QPlainTextEdit()
        self.diff_view.setReadOnly(True)
        self.diff_view.setFont(QtGui.QFont("Consolas", 10))
        diff_layout.addWidget(self.diff_view)
        
        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.addWidget(group_orig)
        container_layout.addWidget(group_gen)
        container_layout.addWidget(group_diff)
        splitter.addWidget(container)
        
        self.tabs.addTab(self.diff_tab, "Comparación Diff")
        self.diff_highlighter = DiffHighlighter(self.diff_view.document())
    
    def create_history_tab(self):
        self.history_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.history_tab)
        self.history_view = QtWidgets.QPlainTextEdit()
        self.history_view.setReadOnly(True)
        self.history_view.setFont(QtGui.QFont("Consolas", 10))
        layout.addWidget(self.history_view)
        self.tabs.addTab(self.history_tab, "Historial")
    
    def menu_open_html(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Abrir Archivo HTML", "", "Archivos HTML (*.html);;Todos los archivos (*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.html_editor.setPlainText(f.read())
                self.statusBar().showMessage(f"HTML cargado: {os.path.basename(path)}", 5000)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo leer el archivo HTML:\n{e}")
    
    def menu_open_csv(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Abrir Archivo CSV", "", "Archivos CSV (*.csv);;Todos los archivos (*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.csv_editor.setPlainText(f.read())
                self.statusBar().showMessage(f"CSV cargado: {os.path.basename(path)}", 5000)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo leer el archivo CSV:\n{e}")
    
    def menu_save_config(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar Configuración", "", "JSON (*.json)")
        if path:
            if not path.lower().endswith(".json"):
                path += ".json"
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=4)
                self.statusBar().showMessage("Configuración guardada", 5000)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo guardar la configuración:\n{e}")
    
    def menu_load_config(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Cargar Configuración", "", "JSON (*.json)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                # Actualizar editores y resaltadores según la nueva configuración
                self.html_highlighter = PhtmlHighlighter(self.html_editor.document(), self.config.get("marker_pattern", "!@![A-Z0-9_]+!@!"))
                sample_csv = (
                    "clave" + self.config.get("csv_separator", ";") + "es" + self.config.get("csv_separator", ";") +
                    "en" + self.config.get("csv_separator", ";") +
                    "fr" + self.config.get("csv_separator", ";") +
                    "it" + self.config.get("csv_separator", ";") +
                    "pt\n" +
                    "TEXTO_EMAIL" + self.config.get("csv_separator", ";") +
                    "Enviar un email" + self.config.get("csv_separator", ";") +
                    "Send an email" + self.config.get("csv_separator", ";") +
                    "Envoyez un email" + self.config.get("csv_separator", ";") +
                    "Invia una mail" + self.config.get("csv_separator", ";") +
                    "Enviar um e-mail\n"
                )
                self.csv_editor.setPlainText(sample_csv)
                # Actualizar el resaltador CSV con el nuevo separador
                self.csv_highlighter = CSVHighlighter(self.csv_editor.document(), self.config.get("csv_separator", ";"))
                self.statusBar().showMessage("Configuración cargada", 5000)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo cargar la configuración:\n{e}")
    
    def edit_settings(self):
        dlg = SettingsDialog(self, self.config)
        if dlg.exec_():
            self.config = dlg.settings
            # Actualizar resaltador con el nuevo patrón
            self.html_highlighter = PhtmlHighlighter(self.html_editor.document(), self.config["marker_pattern"])
            # Actualizar resaltador CSV con el nuevo separador
            self.csv_highlighter = CSVHighlighter(self.csv_editor.document(), self.config["csv_separator"])
            self.statusBar().showMessage("Ajustes actualizados", 5000)
    
    def show_info(self):
        dlg = InfoDialog(self)
        dlg.exec_()

    def parse_csv(self, csv_text):
        """
        Procesa el CSV usando el separador configurado y devuelve:
          - languages: lista de idiomas (desde la segunda columna).
          - translations: diccionario { clave: { idioma: traducción, ... } }

        Si el delimitador es de un solo carácter se usa el módulo csv, de lo contrario se
        utiliza una división de cadena simple. Además, se notifica si hay filas con número
        de columnas diferente al del encabezado.
        """
        translations = {}
        languages = []
        sep = self.config.get("csv_separator", ";")
        inconsistent_rows = 0

        try:
            lines = csv_text.strip().splitlines()
            if not lines:
                raise ValueError("El CSV está vacío.")
            
            # Si el delimitador es de un solo carácter, usar el módulo csv
            if len(sep) == 1:
                reader = csv.reader(lines, delimiter=sep)
                rows = list(reader)
            else:
                # Delimitador multi-caracter: usar división simple
                rows = [line.split(sep) for line in lines]

            if not rows:
                raise ValueError("El CSV no contiene datos.")
            
            headers = rows[0]
            if len(headers) < 2:
                raise ValueError("El CSV debe tener al menos 2 columnas (clave y un idioma).")
            header_count = len(headers)
            languages = headers[1:]
            
            # Contar filas con número de columnas inconsistente
            for row in rows[1:]:
                if len(row) != header_count:
                    inconsistent_rows += 1

            if inconsistent_rows > 0:
                ret = QtWidgets.QMessageBox.question(
                    self,
                    "Inconsistencia en CSV",
                    f"Se han detectado {inconsistent_rows} fila(s) con un número de columnas diferente al del encabezado.\n"
                    "Esto puede provocar errores en las traducciones, ya que se deben mantener las posiciones fijas.\n"
                    "¿Desea continuar de todas formas?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                if ret == QtWidgets.QMessageBox.No:
                    return [], {}
            
            # Procesar filas, rellenando o recortando para ajustar al número de columnas del encabezado.
            for row in rows[1:]:
                if len(row) < header_count:
                    row = row + [""] * (header_count - len(row))
                elif len(row) > header_count:
                    row = row[:header_count]
                key = row[0].strip()
                translations[key] = {}
                for i, lang in enumerate(languages):
                    # Si el valor no existe (por cualquier motivo), se asigna cadena vacía.
                    translations[key][lang] = row[i+1].strip() if i+1 < len(row) else ""
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error al procesar CSV", str(e))
            return [], {}

        return languages, translations


    
    def generate_and_compare(self):
        """
        Genera la salida reemplazando marcadores en la plantilla según las traducciones
        del CSV. Si se marca “Bulk”, genera para todos los idiomas.
        Actualiza la pestaña Diff y guarda en el historial.
        """
        template = self.html_editor.toPlainText()
        csv_text = self.csv_editor.toPlainText()
        if not template.strip():
            QtWidgets.QMessageBox.critical(self, "Error", "La plantilla HTML está vacía.")
            return
        if not csv_text.strip():
            QtWidgets.QMessageBox.critical(self, "Error", "El CSV está vacío.")
            return

        languages, translations = self.parse_csv(csv_text)
        if not languages:
            return

        # Actualizar combo de idiomas si es necesario
        current_langs = [self.lang_combo.itemText(i) for i in range(self.lang_combo.count())]
        if current_langs != languages:
            self.lang_combo.clear()
            self.lang_combo.addItems(languages)

        results = {}  # Almacena salida para cada idioma generado
        if self.bulk_check.isChecked():
            langs_to_generate = languages
        else:
            lang_sel = self.lang_combo.currentText() or languages[0]
            langs_to_generate = [lang_sel]

        for lang in langs_to_generate:
            output = template
            for key, trans in translations.items():
                placeholder = f"!@!{key}!@!"
                value = trans.get(lang, "")
                output = output.replace(placeholder, value)
            results[lang] = output

        # Actualizar la pestaña Diff
        self.diff_original.setPlainText(template)
        
        if not self.bulk_check.isChecked():
            # Modo individual: se muestra el diff del idioma seleccionado
            selected_lang = langs_to_generate[0]
            self.diff_generated.setPlainText(results[selected_lang])
            diff_lines = list(difflib.unified_diff(
                template.splitlines(),
                results[selected_lang].splitlines(),
                fromfile="Original",
                tofile=f"Generado ({selected_lang})",
                lineterm=""
            ))
            self.diff_view.setPlainText("\n".join(diff_lines))
        else:
            # Modo Bulk: concatenar diffs de todos los idiomas
            bulk_diff = ""
            for lang in langs_to_generate:
                bulk_diff += f"========== Diff para {lang} ==========\n"
                diff_lines = list(difflib.unified_diff(
                    template.splitlines(),
                    results[lang].splitlines(),
                    fromfile="Original",
                    tofile=f"Generado ({lang})",
                    lineterm=""
                ))
                bulk_diff += "\n".join(diff_lines) + "\n\n"
            # Puedes también dejar un mensaje en el área de "Salida Generada" si lo deseas
            self.diff_generated.setPlainText("Se han generado múltiples salidas (ver diff abajo).")
            self.diff_view.setPlainText(bulk_diff)

        self.tabs.setCurrentWidget(self.diff_tab)
        
        # Guardar historial del evento
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hist_entry = {
            "timestamp": now,
            "idiomas": langs_to_generate,
            "output_dir": self.config.get("output_dir", os.getcwd())
        }
        self.history.append(hist_entry)
        self.update_history_view()
        
        # Generar archivos de salida en el directorio configurado
        output_dir = self.config.get("output_dir", os.getcwd())
        os.makedirs(output_dir, exist_ok=True)
        errors = []
        for lang, content in results.items():
            filename = f"template_{lang}.html"
            path = os.path.join(output_dir, filename)
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                errors.append(f"{filename}: {e}")
        if errors:
            QtWidgets.QMessageBox.critical(self, "Errores al generar archivos", "\n".join(errors))
        else:
            QtWidgets.QMessageBox.information(self, "Generación exitosa", f"Archivos generados en:\n{output_dir}")
            self.statusBar().showMessage("Proceso completado.", 5000)

    
    def update_history_view(self):
        """Actualiza la pestaña de Historial con los registros de generación."""
        lines = []
        for entry in self.history:
            line = f"{entry['timestamp']} - Idiomas: {', '.join(entry['idiomas'])} - Salida: {entry['output_dir']}"
            lines.append(line)
        self.history_view.setPlainText("\n".join(lines))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    def sigint_handler(sig, frame):
        print("SIGINT recibido, cerrando la aplicación.")
        app.quit()
    signal.signal(signal.SIGINT, sigint_handler)
    timer = QtCore.QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)
    sys.exit(app.exec_())
