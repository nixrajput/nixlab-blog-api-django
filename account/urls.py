from django.urls import path

from account.views import (
    api_registration_view,
    api_update_account_view,
    api_login_view,
    api_change_password_view,
    api_is_account_complete_view,
    api_user_detail_view,
    api_upload_profile_picture_view,
    api_follow_toggle_view,
    api_check_if_following_view,
    verify_account,
    api_send_password_reset_otp_view,
    api_reset_password_view
)

urlpatterns = [
    path('register/', api_registration_view, name="register"),
    path('login/', api_login_view, name="login"),
    path('<str:user_id>/<str:token>/verify_account/', verify_account, name="account_verification"),
    path('is_account_complete/', api_is_account_complete_view, name="is_account_complete"),
    path('change_password/', api_change_password_view, name="change_password"),
    path('send_password_reset_otp/', api_send_password_reset_otp_view, name="send_password_reset_otp"),
    path('reset_password/', api_reset_password_view, name="reset_password"),
    path('update/', api_update_account_view, name='update'),
    path('upload_profile_picture/', api_upload_profile_picture_view, name='upload_profile_picture'),
    path('<user_id>/', api_user_detail_view, name='details'),
    path('<user_id>/follow/', api_follow_toggle_view, name='follow'),
    path('<user_id>/is_following/', api_check_if_following_view, name='is_following'),
]
