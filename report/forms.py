# -*- encoding: utf-8 -*-
from django import forms

from widgets import YUICalendar

from models import Report

from domain.models import Project
from domain.forms import ProjectMultipleChoiceField

month_cycle = [(i,i) for i in range(1,13)]
date_cycle = [(0, 'วันสิ้นเดือน'),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,11),(12,12),(13,13),(14,14),(15,15),(16,16),(17,17),(18,18),(19,19),(20,20),(21,21),(22,22),(23,23),(24,24),(25,25),(26,26),(27,27),(28,28),(29,29),(30,30),(31,31)]

from models import REPORT_NO_DUE_DATE, REPORT_DUE_DATES, REPORT_REPEAT_DUE

REPORT_DUE_TYPE = {
    'no_due':REPORT_NO_DUE_DATE,
    'dates_due':REPORT_DUE_DATES,
    'repeat_due':REPORT_REPEAT_DUE,
}

# FIELD CLASSES

class ReportChoiceField(forms.ModelMultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
    
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = None
        kwargs['queryset'] = Report.objects.all().order_by('name')
        forms.ModelChoiceField.__init__(self, *args, **kwargs)
    
    def label_from_instance(self, obj):
        return obj.name

# FORM CLASSES

class MasterPlanReportForm(forms.Form):
    name = forms.CharField(max_length=512, label='ชื่อรายงาน')
    need_approval = forms.BooleanField(required=False, label='รายงานที่ส่งมา ต้องมีการรับรองรายงาน')
    
    cycle_length = forms.ChoiceField(label='ส่งรายงานทุกๆ', choices=month_cycle)
    monthly_date = forms.ChoiceField(label='ในวันที่', choices=date_cycle)
    
    notify_before = forms.BooleanField(label='แจ้งเตือนก่อนกำหนดส่งรายงาน', required=False)
    notify_before_days = forms.IntegerField(required=False)
    
    notify_due = forms.BooleanField(label='แจ้งเตือนวันกำหนดส่งรายงาน', required=False)

class ProgramReportForm(forms.Form):
    name = forms.CharField(max_length=512, label='ชื่อรายงาน')
    need_checkup = forms.BooleanField(required=False, label='ส่งรายงานถึงแผนหลัก')
    need_approval = forms.BooleanField(required=False, label='ต้องมีการรับรองรายงานที่ส่งมา')
    
    cycle_length = forms.ChoiceField(label='ส่งรายงานทุกๆ', choices=month_cycle)
    monthly_date = forms.ChoiceField(label='ในวันที่', choices=date_cycle)
    
    notify_before = forms.BooleanField(label='แจ้งเตือนก่อนกำหนดส่งรายงาน', required=False)
    notify_before_days = forms.IntegerField(required=False)
    
    notify_due = forms.BooleanField(label='แจ้งเตือนวันกำหนดส่งรายงาน', required=False)

class MasterPlanProgramReportsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        master_plan = kwargs.pop('master_plan', None)
        forms.Form.__init__(self, *args, **kwargs)
        
        if master_plan:
            self.fields["reports"].queryset = Report.objects.filter(master_plan=master_plan).order_by('name')
    
    reports = ReportChoiceField(label='รายงาน', required=False)