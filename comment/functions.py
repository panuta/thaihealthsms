
from django.http import Http404

from models import *

from accounts.models import UserRoleResponsibility
from domain.models import Activity, Project
from report.models import ReportSubmission
from kpi.models import DomainKPISchedule
from budget.models import BudgetSchedule

def _comment_receivers(object_name, object_id, sender):
    
    roles = (
        Group.objects.get(name='sector_manager_assistant'),
        Group.objects.get(name='sector_specialist'),
        Group.objects.get(name='program_manager'),
        Group.objects.get(name='program_manager_assistant')
    )
    
    if object_name == 'activity':
        activity = Activity.objects.get(pk=object_id)
        role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), programs__in=(activity.project.program,))
    
    elif object_name == 'project':
        project = Project.objects.get(pk=object_id)
        role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), programs__in=(project.program,))
    
    elif object_name == 'report':
        report_submission = ReportSubmission.objects.get(pk=object_id)
        role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), programs__in=(report_submission.program,))
    
    elif object_name == 'kpi':
        kpi_schedule = DomainKPISchedule.objects.get(pk=object_id)
        role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), programs__in=(kpi_schedule.program,))
    
    elif object_name == 'budget':
        budget_schedule = BudgetSchedule.objects.get(pk=object_id)
        role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), programs__in=(budget_schedule.program,))
    
    users = set()
    for r in role_resps:
        users.add(r.user)
    users.add(sender)
    return users

def get_object_instance(object_name, object_id):
    if object_name == 'project':
        object = Project.objects.get(pk=object_id)
        
    elif object_name == 'activity':
        object = Activity.objects.get(pk=object_id)
        
    elif object_name == 'report':
        object = ReportSubmission.objects.get(pk=object_id)
    
    elif object_name == 'kpi':
        object = DomainKPISchedule.objects.get(pk=object_id)
    
    elif object_name == 'budget':
        object = BudgetSchedule.objects.get(pk=object_id)
        
    else:
        object = None
    
    return object

def post_comment_for(object_name, object_id, message, user_account):
    if object_name not in ('activity', 'project', 'report', 'kpi', 'budget'): raise Http404
    
    comment = Comment.objects.create(message=message.strip(), object_id=object_id, object_name=object_name, sent_by=user_account)
    for receiver in _comment_receivers(object_name, object_id, user_account):
        UnreadComment.objects.create(comment=comment, user=receiver)
    
    return comment

def post_reply_comment_for(to_comment, object_name, object_id, message, user_account):
    if object_name not in ('activity', 'project', 'report', 'kpi', 'budget'): raise Http404
    
    reply = CommentReply.objects.create(comment=to_comment, message=message.strip(), sent_by=user_account)
    for receiver in _comment_receivers(object_name, object_id, user_account):
        UnreadCommentReply.objects.create(reply=reply, user=receiver)
    
    return reply

def get_comments_for(object_name, object_id, user_account, mark_as_read=False):
    comments = Comment.objects.filter(object_name=object_name, object_id=object_id).order_by('-sent_on')
    
    for comment in comments:
        try:
            unread = UnreadComment.objects.get(user=user_account, comment=comment)
            comment.is_unread = True
            
            if mark_as_read: unread.delete()
            
        except UnreadComment.DoesNotExist:
            comment.is_unread = False
        
        comment.replies = CommentReply.objects.filter(comment=comment).order_by('sent_on')
        
        for reply in comment.replies:
            try:
                unread = UnreadCommentReply.objects.get(user=user_account, reply=reply)
                reply.is_unread = True
                
                if mark_as_read: unread.delete()
                
            except UnreadCommentReply.DoesNotExist:
                reply.is_unread = False
    
    return comments

def get_user_unread_comment_count(user_account):
    unread_comments = UnreadComment.objects.filter(user=user_account)
    unread_replies = UnreadCommentReply.objects.filter(user=user_account)
    return len(unread_comments) + len(unread_replies)

def get_user_unread_comments(user_account):
    unread_comments = UnreadComment.objects.filter(user=user_account)
    unread_replies = UnreadCommentReply.objects.filter(user=user_account).order_by('reply__sent_on')
    unread_count = len(unread_comments) + len(unread_replies)
    
    obj_comments = {}
    
    for unread_comment in unread_comments:
        hash_str = "%s%d" % (unread_comment.comment.object_name, unread_comment.comment.object_id)
        
        if not hash_str in obj_comments:
            obj_comments[hash_str] = {'object_name':unread_comment.comment.object_name, 'object_id':unread_comment.comment.object_id, 'comments':[], 'latest':unread_comment.comment.sent_on}
        
        if unread_comment.comment.sent_on > obj_comments[hash_str]['latest']:
            obj_comments[hash_str]['latest'] = unread_comment.comment.sent_on
        
        obj_comments[hash_str]['comments'].append(unread_comment.comment)
    
    for unread_reply in unread_replies:
        hash_str = "%s%d" % (unread_reply.reply.comment.object_name, unread_reply.reply.comment.object_id)
        
        if not hash_str in obj_comments:
            obj_comments[hash_str] = {'object_name':unread_reply.reply.comment.object_name, 'object_id':unread_reply.reply.comment.object_id, 'comments':[], 'latest':unread_reply.reply.sent_on}
        
        comment_found = False
        for comment in obj_comments[hash_str]['comments']:
            if comment == unread_reply.comment:
                if not hasattr(comment, 'replies'):
                    comment.replies = []
                
                if unread_reply.reply.sent_on > obj_comments[hash_str]['latest']:
                    obj_comments[hash_str]['latest'] = unread_reply.reply.sent_on
                
                comment.replies.append(unread_reply.reply)
                comment_found = True
        
        if not comment_found:
            comment = unread_reply.comment
            comment.replies = [unread_reply.reply]
            obj_comments[hash_str]['comments'].append(comment)
    
    comments = []
    for hash_str in obj_comments.keys():
        obj_comment = obj_comments[hash_str]
        obj_comment['comments'].sort(_comments_sorting, reverse=True)
        comments.append(obj_comment)
    
    comments.sort(_comment_objects_sorting, reverse=True)
    
    return (comments, unread_count)

def _comments_sorting(x, y):
    return cmp(x.sent_on, y.sent_on)

def _comment_objects_sorting(x, y):
    return cmp(x['latest'], y['latest'])