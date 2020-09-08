from django.urls import path

from account.views import (
    registration_view,
    update_account_view,
    ObtainAuthTokenView,
    ChangePasswordView,
    account_properties_view,
    does_account_exist_view,
    detail_user_view,
)

app_name = "account"

urlpatterns = [
    path('register/', registration_view, name="register"),
    path('login/', ObtainAuthTokenView.as_view(), name="login"),
    path('check_if_account_exists/', does_account_exist_view, name="check_if_account_exists"),
    path('change_password/', ChangePasswordView.as_view(), name="change_password"),
    path('properties/', account_properties_view, name="properties"),
    path('properties/update/', update_account_view, name='update'),
    path('details/<user_id>/', detail_user_view, name='details'),
]
