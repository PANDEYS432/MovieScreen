from django.db import models
from django.core.validators import MaxValueValidator
from unittest.util import _MAX_LENGTH
from django.contrib.auth.models import AbstractUser
from PIL import Image 
from django.core.exceptions import ValidationError


from django.contrib.auth.base_user import BaseUserManager
from datetime import date
class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )
    

        return self._create_user(email, password, **extra_fields)
class CustomUser(AbstractUser):
    
    email = models.EmailField(verbose_name="Email", null=False, default='', unique=True, max_length=100)
    username = models.CharField(max_length=20)
    USERNAME_FIELD = "email" # make the user log in with the email
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()
    

class UserProfile(models.Model):

    user = models.OneToOneField(CustomUser,null =True, on_delete=models.CASCADE)
    image=models.ImageField(default='default.jpg',upload_to='profile_pics')  #images will get saved in directory called profile_pics
    phone_no= models.CharField(default='0000',max_length=50)
    def __str__(self):
        return self.user.username
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
    

class Movies(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    poster = models.ImageField(upload_to='movie_posters/')
    available = models.BooleanField(default=True)

    def str(self):
        return self.title


class Show(models.Model):
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    time = models.DateTimeField()
    uuid = models.CharField(max_length=32, unique=True)
    

    def str(self):
     return f"{self.movie.title} ({self.time.strftime('%Y-%m-%d %H:%M')})"

    
class Seat(models.Model):
    seat_no=models.IntegerField()
    show=models.ForeignKey(Show, on_delete=models.CASCADE)
    is_available=models.BooleanField(default=True)
    def str(self):
        return self.seat_no

class Booking(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    seat=models.ManyToManyField(Seat)
    show=models.ForeignKey(Show,on_delete=models.CASCADE)
    def str(self):
        return self.user.username, "has booked" ,self.seat_no
    def save(self, *args, **kwargs):
        bookings_this_month = Booking.objects.filter(user=self.user, show__time__month=self.show.time.month)
        if len(bookings_this_month) >= 2:
            raise ValidationError("You can only book 2 tickets per month.")
        super().save(*args, **kwargs)
