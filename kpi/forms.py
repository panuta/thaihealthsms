# -*- encoding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList

from models import *

from domain.models import MasterPlan
from domain.forms import MasterPlanChoiceField

# FIELD CLASSES
class DomainKPICategoryChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = '-- เลือกประเภท --'
        kwargs['queryset'] = DomainKPICategory.objects.all()
        forms.ModelChoiceField.__init__(self, *args, **kwargs)
    
    def label_from_instance(self, obj):
        return obj.name

# FORM CLASSES

class DomainKPICategoryModifyForm(forms.Form):
    name = forms.CharField(max_length=300, label='ชื่อประเภทตัวชี้วัด')

class DomainKPIModifyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        master_plan = kwargs.pop('master_plan', None)
        program = kwargs.pop('program', None)
        forms.Form.__init__(self, *args, **kwargs)
        
        if master_plan:
            self.fields['category'].queryset = DomainKPICategory.objects.filter(master_plan=master_plan).order_by('name')
        
        if program:
            self.fields['category'].queryset = DomainKPICategory.objects.filter(program=program).order_by('name')
    
    ref_no = forms.CharField(max_length=100, label='รหัส')
    name = forms.CharField(max_length=1000, label='ชื่อตัวชี้วัด')
    abbr_name = forms.CharField(required=False, max_length=200, label='ชื่อย่อตัวชี้วัด')
    year = forms.IntegerField(label='สำหรับปี')
    category = DomainKPICategoryChoiceField(required=False, label='ประเภท')
    unit_name = forms.CharField(max_length=300, label='หน่วยที่ใช้วัด')

class ModifyKPIRemarkForm(forms.Form):
    remark = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(), label='หมายเหตุ')