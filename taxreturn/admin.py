from django.contrib import admin
from .models import TaxReturn

class TaxReturnAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)

admin.site.register(TaxReturn, TaxReturnAdmin)
