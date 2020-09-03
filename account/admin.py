from django.contrib import admin
from django.contrib.admin import site

from account.models import Account


class AccountAdmin(admin.ModelAdmin):
    model = Account
    list_display = ["email", "username", "is_admin", "is_superuser"]
    search_fields = ["email", "username"]


site.register(Account, AccountAdmin)
