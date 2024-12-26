from django.contrib import admin
from .models import FuelStation

class FuelStationAdmin(admin.ModelAdmin):
    list_display = [
        'opis_truckstop_id', 'name', 'address', 'city', 'state', 'rack_id', 'retail_price', 'lat', 'lon'
    ]
    
    list_editable = ['retail_price']  
    
    search_fields = ['name', 'city', 'state']
    
    
    fieldsets = (
        (None, {
            'fields': (
                'opis_truckstop_id', 'name', 'address', 'city', 'state', 'rack_id', 'retail_price', 'lat','lon'
            )
        }),
    )

admin.site.register(FuelStation, FuelStationAdmin)
