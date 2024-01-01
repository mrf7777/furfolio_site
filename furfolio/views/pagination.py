
from typing import Any, List
from django.core.paginator import Page

PAGE_SIZE = 10

class PageRangeContextMixin:
    page_range_context_object_name = "page_range"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context[self.page_range_context_object_name] = self.__class__.get_page_range_items(
            context["page_obj"])
        return context

    def get_page_range_items(page: Page) -> List[str]:
        """
        Given the page object, which you should get from the context, this
        will return a list of page items, including ellipsis, that you
        can then display in a template.
        """
        return list(page.paginator.get_elided_page_range(page.number))
