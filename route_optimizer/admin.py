from django.contrib import admin
from .models import FuelStation

class FuelStationAdmin(admin.ModelAdmin):
    list_display = [
        'opis_truckstop_id', 'name', 'address', 'city', 'state', 
        'latitude', 'longitude', 'rack_id', 'retail_price'
    ]
    
    list_editable = ['retail_price']  
    
    search_fields = ['name', 'city', 'state']
    
    list_filter = ['state', 'city']
    
    fieldsets = (
        (None, {
            'fields': (
                'opis_truckstop_id', 'name', 'address', 'city', 'state', 
                'latitude', 'longitude', 'rack_id', 'retail_price'
            )
        }),
    )

admin.site.register(FuelStation, FuelStationAdmin)
