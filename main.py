import sys
from PyQt5.QtWidgets import QApplication

from db.session import SessionLocal
from services.hierarchy_service import HierarchyService
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    session = SessionLocal()
    try:
        service = HierarchyService(session)
        window = MainWindow(service)
        window.show()
        sys.exit(app.exec_())
    finally:
        session.close()


if __name__ == "__main__":
    main()