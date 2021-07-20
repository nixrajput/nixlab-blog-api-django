from django.urls import path

from account.views import (
    registration_view,
    update_account_view,
    ObtainAuthTokenView,
    ChangePasswordView,
    account_properties_view,
    does_account_exist_view,
    detail_user_view,
    upload_profile_picture,
    api_follow_toggle_view,
    api_check_if_following_view,
    verify_account
)

urlpatterns = [
    path('register/', registration_view, name="register"),
    path('login/', ObtainAuthTokenView.as_view(), name="login"),
    path('verify_account/<str:user_id>/<str:token>/', verify_account, name="account_verification"),
    path('check_if_account_exists/<user_id>/', does_account_exist_view, name="check_if_account_exists"),
    path('change_password/', ChangePasswordView.as_view(), name="change_password"),
    path('properties/', account_properties_view, name="properties"),
    path('update/', update_account_view, name='update'),
    path('details/<user_id>/', detail_user_view, name='details'),
    path('follow/<user_id>/', api_follow_toggle_view, name='follow'),
    path('is_following/<user_id>/', api_check_if_following_view, name='is_following'),
    path('upload_profile_picture/', upload_profile_picture, name='upload_profile_picture'),
]
