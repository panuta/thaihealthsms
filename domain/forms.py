# -*- encoding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList

from domain.models import *

from widgets import YUICalendar

# FIELD CLASSES

class SectorChoiceField(forms.ModelChoiceField):
	def __init__(self, *args, **kwargs):
		kwargs['empty_label'] = None
		kwargs['queryset'] = Sector.objects.all().order_by('ref_no')
		forms.ModelChoiceField.__init__(self, *args, **kwargs)
	
	def label_from_instance(self, obj):
		return '%d %s' % (obj.ref_no, obj.name)

class SectorCheckboxChoiceField(forms.ModelMultipleChoiceField):
	widget = forms.CheckboxSelectMultiple
	
	def __init__(self, *args, **kwargs):
		kwargs['empty_label'] = None
		kwargs['queryset'] = Sector.objects.all().order_by('ref_no')
		forms.ModelChoiceField.__init__(self, *args, **kwargs)
	
	def label_from_instance(self, obj):
		return '%d %s' % (obj.ref_no, obj.name)

class MasterPlanChoiceField(forms.ModelChoiceField):
	def __init__(self, *args, **kwargs):
		kwargs['empty_label'] = None
		kwargs['queryset'] = MasterPlan.objects.all().order_by('ref_no')
		forms.ModelChoiceField.__init__(self, *args, **kwargs)
	
	def label_from_instance(self, obj):
		return '%d %s' % (obj.ref_no, obj.name)

class PlanChoiceField(forms.ModelChoiceField):
	def __init__(self, *args, **kwargs):
		kwargs['empty_label'] = None
		kwargs['queryset'] = Plan.objects.all().order_by('master_plan__ref_no', 'ref_no')
		forms.ModelChoiceField.__init__(self, *args, **kwargs)
	
	def label_from_instance(self, obj):
		return unicode('%s %s', 'utf-8') % (obj.ref_no, obj.name)

