from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser,Movie,Booking,Show,Seat

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Movie)
admin.site.register(Seat)
admin.site.register(Show)
#admin.site.register(SeatMatrix)
admin.site.register(Booking)