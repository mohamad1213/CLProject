from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, LoginForm
from .models import User,Profile
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import Group
import sweetify
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                sweetify.success(request, f'Selamat Datang {user.username}!', text='Kamu telah berhasil Masuk.', persistent='Tutup')
                return redirect('classroom:dashboard')  # Replace 'home' with your home view name
            else:
                sweetify.error(request, 'username atau sandi salah', persistent='Tutup')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = request.POST.get('role')
            if role == 'siswa':
                group = Group.objects.get(name='siswa')
            elif role == 'guru':
                group = Group.objects.get(name='guru')
            else:
                group = None  # Atau sesuaikan dengan logika bisnis Anda
            user.groups.add(group)
            gender = form.cleaned_data.get('gender')
            Profile.objects.create(user=user, gender=gender)
            sweetify.success(request, f'akun {user.username} berhasil dibuat')
            return redirect('users:login')
        else:
            sweetify.error(request, f'Kesalaham Pengaturan akun')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form':form})


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(data=request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(data=request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save(commit=False)
            profile = request.user.profile
            if 'image' in request.FILES:
                profile.image = request.FILES['image']
            profile.save()
            sweetify.success(request, f"Profil telah diperbarui !")
            return redirect('users:profile')
        else:
            sweetify.error(request, f'Profil tidak dapat diperbarui :(')

            sweetify.error(request, profile_form.errors)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/profile.html', context)

def logoutUser(request):
    logout(request)
    sweetify.success(request, 'Kamu Berhasil Keluar !', persistent='Tutup')
    return redirect('users:login')


