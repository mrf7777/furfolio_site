from django import forms


class SortField(forms.ChoiceField):
    CHOICE_RELEVANCE = "relevance"
    CHOICE_CREATED_DATE = "created_date"
    CHOICES = [
        (CHOICE_RELEVANCE, "Relevance"),
        (CHOICE_CREATED_DATE, "Created Date")
    ]
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = self.__class__.CHOICES
        kwargs["required"] = False
        kwargs["initial"] = self.__class__.CHOICE_RELEVANCE
        super(SortField, self).__init__(*args, **kwargs)