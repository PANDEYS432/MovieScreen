from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from .views import login,logout,signup,profile,editprofile,book_show,shows, add_show
urlpatterns = [
    path('profile/', profile, name='profile'),
    path('admin/', admin.site.urls),
    path('book_show/<int:show_id>/', book_show, name='book_show'),
    path('shows/', shows, name='shows'),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),
     path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('add_show/', add_show, name='add_show'),
    path('editprofile/', editprofile, name='editprofile'),
    
]