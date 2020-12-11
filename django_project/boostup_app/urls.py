from django.conf.urls import url
from boostup_app import views


urlpatterns = [
    url(r'^oauth/authorize', views.oauth_authorize),
    url(r'^oauth/redirect', views.oauth_redirect),
]
