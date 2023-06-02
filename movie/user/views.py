from django.views.generic import ListView
from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.urls import reverse
from .models import UserProfile, CustomUser,Show,Seat,Booking,Movies
from .forms import SignUpForm, LogInForm, UpdateUserForm, UpdateProfileForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date
from django.urls import reverse
from django.views.generic import DetailView
from django.core.exceptions import ValidationError
from .decoraters import admin_only
from tmdbv3api import Movie
from tmdbv3api import TMDb

import uuid
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            django_login(request, user)
            return redirect('shows')
    else:
        form = SignUpForm()   

    return render(request, 'user/signup.html', {'form': form})


def login(request):
    error = False
    if request.user.is_authenticated:
        return redirect('user:shows')
    if request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(email=email, password=password)
            if user:
                django_login(request, user)  
                return redirect('user:shows')
            else:
                error = True
    else:
        form = LogInForm()

    return render(request, 'user/login.html', {'form': form, 'error': error})


def logout(request):
    django_logout(request)
    return redirect(reverse('user:login'))
    

@login_required
def profile(request):
    if request.user.is_authenticated:
        
        user=request.user
        get_customuserdetails=CustomUser.objects.get(email=user)
        booked_shows = Booking.objects.filter(user=user)
        get_userprofiledetails=UserProfile.objects.get(user=get_customuserdetails)
        now = timezone.now()
        upcoming_shows = Show.objects.filter(time__gte=now)
    
    return render(request, 'user/profile.html', {'get_userprofiledetails':get_userprofiledetails,'request.user':request.user,'booked_shows':booked_shows,'shows': upcoming_shows})
    
def editprofile(request):
    if request.method == 'POST':
        
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            
          user_form.save()
          return redirect(reverse('user:profile'))        

        
    else:
        user_form = UpdateUserForm(instance=request.user)
    return render(request, 'user/editprofile.html', {'user_form': user_form})

@login_required
def book_show(request, show_id):
    show = Show.objects.get(id=show_id)
    seats = Seat.objects.filter(show=show)
    #booked_seats = Booking.objects.filter(show=show).values_list('seat__seat_no', flat=True)
    booked_seats = seats.filter( is_available=False).values_list('seat_no', flat=True)
    all_seats=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
    available_seats = [seat for seat in all_seats if seat not in booked_seats]
    max_row=5
    max_col=6
    # Create a seat matrix
    seat_matrix = []
    for i in range(1, max_row + 1):
        row = []
        for j in range(1, max_col + 1):
            seat_no = (i-1)*max_col + j
            seat = seats.filter(seat_no=seat_no).first()
            
            if seat==None:
                row.append({'seat_no': seat_no, 'is_available': seat_no not in booked_seats})
            else:
                row.append(None)
        seat_matrix.append(row)

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        
        if len(selected_seats) > len(available_seats):
            return render(request, 'user/error.html', {'error': 'You cannot book more seats than available.'})
        try:
            booking = Booking.objects.create(user=request.user, show=show)
            for seat_no in selected_seats:
                seat = Seat(show=show, seat_no=seat_no,is_available=False)
                seat.save()
                booking.seat.add(seat)
            booking.save()
            return redirect('user:shows')
        except ValidationError as e:
            error_message = str(e)  # Retrieve the error message
        return render(request, 'user/error.html', {'error': error_message})
        
    
    return render(request, 'user/book_show.html', {'show': show, 'seat_matrix': list(seat_matrix)})


def shows(request):
    now = timezone.now()
    upcoming_shows = Show.objects.filter(time__gte=now)
    
        
    
    return render(request, 'user/shows.html', {'shows': upcoming_shows})

@admin_only
def add_show(request):
    tmdb = TMDb()
    tmdb.api_key = '3eee8fa0635034fad69d09fc80da7e97'
    movie1 = Movie()
    if request.method == 'POST':
        movie_title = request.POST['movie_title']
        movie = Movies.objects.filter(title=movie_title).first()
        search_results={}
        if movie_title=='Other':
            other_title = request.POST['other_title']
            search = movie1.search(other_title)
            search_results=search
            print(search[0].original_title)
            #movie = Movies.objects.create(title=search.title,poster=search.poster_path,description=search.overview)
        show_time = request.POST['show_time']
        uuid1=uuid.uuid1()
        movies = Movies.objects.all()
        #show = Show.objects.create(movie=movie, time=show_time,uuid=uuid1)
        return render(request, 'user/add_show.html', {'movies': movies,'search_results': search_results})
    else:
        movies = Movies.objects.all()
        search_results={}
        return render(request, 'user/add_show.html', {'movies': movies,'search_results': search_results})