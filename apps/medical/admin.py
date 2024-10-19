from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from config.settings import IP_ADDR, PORT

from apps.medical.models import Doctor

class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id_doctor', 'first_name', 'last_name', 'email','sexe', 'adress', 'contact', 'credit_vert', 'domaine', 'profession', 'organisation', 'location', 'speciality','last_login', 'profile_image']
    list_per_page = 5
    search_fields = ('first_name', 'last_name', 'adress', 'contact', 'domaine', 'email')
    list_filter = ['speciality']
    actions = ['modifier_utilisateurs']

    def save_model(self, request, obj, form, change):
        obj.password = make_password(obj.password)
        obj.nom = obj.nom.capitalize()
        return super().save_model(request, obj, form, change)
    
    def last_login(self, obj):
        return obj.user.last_login
    
    def profession(self, obj):
        return obj.user.profession
    
    def organisation(self, obj):
        return obj.user.organisation
    
    def credit_vert(self, obj):
        return obj.user.credit_vert
    
    def first_name(self, obj):
        return obj.user.first_name
    
    def last_name(self, obj):
        return obj.user.las_name
    
    def adress(self, obj):
        return obj.user.adress
    
    def contact(self, obj):
        return obj.user.contact
    
    def domaine(self, obj):
        return obj.user.domaine
    
    def sexe(self, obj):
        return obj.user.sexe
    
    def email(self, obj):
        return obj.user.email
    
    
    
    def speciality(self, obj):
        return str(obj.speciality)

    def location(self, obj):
        return str(obj.location)

    def modifier_utilisateurs(self, request, queryset):
        if queryset.count() == 1:
            utilisateur = queryset.first()
            url = reverse('admin:medical_doctor_change', args=[utilisateur.id])
            return HttpResponseRedirect(url)
        else:
            self.message_user(request, "Sélectionnez exactement un utilisateur.", level='ERROR')

    def profile_image(self, obj):
        if obj.profile:
            return format_html('<img src="http://{}:{}/api{}" style="width:30px;height:30px;border-radius:50%;" />', IP_ADDR, PORT, obj.profile.url)
        return 'No Image'

    readonly_fields = ('profile_image_preview',)

    def profile_image_preview(self, obj):
        if obj.profile:
            return format_html('<img src="http://{}:{8000}/api{}" style="width:30px;height:30px;border-radius:50%;" />', IP_ADDR, PORT, obj.profile.url)
        return 'No Image'

    profile_image.allow_tags = True
    profile_image.short_description = 'Profile Image'

admin.site.register(Doctor,DoctorAdmin)