"""
Admin panel dla Location Analysis.
"""
from django.contrib import admin
from .models import LocationAnalysis


@admin.register(LocationAnalysis)
class LocationAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'address', 'price', 'neighborhood_score', 'created_at']
    list_filter = ['has_precise_location', 'source_provider', 'created_at']
    search_fields = ['title', 'address', 'url']
    readonly_fields = ['url_hash', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Identyfikacja', {
            'fields': ('url', 'url_hash', 'source_provider')
        }),
        ('Dane nieruchomości', {
            'fields': ('title', 'address', 'price', 'price_per_sqm', 'area_sqm', 'rooms', 'floor')
        }),
        ('Lokalizacja', {
            'fields': ('latitude', 'longitude', 'has_precise_location', 'analysis_radius')
        }),
        ('Wyniki analizy', {
            'fields': ('neighborhood_score', 'pros', 'cons')
        }),
        ('Meta', {
            'fields': ('created_at',)
        }),
    )
