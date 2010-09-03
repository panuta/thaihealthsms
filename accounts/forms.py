# -*- encoding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList

class ChangeFirstTimePasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='รหัสผ่าน')
    password2 = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='ยืนยันรหัสผ่าน')
    
    def clean(self):
        cleaned_data = self.cleaned_data
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 != password2:
            self._errors["password2"] = ErrorList(['รหัสผ่านไม่สัมพันธ์กัน'])
            del cleaned_data["password2"]

        return cleaned_data

class ChangeUserProfileForm(forms.Form):
    firstname = forms.CharField(max_length=300, label='ชื่อ')
    lastname = forms.CharField(max_length=300, label='นามสกุล')

class ChangeUserPasswordForm(forms.Form):
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(), label='รหัสผ่าน')
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput(), label='ยืนยันรหัสผ่าน')
    
    def clean(self):
        cleaned_data = self.cleaned_data
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 != password2:
            self._errors['password2'] = ErrorList(['รหัสผ่านไม่ตรงกัน'])
            del cleaned_data['password1']
            del cleaned_data['password2']
        
        return cleaned_data
