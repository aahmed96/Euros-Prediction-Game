from django.contrib import admin

# Register your models here.
from django.apps import apps
from django.contrib import admin
# Register your models here.
import django.contrib.auth.admin
import django.contrib.auth.models
from django.contrib import auth

from .models import *

admin.site.site_header = 'Rigged- Administration'


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(ListAdminMixin, self).__init__(model, admin_site)


models = apps.get_models()
for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass