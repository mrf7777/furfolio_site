
from django.views import generic

class TermsOfService(generic.TemplateView):
    template_name = "furfolio/pages/terms_of_service.html"
    
class PrivacyPolicy(generic.TemplateView):
    template_name = "furfolio/pages/privacy_policy.html"