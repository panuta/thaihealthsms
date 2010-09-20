from django.db import models

from django.db import models
from django.contrib.auth.models import Group

class UnreadComment(models.Model):
    user = models.ForeignKey('accounts.UserAccount', related_name='user_comment')
    comment = models.ForeignKey('Comment')

class UnreadCommentReply(models.Model):
    user = models.ForeignKey('accounts.UserAccount', related_name='user_comment_reply')
    reply = models.ForeignKey('CommentReply')

class Comment(models.Model):
    message = models.CharField(max_length=1024)
    object_id = models.IntegerField(default=0)
    object_name = models.CharField(max_length=64, null=True)
    sent_on = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey('accounts.UserAccount', related_name='sent_by')
    
    class Meta:
        ordering = ['sent_on']

class CommentReply(models.Model):
    comment = models.ForeignKey('Comment')
    message = models.CharField(max_length=1024)
    sent_on = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey('accounts.UserAccount', related_name='reply_sent_by')
    
    class Meta:
        ordering = ['sent_on']

class CommentSubscriber(models.Model):
    user = models.ForeignKey('accounts.UserAccount')
    object_id = models.IntegerField(default=0)
    object_name = models.CharField(max_length=64, null=True)