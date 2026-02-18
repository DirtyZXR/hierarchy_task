from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db.models import Hierarchy
from ui.tree_node import TreeNode


class HierarchyService:
    def __init__(self, session: Session):
        self.session = session

    def get_full_tree(self) -> List[TreeNode]:
        stmt = (
            select(Hierarchy)
            .options(selectinload(Hierarchy.children))
        )
        all_nodes = self.session.scalars(stmt).all()

        node_map = {n.id: TreeNode(n) for n in all_nodes}
        roots: List[TreeNode] = []

        for node in all_nodes:
            tnode = node_map[node.id]
            if node.id_parent is None:
                roots.append(tnode)
            else:
                parent = node_map.get(node.id_parent)
                if parent:
                    tnode.parent = parent
                    parent.append_child(tnode)

        return roots

    def update_node(self, entity: Hierarchy):
        self.session.commit()

    def add_child(self, parent_id: Optional[int], name: str = "Новый элемент") -> Hierarchy:
        state = 1
        if parent_id is not None:
            parent = self.session.query(Hierarchy).filter(Hierarchy.id == parent_id).first()
            if parent:
                state = parent.state
                print(f"[DEBUG] Inherited state {state} from parent {parent_id}")

        new_node = Hierarchy(
            id_parent=parent_id,
            name=name,
            state=state,
            # image=None
        )
        self.session.add(new_node)
        self.session.commit()
        self.session.refresh(new_node)
        return new_node

    def delete_node(self, entity: Hierarchy):
        self.session.delete(entity)
        self.session.commit()