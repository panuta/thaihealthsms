# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.conf import settings
from django.core.urlresolvers import reverse

from helper import permission, utilities

from accounts.models import UserRoleResponsibility, RoleDetails
from domain.models import SectorMasterPlan

#
# ADMIN PAGE
#

@register.simple_tag
def list_user_roles(user_account):
    role_html = ''
    
    for responsibility in UserRoleResponsibility.objects.filter(user=user_account):
        group_details = RoleDetails.objects.get(role=responsibility.role)
        
        if group_details.level == RoleDetails.SECTOR_LEVEL:
            for sector in responsibility.sectors.all():
                role_html = role_html + unicode('<li>%s - สำนัก %d</li>', 'utf-8') % (group_details.name, sector.ref_no)
            
        elif group_details.level == RoleDetails.PROGRAM_LEVEL:
            for program in responsibility.programs.all():
                role_html = role_html + unicode('<li>%s - แผนงาน %s</li>', 'utf-8') % (group_details.name, program.ref_no)
            
        else:
            role_html = role_html + '<li>%s</li>' % (group_details.name)
    
    return role_html

#
# USER PAGE
#

@register.simple_tag
def list_responsibility_depts(responsibility):
    html = ''
    
    if responsibility.role.name == 'sector_manager':
        
        for sector in responsibility.sectors.all():
            html += '<li class="dept"><h4>สำนัก %d</h4><ul>' % sector.ref_no
            for smp in SectorMasterPlan.objects.filter(sector=sector):
                html += '<li class="subdept">แผน %d</li>' % smp.master_plan.ref_no
            
            html += '</ul></li>'
        
    elif responsibility.role.name == 'sector_manager':
        pass
    elif responsibility.role.name == 'sector_manager':
        pass
    elif responsibility.role.name == 'sector_manager':
        pass
    
    return html

#
# BUDGET
#
@register.simple_tag
def display_budget_schedule_status(schedule):
    from budget.functions import determine_schedule_status
    status = determine_schedule_status(schedule)
    
    if status == 'today':
        return 'กำหนดเบิกจ่ายในวันนี้'
    elif status == 'future':
        return '<span class="future">ยังไม่ถึงวันเบิก</span>'
    elif status == 'late':
        return unicode('<span class="late">เลยวันที่เบิกมาแล้ว<br/>%s</span>', 'utf-8') % utilities.week_elapse_text(schedule.schedule_on)
    elif status == 'claimed_higher' or status == 'claimed_equal' or status == 'claimed_lower':
        return unicode('<span class="claimed">เบิกเมื่อวันที่<br/>%s</span>', 'utf-8') % utilities.format_abbr_date(schedule.schedule_on)
    else:
        return 'ไม่มีข้อมูล'

@register.simple_tag
def display_full_budget_schedule_status(schedule):
    from budget.functions import determine_schedule_status
    status = determine_schedule_status(schedule)
    
    if status == 'today':
        return 'กำหนดเบิกจ่ายในวันนี้'
    elif status == 'future':
        return '<span class="future">ยังไม่ถึงวันเบิก</span>'
    elif status == 'late':
        return unicode('<span class="late">เลยวันที่เบิกมาแล้ว<br/>%s</span>', 'utf-8') % utilities.week_elapse_text(schedule.schedule_on)
    elif status == 'claimed_higher' or status == 'claimed_equal' or status == 'claimed_lower':
        return unicode('<span class="claimed">เบิกเมื่อวันที่<br/>%s</span>', 'utf-8') % utilities.format_abbr_date(schedule.schedule_on)
    else:
        return 'ไม่มีข้อมูล'

@register.simple_tag
def display_budget_schedule_revision(revision):
    pass

#
# REPORT
#

@register.simple_tag
def display_report_due(report):
    from report.models import ReportDueRepeatable, ReportDueDates
    from report.models import REPORT_NO_DUE_DATE, REPORT_REPEAT_DUE, REPORT_DUE_DATES
    
    if report.due_type == REPORT_REPEAT_DUE:
        repeatable = ReportDueRepeatable.objects.get(report=report)
        
        text = 'ทุกๆ %d เดือน' % repeatable.schedule_cycle_length
        if repeatable.schedule_monthly_date:
            return 'วันที่ %d %s' % (repeatable.schedule_monthly_date, text) 
        else:
            return 'วันสิ้นเดือน %s' % text
        
    elif report.due_type == REPORT_DUE_DATES:
        due_dates = ReportDueDates.objects.filter(report=report).order_by('due_date')
        text = ''
        for due_date in due_dates:
            if text: text = text + ' , '
            text = text + utilities.format_abbr_date(due_date.due_date)
        
        return text
        
    else:
        return 'ยังไม่มีการกำหนด'

@register.simple_tag
def display_report_sending_notice(submission):
    if submission.this_is == 'overdue':
        return unicode('<div class="notice overdue">เลขกำหนดส่งมาแล้ว ', 'utf-8') + utilities.week_elapse_text(submission.schedule_date) + '</div>'
    elif submission.this_is == 'waiting':
        return unicode('<div class="notice waiting">กำลังรอการอนุมัติรายงาน</div>', 'utf-8')
    elif submission.this_is == 'rejected':
        return unicode('<div class="notice rejected">รายงานถูกตีกลับเมื่อวันที่ ', 'utf-8') + utilities.format_abbr_datetime(submission.approval_date) + '</div>'
    return ''