# -*- encoding: utf-8 -*-
from datetime import date

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import NodeList

from helper import utilities, permission

register = template.Library()

# DATE TIME #################################################################

@register.filter(name='dateid')
def dateid(datetime):
    return utilities.format_dateid(datetime)

@register.filter(name='full_datetime')
def full_datetime(datetime):
    return utilities.format_full_datetime(datetime)

@register.filter(name='abbr_datetime')
def abbr_datetime(datetime):
    return utilities.format_abbr_datetime(datetime)

@register.filter(name='full_date')
def full_date(datetime):
    return utilities.format_full_date(datetime)

@register.filter(name='abbr_date')
def abbr_date(datetime):
    return utilities.format_abbr_date(datetime)

@register.filter(name='full_month_year')
def full_month_year(datetime):
    return utilities.format_full_month_year(datetime)

@register.filter(name='abbr_month_year')
def abbr_month_year(datetime):
    return utilities.format_abbr_month_year(datetime)

@register.filter(name='week_elapse')
def week_elapse(value):
    return utilities.week_elapse_text(value)

# Utilities ############################################################

@register.filter
def get_range(value):
    return [i+1 for i in range(value)]

# FORM #################################################################

@register.simple_tag
def display_required():
    return '<span class="required">* ต้องกรอก</span>'

# MESSAGES #################################################################

@register.simple_tag
def display_messages(messages):
    if messages:
        html = ''
        for message in messages:
            html = html + '<li class="%s">%s</li>' % (message.tags, message)
        
        return '<ul class="ss_messages">%s</ul>' % html
    else:
        return ''

# PERMISSION #################################################################

@register.simple_tag
def who_program_manager(program):
    manager_names = permission.who_program_manager(program)
    if not manager_names:
        manager_names = '(ไม่มีข้อมูล)'
    return manager_names

class AccessNode(template.Node):
    """
    Parameter
    user : django.contrib.auth.user object
    permission names : string represents permission names
    object : object to be accessed
    
    Permission Names Guide
    - Use ',' to separate between permission
    - Use '+' in front of permission list to indicate that all permissions listed must meet
    """
    
    def __init__(self, nodelist_true, nodelist_false, user, permission_name, obj):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.user = template.Variable(user)
        self.permission_names = permission_name.strip(' \"\'')
        self.obj = template.Variable(obj)
    
    def render(self, context):
        user = self.user.resolve(context)
        permission_names = self.permission_names
        obj = self.obj.resolve(context)
        
        at_least_one_permission = True
        if permission_names[0] == '+':
            at_least_one_permission = False
            permission_names = permission_names[1:]
        
        permission_names = [permission_name.strip() for permission_name in permission_names.split(',')]
        
        if permission.access_obj(user, permission_names, obj, at_least_one_permission):
            output = self.nodelist_true.render(context)
            return output
        else:
            output = self.nodelist_false.render(context)
            return output

