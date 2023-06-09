from django.shortcuts import render, redirect
from .models import Room, Topic, Message
from .forms import RoomForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from .forms import CreateUserForm
# Create your views here.

class loginPage(View):
    def get(self, request):
        page = "login"
        if request.user.is_authenticated:
            return redirect('home')
        context = {
            'page': page
        }
        return render(request, 'base/login_register.html', context)
    
    def post(self, request):
        page = 'login'
        if request.user.is_authenticated:
            return redirect('home')
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist.')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist.')
        context = {
            'page': page
        }
        return render(request, 'base/login_register.html', context)



class registerPage(View):
    def get(self, request):
        form = CreateUserForm()
        context = {
            'form': form
        }
        return render(request, 'base/created_user.html', context)
    
    def post(self, request):
        form = CreateUserForm(self.request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration?')
        context = {
            'form': form
        }
        return render(request, 'base/created_user.html', context)


class logoutPage(View):
    def get(self, request):
        logout(request)
        return redirect('home')


class home(View):
    def get(self, request):
        q = request.GET.get('q') if request.GET.get('q') != None else ''
        rooms = Room.objects.filter(
            Q(topic__name__contains=q) |
            Q(name__icontains=q) |
            Q(descriptions__icontains=q))

        topics = Topic.objects.all()
        room_count = rooms.count()
        room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
        context = {
            'rooms': rooms,
            'topics': topics,
            'room_count': room_count,
            'room_messages': room_messages,
        }
        return render(request, 'base/home.html', context)


class room(View):
    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        room_messages = room.message_set.all()
        participants = room.participants.all()

        context = {
            'room': room,
            'room_messages': room_messages,
            'participants': participants
        }
        return render(request, 'base/room.html', context)
    
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        room_messages = room.message_set.all()
        participants = room.participants.all()
        
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        context = {
            'room': room,
            'room_messages': room_messages,
            'participants': participants
        }

        return render(request, 'base/room.html', context)


@method_decorator(login_required(login_url='login'), name='dispatch')
class createRoom(View):
    def get(self, request):
        form = RoomForm()
        context = {
            "form": form
        }
        return render(request, 'base/room_form.html', context)

    def post(self, request):
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect("home")
        context = {"form": form}
        return render(request, 'base/room_form.html', context)



@method_decorator(login_required(login_url='login'), name='dispatch')
class updateRoom(View):
    def get(self, request, pk):
        listing = Room.objects.get(id=pk)
        form = RoomForm(instance=listing)
        context = {
            "form": form
        }
        return render(request, 'base/room_form.html', context)
    
    def post(self, request, pk):
        listing = Room.objects.get(id=pk)
        form = RoomForm(request.POST ,instance=listing)
        if form.is_valid():
            form.save()
            return redirect("home")
        context = {
            "form": form
        }
        return render(request, 'base/room_form.html', context)


@method_decorator(login_required(login_url='login'), name='dispatch')
class deleteRoom(View):
    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        return render(request, 'base/delete.html', {'obj':room})
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        if request.method == 'POST':
            room.delete()
            return redirect('home')
        return render(request, 'base/delete.html', {'obj':room})


@method_decorator(login_required(login_url='login'), name='dispatch')
class deleteMessage(View):
    def get(self, request, pk):
        message = Message.objects.get(id=pk)
        return render(request, 'base/delete.html', {'obj':message})
    def post(self, request, pk):
        message = Message.objects.get(id=pk)
        if request.method == 'POST':
            message.delete()
            return redirect('home')
        return render(request, 'base/delete.html', {'obj':message})
    


class userProfile(View):
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        rooms = user.room_set.all()
        topics = Topic.objects.all()
        room_messages = user.message_set.all()

        context = {
            'user': user,
            'rooms': rooms,
            'topics': topics,
            'room_messages': room_messages
        }
        return render(request, 'base/profile.html', context)
    