# -*- encoding: utf-8 -*-
from django.conf import settings

import calendar
from datetime import date

from constants import *

#
# DATE - TIME
#

def format_dateid(datetime):
    return '%02d%02d%d' % (datetime.day, datetime.month, datetime.year)

def format_full_datetime(datetime):
    return unicode('%d %s %d เวลา %02d:%02d น.', 'utf-8') % (datetime.day, unicode(THAI_MONTH_NAME[datetime.month], 'utf-8'), datetime.year + 543, datetime.hour, datetime.minute)

def format_abbr_datetime(datetime):
    return unicode('%d %s %d เวลา %02d:%02d น.', 'utf-8') % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], 'utf-8'), datetime.year + 543, datetime.hour, datetime.minute)

def format_full_date(datetime):
    return unicode('%d %s %d', 'utf-8') % (datetime.day, unicode(THAI_MONTH_NAME[datetime.month], 'utf-8'), datetime.year + 543)

def format_abbr_date(datetime):
    return unicode('%d %s %d', 'utf-8') % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], 'utf-8'), datetime.year + 543)

def format_full_month_year(datetime):
    return '%s %d' % (unicode(THAI_MONTH_NAME[datetime.month], "utf-8"), datetime.year + 543)

def format_abbr_month_year(datetime):
    return '%s %d' % (unicode(THAI_MONTH_ABBR_NAME[datetime.month], "utf-8"), datetime.year + 543)

def convert_dateid_to_date(dateid):
    return date(int(dateid[4:8]), int(dateid[2:4]), int(dateid[0:2]))

def week_elapse(date):
    current_date = date.today()
    
    days_elapse = (current_date - date).days
    weeks_elapse = 0
    
    while days_elapse >= 7:
        weeks_elapse = weeks_elapse + 1
        days_elapse = days_elapse - 7
    
    return (weeks_elapse, days_elapse)

def week_elapse_text(date):
    (weeks_elapse, days_elapse) = week_elapse(date)
    
    if weeks_elapse:
        if days_elapse:
            text = unicode('%d สัปดาห์ %d วัน', 'utf-8') % (weeks_elapse, days_elapse)
        else:
            text = unicode('%d สัปดาห์', 'utf-8') % weeks_elapse
        
    else:
        text = unicode('%d วัน', 'utf-8') % days_elapse
    
    return text

def shift_month_year(month, year, offset):
    month = month + offset
    
    while month > 12:
        month = month - 12
        year = year + 1
    
    while month < 1:
        month = month + 12
        year = year - 1
    
    return (month, year)

#
# QUARTER
#

def find_quarter_number(date):
    month_elapse = date.month - settings.QUARTER_START_MONTH
    if month_elapse < 0: month_elapse = month_elapse + 12
    return month_elapse / 3 + 1

def find_quarter(date):
    quarter = find_quarter_number(date)
    
    if settings.QUARTER_START_MONTH == 1:
        quarter_year = date.year
    else:
        if date.month >= settings.QUARTER_START_MONTH:
            if settings.QUARTER_LOWER_YEAR_NUMBER:
                quarter_year = date.year
            else:
                quarter_year = date.year + 1
        else:
            if settings.QUARTER_LOWER_YEAR_NUMBER:
                quarter_year = date.year + 1
            else:
                quarter_year = date.year
    
    return (quarter, quarter_year)

# AUTH UTILITIES
allow_password_chars = '0123456789'
random_password_length = 6
def make_random_user_password():
    from random import choice
    return ''.join([choice(allow_password_chars) for i in range(random_password_length)])

# MASTER PLAN YEAR
def master_plan_current_year():
    today = date.today()
    
    if settings.QUARTER_START_MONTH == 1:
        return today.year
    else:
        if settings.QUARTER_LOWER_YEAR_NUMBER:
            return today.year - 1
        else:
            return today.year

def master_plan_current_year_span():
    today = date.today()
    
    if settings.QUARTER_START_MONTH == 1:
        return (date(today.year, 1, 1), date(today.year, 12, 31))
    else:
        if today.month >= settings.QUARTER_START_MONTH:
            return (
                date(today.year, settings.QUARTER_START_MONTH, 1),
                date(today.year+1, settings.QUARTER_START_MONTH-1, calendar.monthrange(today.year+1, settings.QUARTER_START_MONTH-1)[1])
                )
        else:
            return (
                date(today.year-1, settings.QUARTER_START_MONTH, 1),
                date(today.year, settings.QUARTER_START_MONTH-1, calendar.monthrange(today.year, settings.QUARTER_START_MONTH-1)[1])
                )

def master_plan_year_span(year_number):
    if settings.QUARTER_START_MONTH == 1:
        return (date(year_number, 1, 1), date(year_number, 12, 31))
    else:
        if settings.QUARTER_LOWER_YEAR_NUMBER:
            return (
                date(year_number, settings.QUARTER_START_MONTH, 1),
                date(year_number+1, settings.QUARTER_START_MONTH-1, calendar.monthrange(year_number+1, settings.QUARTER_START_MONTH-1)[1])
                )
        else:
            return (
                date(year_number-1, settings.QUARTER_START_MONTH, 1),
                date(year_number, settings.QUARTER_START_MONTH-1, calendar.monthrange(year_number, settings.QUARTER_START_MONTH-1)[1])
                )
        
def master_plan_current_year_number():
    today = date.today()
    
    if settings.QUARTER_START_MONTH == 1:
        return today.year
    else:
        if today.month >= settings.QUARTER_START_MONTH:
            return today.year if settings.QUARTER_LOWER_YEAR_NUMBER else (today.year + 1)
        else:
            return (today.year - 1) if settings.QUARTER_LOWER_YEAR_NUMBER else today.year

# URL Utilities
def redirect_or_back(url_name, url_param, request):
    from django.shortcuts import redirect
    back_list = request.POST.get('back')
    
    if back_list:
        back_urls = []
        for back in back_list.split('&'):
            (text, separator, url) = back.partition('=')
            back_urls.append(url)
        
        redirect_url = back_urls[0]
        if len(back_urls) > 1:
            redirect_url = redirect_url + '?back=' + '&back='.join(back_urls[1:])
        
        return redirect(redirect_url)
    else:
        return redirect(url_name, url_param)
