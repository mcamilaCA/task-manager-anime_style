"""Entry point for Apothecary's Almanac — a Ghibli x Apothecary Diaries
styled task & time tracker."""

import sys

from PySide6.QtWidgets import QApplication

from app import db
from app.theme import build_stylesheet, load_bundled_fonts
from app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    load_bundled_fonts()
    app.setStyleSheet(build_stylesheet())

    conn = db.connect()
    db.init_db(conn)

    window = MainWindow(conn)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
