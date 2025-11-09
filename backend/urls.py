from django.urls import path
from views import ShortenURLView, RedirectView

urlpatterns = [
    path('api/shorten/', ShortenURLView.as_view(), name='shorten_url'),

    path('<str:short_code>', RedirectView.as_view(), name='redirect'),
]