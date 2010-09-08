# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.conf import settings
from django.core.urlresolvers import reverse

from helper import permission, utilities

from accounts.models import UserRoleResponsibility, RoleDetails
from domain.models import SectorMasterPlan

# TEMPLATE #################################################################

@register.simple_tag
def display_header_navigation(user):
    html = '<a href="%s"><img src="%s/images/base/nav_home.png" class="icon"/> หน้าผู้ใช้</a>' % (reverse('view_homepage'), settings.MEDIA_URL)
    
    if user.is_superuser:
        html = html + '<a href="%s"><img src="%s/images/base/nav_admin.png" class="icon"/> จัดการระบบ</a>' % (reverse('view_administration'), settings.MEDIA_URL)
    
    html = html + '<a href="%s"><img src="%s/images/base/nav_org.png" class="icon"/> ผังองค์กร</a>' % (reverse('view_organization'), settings.MEDIA_URL)
    
    return html

@register.simple_tag
def display_sector_header(user, sector):
    return unicode('<h1>สำนัก %d - %s</h1>', 'utf-8') % (sector.ref_no, sector.name)

@register.simple_tag
def display_master_plan_header(user, master_plan):
    header_html = unicode('<h1>แผนหลัก %d - %s</h1>', 'utf-8') % (master_plan.ref_no, master_plan.name)
    
    if permission.access_obj(user, 'master_plan manage', master_plan):
        header_html = header_html + unicode('<div class="subtitle"><img src="%s/images/icons/settings.png" class="icon" /> <a href="%s">จัดการแผนหลัก</a></div>', 'utf-8') % (settings.MEDIA_URL, reverse('view_master_plan_manage_organization', args=[master_plan.ref_no]))
    
    return header_html

@register.simple_tag
def display_master_plan_management_header(user, master_plan):
    return unicode('<div class="supertitle"><a href="%s">แผน %d - %s</a></div><h1>จัดการแผนหลัก</h1>', 'utf-8') % (reverse('view_master_plan_overview', args=[master_plan.ref_no]), master_plan.ref_no, master_plan.name)

@register.simple_tag
def display_program_header(user, program):
    manager_names = permission.who_program_manager(program)
    if not manager_names: manager_names = unicode('(ไม่มีข้อมูล)', 'utf-8')
    
    return unicode('<div class="supertitle"><a href="%s">แผน %d - %s</a></div><h1>แผนงาน (%s) %s</h1><div class="subtitle">ผู้จัดการ: %s</div>', 'utf-8') % (reverse('view_master_plan_overview', args=[program.plan.master_plan.ref_no]), program.plan.master_plan.ref_no, program.plan.master_plan.name, program.ref_no, program.name, manager_names)

@register.simple_tag
def display_project_header(user, project):
    return unicode('<div class="supertitle"><a href="%s">แผนงาน %s - %s</a></div><h1>โครงการ (%s) %s</h1><div class="subtitle"><img src="%s/images/icons/edit.png" class="icon"/> <a href="%s">แก้ไขโครงการ</a></div>', 'utf-8') % (reverse('view_program_overview', args=[project.program.id]), project.program.ref_no, project.program.name, project.ref_no, project.name, settings.MEDIA_URL, reverse('view_project_edit_project', args=[project.id]))

@register.simple_tag
def display_project_edit_header(user, project):
    return unicode('<div class="supertitle"><a href="%s">โครงการ (%s) %s</a></div><h1>แก้ไขโครงการ</h1>', 'utf-8') % (reverse('view_project_overview', args=[project.id]), project.ref_no, project.name)

@register.simple_tag
def display_activity_header(user, activity):
    return unicode('<div class="supertitle"><a href="%s">แผนงาน %s</a> &#187; <a href="%s">โครงการ %s - %s</a></div><h1>กิจกรรม %s</h1><div class="subtitle"><img src="%s/images/icons/edit.png" class="icon"/> <a href="%s">แก้ไขกิจกรรม</a></div>', 'utf-8') % (reverse('view_program_overview', args=[activity.project.program.id]), activity.project.program.ref_no, reverse('view_project_overview', args=[activity.project.id]), activity.project.ref_no, activity.project.name, activity.name, settings.MEDIA_URL, reverse('view_activity_edit_activity', args=[activity.id]))

@register.simple_tag
def display_activity_edit_header(user, activity):
    return unicode('<div class="supertitle"><a href="%s">กิจกรรม %s</a></div><h1>แก้ไขกิจกรรม</h1>', 'utf-8') % (reverse('view_activity_overview', args=[activity.id]), activity.name)

@register.simple_tag
def display_report_header(user, report_submission):
    return unicode('<div class="supertitle"><a href="%s">แผนงาน %s - %s</a></div><h1>รายงาน %s</h1><div class="subtitle">กำหนดส่งวันที่ %s</div>', 'utf-8') % (reverse('view_activity_overview', args=[activity.id]), activity.name)


# ADMIN PAGE

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