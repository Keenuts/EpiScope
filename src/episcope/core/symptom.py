import json
from enum import Enum
from typing import Self, Optional
from dataclasses import dataclass

class CriteriaType(Enum):
    EXCLUSIVE = 1
    MIX = 2

@dataclass
class Criteria:
    name : str
    type : CriteriaType
    values : list[str]

    @staticmethod
    def fromJSON(data : dict):
        return Criteria(data['name'], CriteriaType[data['type'].upper()], data['values'])

class Symptom:
    def __init__(self : Self, name : str, criterias : list, parent : Optional[Self] = None) -> None:
        self._parent = parent
        self._name = name
        self._criterias = criterias
        self._children : list[Self] = []

    # Add a child to this node.
    def appendChild(self : Self, item : Self) -> None:
        self._children.append(item)

    # Return this node's child at index "index".
    def child(self : Self, index : int) -> Self:
        return self._children[index]

    # Returns the number of direct children this node has (no recursion).
    def childCount(self : Self) -> int:
        return len(self._children)

    # Returns the name of this node.
    def name(self : Self) -> str:
        return self._name

    # Returns the list of criterias associated with this node.
    # If this node has no criterias defined, it inherits its parents'
    def criterias(self : Self) -> list:
        if self._criterias is None and self._parent:
            return self._parent.criterias()
        return self._criterias

    # Returns the parent of this node, None if this node is the root.
    def parent(self : Self) -> Optional[Self]:
        return self._parent

    # Returns the absolute path from the root to this node.
    # Used for auto-completion.
    def path(self : Self) -> str:
        if self._parent is None:
            return ""
        parentPath = self._parent.path()
        if len(parentPath) == 0:
            return self._name
        return "{}/{}".format(self._parent.path(), self._name)

    # Returns the child node matching the given path if any.
    # None otherwise.
    # This function assumes there is a unique path for each node.
    def fromPath(self : Self, path : str) -> Optional[Self]:
        if len(path) == 0:
            return self

        parts = path.split("/")
        for child in self._children:
            if child.name().lower() != parts[0].lower():
                continue
            return child.fromPath("/".join(parts[1:]))
        return None

    # Used for Qt models: the row is the index of this node in the parents'
    # children.
    def row(self : Self) -> int:
        if self._parent:
            return self._parent._children.index(self)
        return 0

    # Loads a symptom hierarchy from a JSON dictionnary.
    @staticmethod
    def loadHierarchy(data : dict, parent = None):
        if 'criterias' not in data:
            criterias = [] if parent is None else parent.criterias()
        else:
            criterias = data['criterias']

        node = Symptom(data['name'], criterias, parent)
        if 'children' not in data:
            return node

        for item in data['children']:
            node.appendChild(Symptom.loadHierarchy(item, node))
        return node
