from django.contrib import admin

from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'agreement_accepted', 'avatar']


admin.site.register(Profile, ProfileAdmin)
