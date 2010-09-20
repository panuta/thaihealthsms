# -*- encoding: utf-8 -*-

from django import forms

class PostCommentForm(forms.Form):
    comment_message = forms.CharField(max_length=1024, widget=forms.Textarea())
    