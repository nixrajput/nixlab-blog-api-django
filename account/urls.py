from django.urls import path

from account.views import (
    registration_view,
    update_account_view,
    ObtainAuthTokenView,
    ChangePasswordView,
    account_properties_view,
    is_account_complete_view,
    detail_user_view,
    upload_profile_picture_view,
    api_follow_toggle_view,
    api_check_if_following_view,
    verify_account
)

urlpatterns = [
    path('register/', registration_view, name="register"),
    path('login/', ObtainAuthTokenView.as_view(), name="login"),
    path('<str:user_id>/<str:token>/verify_account/', verify_account, name="account_verification"),
    path('is_account_complete/', is_account_complete_view, name="is_account_complete"),
    path('change_password/', ChangePasswordView.as_view(), name="change_password"),
    path('properties/', account_properties_view, name="properties"),
    path('update/', update_account_view, name='update'),
    path('upload_profile_picture/', upload_profile_picture_view, name='upload_profile_picture'),
    path('<user_id>/', detail_user_view, name='details'),
    path('<user_id>/follow/', api_follow_toggle_view, name='follow'),
    path('<user_id>/is_following/', api_check_if_following_view, name='is_following'),
]
