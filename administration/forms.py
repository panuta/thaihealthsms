# -*- encoding: utf-8 -*-
import datetime

from django import forms
from django.contrib.auth.models import User
from django.forms.util import ErrorList

from domain.forms import SectorChoiceField, SectorCheckboxChoiceField

from accounts.models import RoleDetails
from domain.models import Sector, MasterPlan, SectorMasterPlan

roles = [(role_details.role.name, role_details.name) for role_details in RoleDetails.objects.all()]
roles.insert(0, ('',''))

class UserAccountForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    username = forms.CharField(max_length=500, label='ชื่อผู้ใช้')
    email = forms.EmailField(label='อีเมล')
    firstname = forms.CharField(max_length=500, label='ชื่อจริง')
    lastname = forms.CharField(max_length=500, label='นามสกุล')
    role = forms.CharField(widget=forms.Select(choices=roles), label='ตำแหน่ง')
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        user_id = cleaned_data.get('user_id')
        username=cleaned_data.get('username')
        
        if user_id: existing = User.objects.filter(username=username).exclude(id=user_id).count()
        else: existing = User.objects.filter(username=username).count()
        
        if existing:
            self._errors['username'] = ErrorList(['ชื่อผู้ใช้ซ้ำกับผู้ใช้คนอื่นในระบบ'])
            del cleaned_data['username']
        
        return cleaned_data
        
class UserChangePasswordForm(forms.Form):
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

class ModifySectorForm(forms.Form):
    sector_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    ref_no = forms.IntegerField(label='เลขสำนัก')
    name = forms.CharField(max_length=512, label='ชื่อสำนัก')
    
    def clean(self):
        cleaned_data = self.cleaned_data
        sector_id = cleaned_data.get('sector_id')
        ref_no = cleaned_data.get('ref_no')
        
        if sector_id: existing = Sector.objects.filter(ref_no=ref_no).exclude(id=sector_id).count()
        else: existing = Sector.objects.filter(ref_no=ref_no).count()
        
        if existing:
            self._errors['ref_no'] = ErrorList(['เลขสำนักนี้ซ้ำกับสำนักอื่น'])
            del cleaned_data['ref_no']
        
        return cleaned_data

class ModifyMasterPlanForm(forms.Form):
    master_plan_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    ref_no = forms.IntegerField(label='รหัสแผน')
    name = forms.CharField(max_length=512, label='ชื่อแผน')
    sectors = SectorCheckboxChoiceField(label='สำนักที่ดูแล')

    def clean(self):
        cleaned_data = self.cleaned_data
        master_plan_id = cleaned_data.get('master_plan_id')
        ref_no = cleaned_data.get('ref_no')
        
        if master_plan_id: existing = MasterPlan.objects.filter(ref_no=ref_no).exclude(id=master_plan_id).count()
        else: existing = MasterPlan.objects.filter(ref_no=ref_no).count()
        
        if existing:
            self._errors['ref_no'] = ErrorList(['รหัสแผนหลักนี้ซ้ำกับแผนหลักอื่น'])
            del cleaned_data['ref_no']
        
        return cleaned_data
