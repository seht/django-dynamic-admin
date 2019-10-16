from django.contrib import admin

from .models import *


class TaxonomyDictionaryAdmin(admin.ModelAdmin):

    class TaxonomyTermInline(admin.TabularInline):
        show_change_link = True
        extra = 0
        model = TaxonomyTerm

    inlines = [
        TaxonomyTermInline,
    ]
