from django.contrib import admin

from .models import HarvestToken


@admin.register(HarvestToken)
class HarvestTokenAdmin(admin.ModelAdmin):
    pass
