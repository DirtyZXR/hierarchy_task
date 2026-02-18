from PyQt5.QtCore import Qt, QModelIndex, QAbstractItemModel
from PyQt5.QtGui import QColor, QPixmap

from ui.tree_node import TreeNode


class HierarchyModel(QAbstractItemModel):
    def __init__(self, roots: list[TreeNode], service, parent=None):
        super().__init__(parent)
        self._roots = roots
        self.service = service

    def columnCount(self, parent=QModelIndex()):
        return 1

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return len(self._roots)
        node: TreeNode = parent.internalPointer()
        return node.child_count()

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            node = self._roots[row]
        else:
            parent_node: TreeNode = parent.internalPointer()
            node = parent_node.child(row)

        return self.createIndex(row, column, node)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        node: TreeNode = index.internalPointer()
        p = node.parent
        if p is None:
            return QModelIndex()

        return self.createIndex(p.row(), 0, p)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        node: TreeNode = index.internalPointer()
        entity = node.data

        if role in (Qt.DisplayRole, Qt.EditRole):
            return entity.name

        if role == Qt.BackgroundRole:
            if entity.state == 0:
                return QColor("red")
            elif entity.state == 1:
                return QColor("yellow")
            elif entity.state == 2:
                return QColor("green")

        if role == Qt.DecorationRole and entity.image:
            pix = QPixmap()
            if pix.loadFromData(entity.image):
                return pix.scaled(24, 24)

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole or not index.isValid():
            return False

        node: TreeNode = index.internalPointer()
        entity = node.data

        if value.strip() == "":
            return False

        old_name = entity.name
        entity.name = value.strip()


        try:
            self.service.update_node(entity)
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            entity.name = old_name
            return False