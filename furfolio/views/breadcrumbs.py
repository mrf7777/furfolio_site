from abc import ABC, abstractmethod
from typing import Type


class BreadcrumbItem:
    def __init__(self, name: str, url: str | None):
        self.name = name
        self.url = url


class IBreadcrumbParticipant(ABC):
    """
    If a view implements these methods, it provides an easy
    way to get information about itself in a tree structure.

    This is very useful if you need breadcrumb info
    for a template.
    """

    @staticmethod
    @abstractmethod
    def breadcrumb_parent() -> Type['IBreadcrumbParticipant'] | None:
        ...

    @staticmethod
    @abstractmethod
    def breadcrumb_name() -> str:
        ...

    @staticmethod
    def breadcrumb_url() -> str | None:
        return None


def breadcrumb_items(leaf: Type[IBreadcrumbParticipant], no_url_at_head: bool = True, depth: int = 0) -> list[BreadcrumbItem]:
    parent = leaf.breadcrumb_parent()
    name = leaf.breadcrumb_name()
    url = leaf.breadcrumb_url()

    if parent is not None:
        items = breadcrumb_items(parent, no_url_at_head, depth + 1)
    else:
        items = list()

    items.append(BreadcrumbItem(name, url))

    if depth == 0 and no_url_at_head:
        items[-1].url = None

    return items

