from . import utils


class GetFullUrlMixin:
    def get_full_url(self):
        url = self.get_absolute_url()
        full_url = utils.add_domain_and_scheme_to_url(url)
        return full_url
