from django.contrib import admin
from django.contrib.admin import site

from account.models import Account, ProfilePicture


class ProfilePictureInline(admin.TabularInline):
    model = ProfilePicture
    extra = 1
    max_num = 1


class ProfilePictureAdmin(admin.ModelAdmin):
    list_filter = ('user', 'uploaded_at')
    ordering = ("-uploaded_at",)


class AccountAdmin(admin.ModelAdmin):
    model = Account
    list_display = ["email", "username", "is_admin", "is_superuser"]
    search_fields = ["email", "username"]

    inlines = [ProfilePictureInline, ]


site.register(Account, AccountAdmin)
admin.site.register(ProfilePicture, ProfilePictureAdmin)
