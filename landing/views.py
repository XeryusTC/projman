from braces.views import AnonymousRequiredMixin
from django.views.generic import TemplateView

class LandingView(AnonymousRequiredMixin, TemplateView):
    template_name = 'landing/index.html'
