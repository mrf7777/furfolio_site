from . import utils


class GetFullUrlMixin:
    def get_full_url(self):
        url = self.get_absolute_url()
        full_url = utils.add_domain_and_scheme_to_url(url)
        return full_url


class GetAdultConsentMixin:
    def does_user_consent_to_adult_content(self) -> bool:
        consent_to_adult_content = getattr(
            self.request.user, "consent_to_adult_content", False
        )
        return consent_to_adult_content
