from django.contrib import admin

from .models import HarvestToken, HarvestSubmission


@admin.register(HarvestToken)
class HarvestTokenAdmin(admin.ModelAdmin):
    pass


@admin.register(HarvestSubmission)
class HarvestSubmissionAdmin(admin.ModelAdmin):
    pass
