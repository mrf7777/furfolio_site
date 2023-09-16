
from django.views import generic

class TermsOfService(generic.TemplateView):
    template_name = "furfolio/terms_of_service.html"
    
class PrivacyPolicy(generic.TemplateView):
    template_name = "furfolio/privacy_policy.html"