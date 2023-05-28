from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser,Movie,Seat,Booking

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Movie)
admin.site.register(Seat)
admin.site.register(Booking)