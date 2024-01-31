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


class SavingMixin:
    def save(self, *args, **kwargs) -> None:
        # https://docs.djangoproject.com/en/5.0/ref/models/instances/#django.db.models.Model._state
        if self._state.adding:
            self.pre_save_new_object()
            super().save(*args, **kwargs)
            self.post_save_new_object()
        else:
            self.pre_save_existing_object()
            super().save(*args, **kwargs)
            self.post_save_existing_object()

    def pre_save_new_object(self):
        pass

    def post_save_new_object(self):
        pass

    def pre_save_existing_object(self):
        pass

    def post_save_existing_object(self):
        pass


class CleaningMixin:
    def clean(self):
        if self._state.adding:
            self.pre_clean_new_object()
            super().clean()
            self.post_clean_new_object()
        else:
            self.pre_clean_existing_object()
            super().clean()
            self.post_clean_existing_object()

    def pre_clean_new_object(self):
        pass

    def post_clean_new_object(self):
        pass

    def pre_clean_existing_object(self):
        pass

    def post_clean_existing_object(self):
        pass
