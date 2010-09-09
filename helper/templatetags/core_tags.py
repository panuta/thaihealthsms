# -*- encoding: utf-8 -*-
from django import template
register = template.Library()

from django.conf import settings
from django.core.urlresolvers import reverse

from helper import permission, utilities

#
# HEADER
#

@register.simple_tag
def display_header_navigation(user):
    html = '<a href="%s"><img src="%s/images/base/nav_home.png" class="icon"/> หน้าผู้ใช้</a>' % (reverse('view_homepage'), settings.MEDIA_URL)
    
    if not user.is_superuser:
        html = html + '<a href="%s"><img src="%s/images/base/nav_inbox.png" class="icon"/> ข้อความ</a>' % (reverse('view_user_inbox'), settings.MEDIA_URL)
    
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
    return unicode('<div class="supertitle"><a href="%s">แผนงาน %s - %s</a></div><h1>รายงาน %s</h1><div class="subtitle">รอบกำหนดส่งวันที่ %s</div>', 'utf-8') % (reverse('view_program_overview', args=[report_submission.program.id]), report_submission.program.ref_no, report_submission.program.name, report_submission.report.name, utilities.format_abbr_date(report_submission.schedule_date))

#
# TAB
#

def _generate_tabs(html):
    return '<div id="body-tabs"><ul>%s</ul><div class="clear"></div></div>' % html

@register.simple_tag
def tabs_for_administration(page):
    html = ''
    
    if page == 'organization': html = html + '<li class="selected">โครงสร้างองค์กร</li>'
    else: html = html + '<li><a href="%s">โครงสร้างองค์กร</a></li>' % reverse('view_administration_organization')
    
    if page == 'users': html = html + '<li class="selected">ผู้ใช้ระบบ</li>'
    else: html = html + '<li><a href="%s">ผู้ใช้ระบบ</a></li>' % reverse('view_administration_users')
    
    return _generate_tabs(html)

@register.simple_tag
def tabs_for_sector(page, user, sector):
    html = ''
    
    if page == 'overview': html = html + '<li class="selected">ภาพรวม</li>'
    else: html = html + '<li><a href="%s">ภาพรวม</a></li>' % reverse('view_sector_overview', args=[sector.ref_no])
    
    if page == 'kpi': html = html + '<li class="selected">แผนผลลัพธ์</li>'
    else: html = html + '<li><a href="%s">แผนผลลัพธ์</a></li>' % reverse('view_sector_kpi', args=[sector.ref_no])
    
    if page == 'budget': html = html + '<li class="selected">แผนการเงิน</li>'
    else: html = html + '<li><a href="%s">แผนการเงิน</a></li>' % reverse('view_sector_budget', args=[sector.ref_no])
    
    return _generate_tabs(html)

@register.simple_tag
def tabs_for_master_plan(page, user, master_plan):
    html = ''
    
    if page == 'overview': html = html + '<li class="selected">ภาพรวม</li>'
    else: html = html + '<li><a href="%s">ภาพรวม</a></li>' % reverse('view_master_plan_overview', args=[master_plan.ref_no])
    
    if page == 'programs': html = html + '<li class="selected">แผนงาน</li>'
    else: html = html + '<li><a href="%s">แผนงาน</a></li>' % reverse('view_master_plan_programs', args=[master_plan.ref_no])
    
    if page == 'kpi': html = html + '<li class="selected">แผนผลลัพธ์</li>'
    else: html = html + '<li><a href="%s">แผนผลลัพธ์</a></li>' % reverse('view_master_plan_kpi', args=[master_plan.ref_no])
    
    if page == 'budget': html = html + '<li class="selected">แผนการเงิน</li>'
    else: html = html + '<li><a href="%s">แผนการเงิน</a></li>' % reverse('view_master_plan_budget', args=[master_plan.ref_no])
    
    return _generate_tabs(html)

