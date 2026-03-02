import sys
import io
import numpy as np
import pandas as pd
from scipy.stats import norm

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QFileDialog, QMessageBox

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

TEXT = {
    "PL": {
        "title": "Analiza próby — Przedział Ufności",
        "btn_load": "Import CSV / Excel",
        "btn_paste": "Wklej dane (kolumna wyników)",
        "conf_level": "Poziom ufności (%):",
        "margin_error": "Margines błędu (mg/L):",
        "run": "Oblicz optymalną próbę",
        "lang_btn": "PL / EN",
        "file_dialog": "Wybierz plik",
        "file_filter": "CSV (*.csv);;Excel (*.xlsx *.xls)",
        "err_load": "Nie można wczytać pliku:\n{}",
        "no_data": "Brak danych w pamięci.",
        "clipboard_empty": "Schowek jest pusty.",
        "clipboard_title": "Brak danych",
        "clipboard_err": "Błąd parsowania wklejonych danych: {}",
        "pasted_cols": "Załadowano wklejone dane.",
        "loaded_cols": "Wczytano plik: {}",
        "error_title": "Błąd logiczny",
        "calc_result": "Zbadano próbę. Poziom ufności: {}%, Zakładany błąd E: {}. Obliczono sigma={:.4f}, Z={:.4f}. Minimalna wymagana próba n={}.",
        "plot_title": "Margines błędu w funkcji wielkości próby",
        "plot_xlabel": "Wielkość próby (n)",
        "plot_ylabel": "Margines błędu (E)",
        "plot_l1": "Krzywa błędu standardowego",
        "plot_l2": "Docelowy maksymalny błąd (E)",
        "plot_l3": "Wymagane n"
    },
    "EN": {
        "title": "Sample Analysis — Confidence Interval",
        "btn_load": "Import CSV / Excel",
        "btn_paste": "Paste data (column of results)",
        "conf_level": "Confidence level (%):",
        "margin_error": "Margin of error (mg/L):",
        "run": "Calculate optimal sample",
        "lang_btn": "PL / EN",
        "file_dialog": "Select file",
        "file_filter": "CSV (*.csv);;Excel (*.xlsx *.xls)",
        "err_load": "Cannot load file:\n{}",
        "no_data": "No data in memory.",
        "clipboard_empty": "Clipboard is empty.",
        "clipboard_title": "No data",
        "clipboard_err": "Parse error: {}",
        "pasted_cols": "Pasted data loaded.",
        "loaded_cols": "Loaded file: {}",
        "error_title": "Logical error",
        "calc_result": "Sample analyzed. Confidence: {}%, Target error E: {}. Calculated sigma={:.4f}, Z={:.4f}. Minimum required sample n={}.",
        "plot_title": "Margin of error vs Sample size",
        "plot_xlabel": "Sample size (n)",
        "plot_ylabel": "Margin of error (E)",
        "plot_l1": "Standard error curve",
        "plot_l2": "Target max error (E)",
        "plot_l3": "Required n"
    }
}

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=6, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        super().__init__(fig)
        self.axes = fig.subplots(1, 1)

class SampleSizeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "PL"
        self.df = None
        self._build_ui()
        self._apply_language()

    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        controls = QtWidgets.QHBoxLayout()
        layout.addLayout(controls)

        self.btn_load = QtWidgets.QPushButton()
        self.btn_load.clicked.connect(self.load_file)
        controls.addWidget(self.btn_load)

        self.btn_paste = QtWidgets.QPushButton()
        self.btn_paste.clicked.connect(self.paste_data)
        controls.addWidget(self.btn_paste)

        controls.addSpacing(10)
        self.lbl_conf = QtWidgets.QLabel()
        controls.addWidget(self.lbl_conf)
        self.spin_conf = QtWidgets.QDoubleSpinBox()
        self.spin_conf.setRange(50.0, 99.99)
        self.spin_conf.setValue(95.0)
        controls.addWidget(self.spin_conf)

        self.lbl_margin = QtWidgets.QLabel()
        controls.addWidget(self.lbl_margin)
        self.spin_margin = QtWidgets.QDoubleSpinBox()
        self.spin_margin.setRange(0.01, 1000.0)
        self.spin_margin.setValue(0.5)
        self.spin_margin.setSingleStep(0.1)
        controls.addWidget(self.spin_margin)

        self.btn_run = QtWidgets.QPushButton()
        self.btn_run.clicked.connect(self.run_calculation)
        controls.addWidget(self.btn_run)

        self.btn_lang = QtWidgets.QPushButton()
        self.btn_lang.clicked.connect(self.toggle_language)
        controls.addWidget(self.btn_lang)

        self.canvas = MplCanvas(self, width=8, height=5)
        layout.addWidget(self.canvas)

        self.txt_log = QtWidgets.QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(120)
        layout.addWidget(self.txt_log)

    def _apply_language(self):
        t = TEXT[self.lang]
        self.setWindowTitle(t["title"])
        self.btn_load.setText(t["btn_load"])
        self.btn_paste.setText(t["btn_paste"])
        self.lbl_conf.setText(t["conf_level"])
        self.lbl_margin.setText(t["margin_error"])
        self.btn_run.setText(t["run"])
        self.btn_lang.setText(t["lang_btn"])

    def toggle_language(self):
        self.lang = "EN" if self.lang == "PL" else "PL"
        self._apply_language()

    def log(self, key, *args):
        msg = TEXT[self.lang][key].format(*args)
        self.txt_log.append(msg)

    def load_file(self):
        t = TEXT[self.lang]
        path, _ = QFileDialog.getOpenFileName(
            self, t["file_dialog"], "", t["file_filter"]
        )
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
        except Exception as e:
            QMessageBox.critical(self, t["error_title"], t["err_load"].format(e))
            return
        self.df = df
        self.log("loaded_cols", path)

    def paste_data(self):
        t = TEXT[self.lang]
        text = QtWidgets.QApplication.clipboard().text()
        if not text.strip():
            QMessageBox.information(self, t["clipboard_title"], t["clipboard_empty"])
            return
        try:
            df = pd.read_csv(io.StringIO(text), sep=None, engine="python")
            if df.shape[1] > 1:
                df = df.iloc[:, [0]]
        except Exception:
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            try:
                vals = [float(l.replace(",", ".")) for l in lines]
                df = pd.DataFrame({"obs": vals})
            except Exception as e:
                QMessageBox.critical(self, t["error_title"], t["clipboard_err"].format(e))
                return
        self.df = df
        self.log("pasted_cols")

    def run_calculation(self):
        t = TEXT[self.lang]
        if self.df is None or self.df.empty:
            QMessageBox.critical(self, t["error_title"], t["no_data"])
            return

        try:
            vals = self.df.iloc[:, 0].astype(float).values
        except Exception as e:
            QMessageBox.critical(self, t["error_title"], str(e))
            return

        sigma = float(np.std(vals, ddof=1))
        if sigma == 0:
            QMessageBox.critical(self, t["error_title"], "Sigma wynosi 0.")
            return

        conf = self.spin_conf.value()
        margin = self.spin_margin.value()

        alpha = 1.0 - (conf / 100.0)
        z_score = norm.ppf(1.0 - (alpha / 2.0))

        n_req = ((z_score * sigma) / margin) ** 2
        n_req_ceil = int(np.ceil(n_req))

        self.log("calc_result", conf, margin, sigma, z_score, n_req_ceil)

        plot_max_n = max(n_req_ceil * 3, 50)
        n_plot = np.arange(2, plot_max_n)
        e_plot = z_score * sigma / np.sqrt(n_plot)

        ax = self.canvas.axes
        ax.clear()
        ax.plot(n_plot, e_plot, label=t["plot_l1"], color="#1f77b4", linewidth=2)
        ax.axhline(y=margin, color="#d62728", linestyle="--", label=t["plot_l2"])
        ax.axvline(x=n_req_ceil, color="#2ca02c", linestyle=":", label=t["plot_l3"], linewidth=2)
        
        ax.set_title(t["plot_title"])
        ax.set_xlabel(t["plot_xlabel"])
        ax.set_ylabel(t["plot_ylabel"])
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        self.canvas.draw()

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = SampleSizeApp()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()