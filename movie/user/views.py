from django.views.generic import ListView
from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.urls import reverse
from .models import UserProfile, CustomUser,Show,Seat,Booking
from .forms import SignUpForm, LogInForm, UpdateUserForm, UpdateProfileForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date
from django.urls import reverse
from django.views.generic import DetailView

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
                return redirect('shows')
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
        
        user=request.user.email
        get_customuserdetails=CustomUser.objects.get(email=user)
        
        get_userprofiledetails=UserProfile.objects.get(user=get_customuserdetails)
    return render(request, 'user/profile.html', {'get_userprofiledetails':get_userprofiledetails,'request.user':request.user})
    
def editprofile(request):
    if request.method == 'POST':
        
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            
          user_form.save()
          return redirect(reverse('user:profile'))        

        
    else:
        user_form = UpdateUserForm(instance=request.user)
    return render(request, 'user/editprofile.html', {'user_form': user_form})



class PostListView(ListView):
    model = Show
    template_name = 'home.html'
    context_object_name = 'show'   
    ordering = ['time']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show'] = context['show'][:3]
        return context

class PostDetailView(DetailView):
    model = Show
    template_name = 'blog/detail.html'
    slug_url_kwarg = "choice"
    slug_field = "choice"
    context_object_name = 'show'   
    def get_object(self, queryset=None):
        return Show.objects.filter(choice=self.kwargs.get("choice"))

@login_required
def book_show(request, show_id):
    show = Show.objects.get(id=show_id)
    seats = Seat.objects.filter(show=show)
    #booked_seats = Booking.objects.filter(show=show).values_list('seat__seat_no', flat=True)
    booked_seats = seats.filter( is_available=False)
    available_seats = [seat for seat in seats if seat.seat_no not in booked_seats]
    for i in available_seats:
        print(i)
    max_row=5
    max_col=6
    # Create a seat matrix
    seat_matrix = []
    for i in range(1, max_row + 1):
        row = []
        for j in range(1, max_col + 1):
            seat_no = (i-1)*max_col + j
            seat = seats.filter(seat_no=seat_no).first()
            print(seat)
            if seat==None:
                row.append({'seat_no': seat_no, 'is_available': seat_no not in booked_seats})
            else:
                row.append(None)
        seat_matrix.append(row)

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        
        if len(selected_seats) > len(available_seats):
            return render(request, 'user/error.html', {'error': 'You cannot book more seats than available.'})
        booking = Booking.objects.create(user=request.user, show=show)
        for seat_no in selected_seats:
            seat = Seat.objects.get(show=show, seat_no=seat_no)
            seat.is_available = False
            seat.save()
            booking.seat.add(seat)
        booking.save()
        return redirect('user:shows')
    
    return render(request, 'user/book_show.html', {'show': show, 'seat_matrix': seat_matrix})


def shows(request):
    now = timezone.now()
    upcoming_shows = Show.objects.filter(time__gte=now)
    
        
    
    return render(request, 'user/shows.html', {'shows': upcoming_shows})