@register.simple_tag
def tabs_for_manage_master_plan(page, master_plan):
    html = ''
    
    if page == 'organization': html = html + '<li class="selected">แผนงาน</li>'
    else: html = html + '<li><a href="%s">แผนงาน</a></li>' % reverse('view_master_plan_manage_organization', args=[master_plan.ref_no])
    
    if page == 'report': html = html + '<li class="selected">รายงาน</li>'
    else: html = html + '<li><a href="%s">รายงาน</a></li>' % reverse('view_master_plan_manage_report', args=[master_plan.ref_no])
    
    if page == 'kpi': html = html + '<li class="selected">ตัวชี้วัด</li>'
    else: html = html + '<li><a href="%s">ตัวชี้วัด</a></li>' % reverse('view_master_plan_manage_kpi', args=[master_plan.ref_no])
    
    return _generate_tabs(html)

@register.simple_tag
def tabs_for_program(page, user, program):
    html = ''
    
    if page == 'overview': html = html + '<li class="selected">ภาพรวม</li>'
    else: html = html + '<li><a href="%s">ภาพรวม</a></li>' % reverse('view_program_overview', args=[program.id])
    
    if page == 'projects': html = html + '<li class="selected">โครงการ</li>'
    else: html = html + '<li><a href="%s">โครงการ</a></li>' % reverse('view_program_projects', args=[program.id])
    
    if page == 'kpi': html = html + '<li class="selected">แผนผลลัพธ์</li>'
    else: html = html + '<li><a href="%s">แผนผลลัพธ์</a></li>' % reverse('view_program_kpi', args=[program.id])
    
    if page == 'budget': html = html + '<li class="selected">แผนการเงิน</li>'
    else: html = html + '<li><a href="%s">แผนการเงิน</a></li>' % reverse('view_program_budget', args=[program.id])
    
    if page == 'reports': html = html + '<li class="selected">รายงาน</li>'
    else: html = html + '<li><a href="%s">รายงาน</a></li>' % reverse('view_program_reports', args=[program.id])
    
    return _generate_tabs(html)

@register.simple_tag
def tabs_for_project(page, user, project):
    html = ''
    
    if page == 'overview': html = html + '<li class="selected">ภาพรวม</li>'
    else: html = html + '<li><a href="%s">ภาพรวม</a></li>' % reverse('view_project_overview', args=[project.id])
    
    if page == 'activities': html = html + '<li class="selected">กิจกรรม</li>'
    else: html = html + '<li><a href="%s">กิจกรรม</a></li>' % reverse('view_project_activities', args=[project.id])
    
    if page == 'comments': html = html + '<li class="selected">ความคิดเห็น</li>'
    else: html = html + '<li><a href="%s">ความคิดเห็น</a></li>' % reverse('view_project_comments', args=[project.id])
    
    return _generate_tabs(html)

@register.simple_tag
def tabs_for_activity(page, user, activity):
    html = ''
    
    if page == 'overview': html = html + '<li class="selected">ภาพรวม</li>'
    else: html = html + '<li><a href="%s">ภาพรวม</a></li>' % reverse('view_activity_overview', args=[activity.id])
    
    if page == 'comments': html = html + '<li class="selected">ความคิดเห็น</li>'
    else: html = html + '<li><a href="%s">ความคิดเห็น</a></li>' % reverse('view_activity_comments', args=[activity.id])
    
    return _generate_tabs(html)

@register.simple_tag
def tabs_for_report(page, user, report_submission):
    html = ''
    
    if page == 'overview': html = html + '<li class="selected">เนื้อหา</li>'
    else: html = html + '<li><a href="%s">เนื้อหา</a></li>' % reverse('view_report_overview', args=[report_submission.program.id, report_submission.report.id, utilities.format_dateid(report_submission.schedule_date)])
    
    if page == 'reference': html = html + '<li class="selected">ข้อมูลประกอบ</li>'
    else: html = html + '<li><a href="%s">ข้อมูลประกอบ</a></li>' % reverse('view_report_reference', args=[report_submission.program.id, report_submission.report.id, utilities.format_dateid(report_submission.schedule_date)])
    
    if page == 'comments': html = html + '<li class="selected">ความคิดเห็น</li>'
    else: html = html + '<li><a href="%s">ความคิดเห็น</a></li>' % reverse('view_report_comments', args=[report_submission.program.id, report_submission.report.id, utilities.format_dateid(report_submission.schedule_date)])
    
    return _generate_tabs(html)