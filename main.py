import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIntValidator, QColor, QPainter, QPen


# ================= CONFIG =================
CELL_W = 50
CELL_H = 36
CELL_SPACING = 6

FONT_CELL = QFont("Consolas", 12)
FONT_OP = QFont("Consolas", 18)

COLOR_BORDER = "#CCCCCC"
COLOR_INPUT = "#FFFFFF"
COLOR_READONLY = "#F5F5F5"
COLOR_BRACKET = "#666666"
COLOR_TEXT = "#333333"


# ================= MATRIX CELL =================
class MatrixCell(QLineEdit):
    def __init__(self, readonly=False):
        super().__init__("0")
        self.setReadOnly(readonly)

    def focusInEvent(self, event):
        if not self.isReadOnly():
            if self.text() == "0":
                self.clear()
            else:
                self.selectAll()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        if not self.isReadOnly() and self.text().strip() == "":
            self.setText("0")
        super().focusOutEvent(event)


# ================= BRACKET WIDGET =================
class BracketWidget(QWidget):
    def __init__(self, is_left=True, parent=None):
        super().__init__(parent)
        self.is_left = is_left
        self.setFixedWidth(12)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(COLOR_BRACKET))
        pen.setWidth(2)
        painter.setPen(pen)

        w = self.width()
        h = self.height()

        if self.is_left:
            painter.drawLine(w - 4, 1, 4, 1)
            painter.drawLine(4, 1, 4, h - 1)
            painter.drawLine(4, h - 1, w - 4, h - 1)
        else:
            painter.drawLine(4, 1, w - 4, 1)
            painter.drawLine(w - 4, 1, w - 4, h - 1)
            painter.drawLine(4, h - 1, w - 4, h - 1)


# ================= MATRIX WIDGET =================
class MatrixWidget(QWidget):
    def __init__(self, size: int, readonly=False):
        super().__init__()
        self.size = size
        self.readonly = readonly
        self.cells = []
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        row = QHBoxLayout(container)
        row.setSpacing(6)
        row.setContentsMargins(0, 0, 0, 0)

        grid_h = self.size * CELL_H + (self.size - 1) * CELL_SPACING
        grid_w = self.size * CELL_W + (self.size - 1) * CELL_SPACING

        grid_widget = QWidget()
        grid_widget.setFixedSize(grid_w, grid_h)
        grid = QGridLayout(grid_widget)
        grid.setSpacing(CELL_SPACING)
        grid.setContentsMargins(0, 0, 0, 0)

        for r in range(self.size):
            row_cells = []
            for c in range(self.size):
                cell = MatrixCell(self.readonly)
                cell.setFont(FONT_CELL)
                cell.setAlignment(Qt.AlignCenter)
                cell.setFixedSize(CELL_W, CELL_H)

                if not self.readonly:
                    cell.setValidator(QIntValidator(-9999, 9999))

                bg = COLOR_READONLY if self.readonly else COLOR_INPUT
                cell.setStyleSheet(f"""
                    QLineEdit {{
                        background-color: {bg};
                        border: 1px solid {COLOR_BORDER};
                        border-radius: 3px;
                    }}
                """)

                grid.addWidget(cell, r, c)
                row_cells.append(cell)
            self.cells.append(row_cells)

        left = BracketWidget(True)
        right = BracketWidget(False)
        left.setFixedHeight(grid_h)
        right.setFixedHeight(grid_h)

        row.addWidget(left)
        row.addWidget(grid_widget)
        row.addWidget(right)

        main.addWidget(container, alignment=Qt.AlignCenter)

    def get_matrix(self):
        try:
            return [[int(c.text() or "0") for c in row] for row in self.cells]
        except ValueError:
            return None

    def set_matrix(self, data):
        for i in range(self.size):
            for j in range(self.size):
                self.cells[i][j].setText(str(data[i][j]))

    def clear_matrix(self):
        for row in self.cells:
            for cell in row:
                cell.setText("0")


# ================= MAIN WINDOW =================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.A = self.B = self.C = None
        self._build_ui()
        self._apply_styles()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(20)
        root.setContentsMargins(15, 15, 15, 15)

        top = QHBoxLayout()
        lbl = QLabel("Bậc ma trận:")
        lbl.setFont(QFont("Arial", 20, QFont.Bold))

        self.size_input = QLineEdit()
        self.size_input.setFont(QFont("Consolas", 22))
        self.size_input.setAlignment(Qt.AlignCenter)
        self.size_input.setValidator(QIntValidator(1, 9))
        self.size_input.setFixedSize(280, 60)
        self.size_input.returnPressed.connect(self.create_matrices)

        top.addStretch()
        top.addWidget(lbl)
        top.addWidget(self.size_input)
        top.addStretch()
        root.addLayout(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none}")
        root.addWidget(scroll)

        container = QWidget()
        self.matrix_row = QHBoxLayout(container)
        self.matrix_row.setAlignment(Qt.AlignCenter)
        scroll.setWidget(container)

        btns = QHBoxLayout()
        self.clear_btn = QPushButton("Reset")
        self.calc_btn = QPushButton("Calculate")
        for b in (self.clear_btn, self.calc_btn):
            b.setFixedSize(140, 45)
            b.setEnabled(False)

        self.clear_btn.clicked.connect(self.clear_all)
        self.calc_btn.clicked.connect(self.multiply)

        btns.addStretch()
        btns.addWidget(self.clear_btn)
        btns.addWidget(self.calc_btn)
        btns.addStretch()
        root.addLayout(btns)

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QWidget {{ background:#FFFFFF; }}
            QPushButton {{
                border:1px solid {COLOR_BORDER};
                background:#F5F5F5;
            }}
            QPushButton:hover {{ background:#EEEEEE; }}
            QPushButton:disabled {{ color:#AAAAAA; }}
        """)

    def create_matrices(self):
        n = int(self.size_input.text())
        if not (1 <= n <= 9):
            QMessageBox.warning(self, "Lỗi", "Bậc phải từ 1 đến 9")
            return

        while self.matrix_row.count():
            item = self.matrix_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            del item

        self.A = MatrixWidget(n)
        self.B = MatrixWidget(n)
        self.C = MatrixWidget(n, readonly=True)

        mul = QLabel("×")
        eq = QLabel("=")
        mul.setFont(FONT_OP)
        eq.setFont(FONT_OP)

        self.matrix_row.addWidget(self.A)
        self.matrix_row.addWidget(mul)
        self.matrix_row.addWidget(self.B)
        self.matrix_row.addWidget(eq)
        self.matrix_row.addWidget(self.C)

        self.calc_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.A.cells[0][0].setFocus()

    def multiply(self):
        A = self.A.get_matrix()
        B = self.B.get_matrix()
        if A is None or B is None:
            QMessageBox.warning(self, "Lỗi", "Giá trị không hợp lệ")
            return

        n = len(A)
        res = [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        self.C.set_matrix(res)

    def clear_all(self):
        self.A.clear_matrix()
        self.B.clear_matrix()
        self.C.clear_matrix()


# ================= RUN =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.resize(900, 500)
    w.show()
    sys.exit(app.exec())
