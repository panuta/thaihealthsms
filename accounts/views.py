# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import simplejson

from accounts.forms import *
from accounts.models import *

from helper.shortcuts import render_response

# NOTE: Use this method to create UserAccount object after django.auth.User object is created
def user_post_save_callback(sender, instance, created, *args, **kwargs):
    if created: UserAccount.objects.create(user=instance)

from django.contrib.auth.views import login
from django.contrib.auth import REDIRECT_FIELD_NAME

# NOTE: Determine if the user has logged in for the first time
def hooked_login(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME):
    response = login(request, template_name, redirect_field_name)

    if request.user.is_authenticated():
        if not request.user.is_superuser and request.user.get_profile().random_password:
            return redirect('/accounts/first_time/')
        
    return response

@login_required
def view_first_time_login(request):
    if request.user.is_authenticated():
        if request.user.is_superuser or (not request.user.is_superuser and not request.user.get_profile().random_password):
            return redirect('/')
        
    if request.method == 'POST':
        form = ChangeFirstTimePasswordForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 =form.cleaned_data['password2']

            user = request.user
            user.set_password(password1)
            user.save()

            user_account = user.get_profile()
            user_account.random_password = ''
            user_account.save()

            next = request.POST.get('next')
            if not next: next = '/'
            return redirect(next)

    else:
        form = ChangeFirstTimePasswordForm()

    next = request.GET.get('next', '')
    return render_response(request, "registration/first_time_login.html", {'form':form, 'next':next})

@login_required
def view_user_settings(request):
    if request.method == 'POST':
        if 'profile_button' in request.POST and request.POST.get('profile_button'):
            form_profile = ChangeUserProfileForm(request.POST)
            if form_profile.is_valid():
                firstname = form_profile.cleaned_data['firstname']
                lastname =form_profile.cleaned_data['lastname']
                
                user_account = request.user.get_profile()
                user_account.firstname = firstname
                user_account.lastname = lastname
                user_account.save()
                
                messages.success(request, 'แก้ไขข้อมูลผู้ใช้เรียบร้อย')
                return redirect('view_user_settings')
        
        if 'password_button' in request.POST and request.POST.get('password_button'):
            form_password = ChangeUserPasswordForm(request.POST)
            if form_password.is_valid():
                password1 = form_password.cleaned_data['password1']
                password2 =form_password.cleaned_data['password2']
                
                user = request.user
                user.set_password(password1)
                user.save()
                
                messages.success(request, 'เปลี่ยนรหัสผ่านเรียบร้อย')
                return redirect('view_user_settings')
    
    else:
        form_profile = ChangeUserProfileForm(initial={'firstname':request.user.get_profile().firstname, 'lastname':request.user.get_profile().lastname})
        form_password = ChangeUserPasswordForm()
    
    return render_response(request, "page_user/user_settings.html", {'form_profile':form_profile, 'form_password':form_password,})