from django.urls import path

from account.views import (
    registration_view,
    update_account_view,
    ObtainAuthTokenView
)

app_name = "account"

urlpatterns = [
    path('register/', registration_view, name="register"),
    path('login/', ObtainAuthTokenView.as_view(), name="login"),
    path('update', update_account_view, name='update'),
]
