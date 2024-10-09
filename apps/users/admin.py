from django.contrib import admin
from apps.users.models import AccountMode

from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from config.settings import IP_ADDR

class AccountModeAdmin(admin.ModelAdmin):
    list_display = ['id_account_mode', 'name', 'price','free_trial_days', 'validity_days']
    list_per_page = 5
    search_fields = ('name',)
    list_filter = ['validity_days']
    actions = ['modifier_account_mode']

    def modifier_account_mode(self, request, queryset):
        if queryset.count() == 1:
            account_mode = queryset.first()
            url = reverse('admin:users_accountmode_change', args=[account_mode.id_account_mode])
            return HttpResponseRedirect(url)
        else:
            self.message_user(request, "Sélectionnez exactement un utilisateur.", level='ERROR')

admin.site.register(AccountMode,AccountModeAdmin)