class ProjectMultipleChoiceField(forms.ModelMultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
    
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = None
        kwargs['queryset'] = Project.objects.all().order_by('ref_no')
        forms.ModelChoiceField.__init__(self, *args, **kwargs)
    
    def label_from_instance(self, obj):
    	if obj.ref_no:
    		return '(' + obj.ref_no + ') ' + obj.name
     	else:
     		return obj.name

# FORM CLASSES

class PlanModifyForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.master_plan = kwargs.pop('master_plan', None)
		forms.Form.__init__(self, *args, **kwargs)
	
	plan_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	ref_no = forms.CharField(max_length=100, label='รหัส')
	name = forms.CharField(max_length=500, label='ชื่อกลุ่มแผนงาน')
	
	def clean(self):
		cleaned_data = self.cleaned_data
		plan_id = cleaned_data.get('plan_id')
		ref_no = cleaned_data.get('ref_no')
		
		if plan_id: existing = Plan.objects.filter(ref_no=ref_no, master_plan=self.master_plan).exclude(id=plan_id).count()
		else: existing = Plan.objects.filter(ref_no=ref_no, master_plan=self.master_plan).count()
		
		if existing:
			self._errors['ref_no'] = ErrorList(['เลขที่กลุ่มแผนงานนี้ซ้ำกับกลุ่มแผนงานอื่นในแผนหลักเดียวกัน'])
			del cleaned_data['ref_no']
		
		return cleaned_data

class MasterPlanProgramForm(forms.Form):
	def __init__(self, *args, **kwargs):
		master_plan = kwargs.pop('master_plan', None)
		forms.Form.__init__(self, *args, **kwargs)
		
		if master_plan:
			self.fields["plan"].queryset = Plan.objects.filter(master_plan=master_plan).order_by('master_plan__ref_no', 'ref_no')
			self.master_plan = master_plan
	
	program_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	plan = PlanChoiceField(label="กลุ่มแผนงาน")
	ref_no = forms.CharField(max_length=64, label='รหัสแผนงาน')
	name = forms.CharField(max_length=500, label='ชื่อแผนงาน')
	abbr_name = forms.CharField(max_length=200, label='ชื่อย่อแผนงาน', required=False)
	manager_name = forms.CharField(max_length=300, label='ผู้จัดการแผนงาน', required=False)
	start_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_start_date'}), label='ระยะเวลา', required=False)
	end_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง', required=False)
	
	def clean(self):
		cleaned_data = self.cleaned_data
		start_date = cleaned_data.get('start_date')
		end_date = cleaned_data.get('end_date')
		
		if start_date > end_date:
			self._errors['start_date'] = ErrorList(['วันที่เริ่มต้นเกิดขึ้นหลังจากวันที่สิ้นสุด'])
			del cleaned_data['start_date']
		
		ref_no = cleaned_data.get('ref_no')
		program_id = cleaned_data.get('program_id')
		
		if program_id: existing = Program.objects.filter(ref_no=ref_no, plan__master_plan=self.master_plan).exclude(id=program_id).count()
		else: existing = Program.objects.filter(ref_no=ref_no, plan__master_plan=self.master_plan).count()
		
		if existing:
			self._errors['ref_no'] = ErrorList(['เลขที่แผนงานนี้ซ้ำกับแผนงานอื่นในแผนหลัก'])
			del cleaned_data['ref_no']
		
		return cleaned_data

class ProjectModifyForm(forms.Form):
	program_id = forms.IntegerField(widget=forms.HiddenInput())
	project_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	ref_no = forms.CharField(required=False, max_length=64, label='รหัสโครงการ')
	contract_no = forms.CharField(max_length=200, label='เลขที่สัญญา', required=False)
	name = forms.CharField(max_length=500, label='ชื่อโครงการ')
	abbr_name = forms.CharField(required=False, max_length=200, label='ชื่อย่อโครงการ')
	start_date = forms.DateField(required=False, widget=YUICalendar(attrs={'id':'id_start_date'}), label='ระยะเวลาโครงการ')
	end_date = forms.DateField(required=False, widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง')
	description = forms.CharField(required=False, max_length=1000, label='คำอธิบายโครงการ', widget=forms.Textarea)
	
	def clean(self):
		cleaned_data = self.cleaned_data
		start_date = cleaned_data.get('start_date')
		end_date = cleaned_data.get('end_date')
		
		if start_date > end_date:
			self._errors['start_date'] = ErrorList(['วันที่เริ่มต้นเกิดขึ้นหลังจากวันที่สิ้นสุด'])
			del cleaned_data['start_date']
		
		program_id = cleaned_data.get('program_id')
		project_id = cleaned_data.get('project_id')
		ref_no = cleaned_data.get('ref_no')
		
		if ref_no:
			program = Program.objects.get(pk=program_id)
			
			if project_id: existing = Project.objects.filter(ref_no=ref_no, program=program).exclude(id=project_id).count()
			else: existing = Project.objects.filter(ref_no=ref_no, program=program).count()
			
			if existing:
				self._errors['ref_no'] = ErrorList(['เลขที่โครงการนี้ซ้ำกับโครงการอื่นในแผนงาน'])
				del cleaned_data['ref_no']
			
		return cleaned_data

class ActivityModifyForm(forms.Form):
	name 			= forms.CharField(max_length=500, label='ชื่อกิจกรรม')
	start_date      = forms.DateField(widget=YUICalendar(attrs={'id':'id_start_date'}), label='เริ่มตั้งแต่วันที่', required=False)
	end_date        = forms.DateField(widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง', required=False)
	description 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='รายละเอียด')
	location 		= forms.CharField(max_length=2000, required=False, label='สถานที่')
	result_goal 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่ต้องการ')
	result_real 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่เกิดขึ้น')
	
	def clean(self):
		cleaned_data = self.cleaned_data
		start_date = cleaned_data.get('start_date')
		end_date = cleaned_data.get('end_date')
		
		if start_date > end_date:
			self._errors['start_date'] = ErrorList(['วันที่เริ่มต้นเกิดขึ้นหลังจากวันที่สิ้นสุด'])
			del cleaned_data['start_date']
		
		return cleaned_data