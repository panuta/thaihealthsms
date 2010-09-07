# -*- encoding: utf-8 -*-
from django import template
register = template.Library()

from django.core.urlresolvers import reverse

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
    
    if page == 'report': html = html + '<li class="selected">กำหนดส่งรายงาน</li>'
    else: html = html + '<li><a href="%s">กำหนดส่งรายงาน</a></li>' % reverse('view_master_plan_manage_report', args=[master_plan.ref_no])
    
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
