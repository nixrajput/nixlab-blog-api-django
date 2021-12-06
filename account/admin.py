from django.contrib import admin

from account.models import Account, ProfilePicture, OTP


class ProfilePictureInline(admin.TabularInline):
    model = ProfilePicture
    extra = 1
    max_num = 1


class ProfilePictureAdmin(admin.ModelAdmin):
    readonly_fields = ["uploaded_at"]
    list_filter = ('user', 'uploaded_at')
    list_display = ["id", "user", "uploaded_at"]
    ordering = ("-uploaded_at",)


class AccountAdmin(admin.ModelAdmin):
    model = Account
    readonly_fields = ["date_joined", "last_updated"]
    list_display = ["id", "username", "is_admin", "is_valid"]
    search_fields = ["email", "username"]

    inlines = [ProfilePictureInline]


class OTPAdmin(admin.ModelAdmin):
    model = OTP
    readonly_fields = ["added_at", "expires_at"]
    list_display = ["user", "otp", "added_at"]
    search_fields = ["user", "otp"]


admin.site.register(Account, AccountAdmin)
admin.site.register(ProfilePicture, ProfilePictureAdmin)
admin.site.register(OTP, OTPAdmin)
