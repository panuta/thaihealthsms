# -*- encoding: utf-8 -*-
from django import forms

class ModifyBudgetRemarkForm(forms.Form):
    remark = forms.CharField(max_length=1000, widget=forms.Textarea(), label='หมายเหตุ')