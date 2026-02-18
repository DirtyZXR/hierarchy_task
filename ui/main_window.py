from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QPoint, QModelIndex

from services.hierarchy_service import HierarchyService
from ui.tree_model import HierarchyModel, TreeNode


class MainWindow(QMainWindow):
    def __init__(self, service: HierarchyService):
        super().__init__()
        self.service = service

        uic.loadUi("ui/main_window.ui", self)

        self.tree = self.treeView
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        roots = self.service.get_full_tree()
        self.model = HierarchyModel(roots, self.service, self)
        self.tree.setModel(self.model)
        self.tree.expandAll()

        self.setWindowTitle("Иерархия управления")

    def show_context_menu(self, position: QPoint):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return

        menu = QMenu(self)

        add_action = QAction("Добавить дочерний элемент", self)
        add_action.triggered.connect(lambda: self.add_child(index))
        menu.addAction(add_action)

        delete_action = QAction("Удалить элемент", self)
        delete_action.triggered.connect(lambda: self.delete_node(index))
        menu.addAction(delete_action)

        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def add_child(self, parent_index: QModelIndex):
        if not parent_index.isValid():
            parent_id = None
            parent_model_index = QModelIndex()
        else:
            parent_node = parent_index.internalPointer()
            parent_id = parent_node.data.id
            parent_model_index = parent_index

        new_entity = self.service.add_child(parent_id)

        new_tree_node = TreeNode(new_entity)
        if parent_id is not None:
            new_tree_node.parent = parent_index.internalPointer()

        if parent_id is None:
            row = len(self.model._roots)
            self.model.beginInsertRows(QModelIndex(), row, row)
            self.model._roots.append(new_tree_node)
            self.model.endInsertRows()
        else:
            parent_node = parent_index.internalPointer()
            row = parent_node.child_count()
            self.model.beginInsertRows(parent_model_index, row, row)
            parent_node.append_child(new_tree_node)
            self.model.endInsertRows()

        self.model.layoutChanged.emit()

        self.tree.expand(parent_model_index)
        new_index = self.model.index(row, 0, parent_model_index)
        self.tree.setCurrentIndex(new_index)
        self.tree.scrollTo(new_index)
        self.tree.edit(new_index)

    def delete_node(self, index: QModelIndex):
        if not index.isValid():
            return

        reply = QMessageBox.question(self, "Удаление", "Удалить этот элемент и его дочерние?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        node = index.internalPointer()
        entity = node.data

        parent_node = node.parent
        if parent_node is None:
            row = self.model._roots.index(node)
            self.model.beginRemoveRows(QModelIndex(), row, row)
            self.model._roots.pop(row)
            self.model.endRemoveRows()
        else:
            row = parent_node.children.index(node)
            parent_index = self.create_index_for_node(parent_node)
            self.model.beginRemoveRows(parent_index, row, row)
            parent_node.children.pop(row)
            self.model.endRemoveRows()


        self.service.delete_node(entity)

        self.model.layoutChanged.emit()

    def create_index_for_node(self, node: TreeNode) -> QModelIndex:
        if node.parent is None:
            row = self.model._roots.index(node)
            return self.model.createIndex(row, 0, node)
        else:
            return self.create_index_for_node(node.parent).child(node.row(), 0)