@register.tag(name="access")
def do_access(parser, token):
    try:
        tag_name, user, permission_names, obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "Access tag raise ValueError"
    
    nodelist_true = parser.parse(('else', 'endaccess'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endaccess',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return AccessNode(nodelist_true, nodelist_false, user, permission_names, obj)

class RoleNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, user, role_names, obj):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.user = template.Variable(user)
        self.role_names = role_names.strip(' \"\'')
        self.obj = template.Variable(obj)
    
    def render(self, context):
        user = self.user.resolve(context)
        role_names = self.role_names
        obj = self.obj.resolve(context)
        
        roles = [role_name.strip() for role_name in role_names.split(',')]
        
        if permission.has_role_with_obj(user, roles, obj):
            output = self.nodelist_true.render(context)
            return output
        else:
            output = self.nodelist_false.render(context)
            return output

@register.tag(name="role")
def do_role(parser, token):
    try:
        tag_name, user, role_names, obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "Role tag raise ValueError"
    
    nodelist_true = parser.parse(('else', 'endrole'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endrole',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return RoleNode(nodelist_true, nodelist_false, user, role_names, obj)

# BACK TO PAGE #################################################################

@register.simple_tag
def back_to_this(request):
    back_list = request.GET.getlist('back')
    
    if back_list:
        return 'back=%s&back=%s' % (request.path, '&back='.join(request.GET.getlist('back')))
    else:
        return 'back=%s' % request.path

@register.simple_tag
def back_form(request):
    back_list = request.GET.getlist('back')
    
    str = ''
    for back in back_list:
        if str: str = str + '&'
        str = str + 'back=%s' % back
    
    if str:
        return '<input type="hidden" name="back" value="%s"/>' % str
    else:
        return ''

# TEMPLATE #################################################################

@register.simple_tag
def display_pagination(objects, url_name):
    if objects.paginator.num_pages != 1:
        html = ''
        
        if objects.number != 1:
            html = html + '<span><a href="%s">&#171; หน้าแรก</a></span>' % reverse(url_name)
        else:
            html = html + '<span class="disabled">&#171; หน้าแรก</span>'
        
        if objects.has_previous():
            html = html + '<span><a href="%s?p=%d">&#139; ก่อนหน้า</a></span>' % (reverse(url_name), objects.previous_page_number())
        else:
            html = html + '<span class="disabled">&#139; ก่อนหน้า</span>'
        
        html = html + '<span class="number">หน้าที่ %d / %d</span>' % (objects.number, objects.paginator.num_pages)
        
        if objects.has_next():
            html = html + '<span><a href="%s?p=%d">ถัดไป &#155;</a></span>' % (reverse(url_name), objects.next_page_number())
        else:
            html = html + '<span class="disabled">ถัดไป &#155;</span>'
        
        if objects.number != objects.paginator.num_pages:
            html = html + '<span><a href="%s?p=%d">หน้าสุดท้าย &#187;</a></span>' % (reverse(url_name), objects.paginator.num_pages)
        else:
            html = html + '<span class="disabled">หน้าสุดท้าย &#187;</span>'
        
        return '<div class="ss_pagination">%s</div>' % html
    
    else:
        return ''

@register.simple_tag
def generate_quarter_text(quarter_no, quarter_year):
    from helper.constants import THAI_MONTH_NAME
    
    start_month = settings.QUARTER_START_MONTH + (quarter_no * 3 - 3)
    if start_month > 12: start_month = start_month - 12
    
    end_month = start_month + 2
    if end_month > 12: end_month = end_month - 12
    
    if settings.QUARTER_START_MONTH != 1:
        if start_month >= settings.QUARTER_START_MONTH:
            if not settings.QUARTER_LOWER_YEAR_NUMBER:
                quarter_year = quarter_year - 1
        else:
            if settings.QUARTER_LOWER_YEAR_NUMBER:
                quarter_year = quarter_year + 1
    
    return '%s %d - %s %d' % (THAI_MONTH_NAME[start_month], quarter_year+543, THAI_MONTH_NAME[end_month], quarter_year+543)

@register.simple_tag
def generate_quarter_table_header(quarter_year):
    from helper.constants import THAI_MONTH_ABBR_NAME
    
    start_month = settings.QUARTER_START_MONTH
    end_month = settings.QUARTER_START_MONTH + 2
    if end_month > 12: end_month = end_month - 12
    
    html = ''
    for i in range(1, 5):
        year = quarter_year
        
        if start_month >= settings.QUARTER_START_MONTH and not settings.QUARTER_LOWER_YEAR_NUMBER:
            year = quarter_year - 1
        
        if start_month < settings.QUARTER_START_MONTH and settings.QUARTER_LOWER_YEAR_NUMBER:
            year = quarter_year + 1
        
        html = html + '<th colspan="2" class="quarter">ไตรมาสที่ %d (%s - %s %d)</th>' % (i, THAI_MONTH_ABBR_NAME[start_month], THAI_MONTH_ABBR_NAME[end_month], year+543)
        
        start_month = start_month + 3
        if start_month > 12: start_month = start_month - 12
        
        end_month = end_month + 3
        if end_month > 12: end_month = end_month - 12
    
    return html

@register.simple_tag
def generate_quarter_month_selector(quarter, quarter_year):
    if not quarter_year: quarter_year = date.today().year + 543
    
    from helper.constants import THAI_MONTH_NAME
    
    start_month = settings.QUARTER_START_MONTH
    end_month = settings.QUARTER_START_MONTH + 2
    if end_month > 12: end_month = end_month - 12
    
    html = ''
    for i in range(1, 5):
        year = quarter_year
        
        if start_month >= settings.QUARTER_START_MONTH and not settings.QUARTER_LOWER_YEAR_NUMBER:
            year = quarter_year - 1
        
        if start_month < settings.QUARTER_START_MONTH and settings.QUARTER_LOWER_YEAR_NUMBER:
            year = quarter_year + 1
        
        if i == quarter:
            html = html + '<option value="%d" selected="selected">%s - %s %d</option>' % (i, THAI_MONTH_NAME[start_month], THAI_MONTH_NAME[end_month], year)
        else:
            html = html + '<option value="%d">%s - %s %d</option>' % (i, THAI_MONTH_NAME[start_month], THAI_MONTH_NAME[end_month], year)
        
        start_month = start_month + 3
        if start_month > 12: start_month = start_month - 12
        
        end_month = end_month + 3
        if end_month > 12: end_month = end_month - 12
    
    return html

@register.simple_tag
def generate_quarter_year_selector(quarter_year):
    if not quarter_year: quarter_year = date.today().year
    
    quarter_year = quarter_year + 543
    year_span = settings.QUARTER_INPUT_YEAR_SPAN
    
    html = '<option value="back-%d">&lt; ปีก่อนหน้า</option>' % (quarter_year - year_span)
    for i in range(-year_span, year_span+1):
        if (quarter_year + i) == quarter_year:
            html = html + '<option selected="selected">%d</option>' % (quarter_year + i)
        else:
            html = html + '<option>%d</option>' % (quarter_year + i)
    
    html = html + '<option value="next-%d">ปีถัดไป &gt;</option>' % (quarter_year + year_span)
    
    return html
