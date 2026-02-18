from typing import List, Optional
from db.models import Hierarchy


class TreeNode:
    def __init__(
        self,
        data: Hierarchy,
        parent: Optional["TreeNode"] = None
    ):
        self.data = data
        self.parent = parent
        self.children: List["TreeNode"] = []

    def append_child(self, child: "TreeNode"):
        self.children.append(child)

    def child(self, row: int) -> "TreeNode":
        return self.children[row]

    def child_count(self) -> int:
        return len(self.children)

    def row(self) -> int:
        if self.parent:
            return self.parent.children.index(self)
        return 0