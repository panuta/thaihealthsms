# -*- encoding: utf-8 -*-
from django.conf import settings

import calendar
from datetime import date

from constants import *

def format_full_datetime(datetime):
    return unicode('%d %s %d เวลา %02d:%02d น.', 'utf-8') % (datetime.day, unicode(THAI_MONTH_NAME[datetime.month], 'utf-8'), datetime.year + 543, datetime.hour, datetime.minute)

def format_abbr_datetime(datetime):
    return unicode('%d %s %d เวลา %02d:%02d น.', 'utf-8') % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], 'utf-8'), datetime.year + 543, datetime.hour, datetime.minute)

def format_full_date(datetime):
    return unicode('%d %s %d', 'utf-8') % (datetime.day, unicode(THAI_MONTH_NAME[datetime.month], 'utf-8'), datetime.year + 543)

def format_abbr_date(datetime):
    return unicode('%d %s %d', 'utf-8') % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], 'utf-8'), datetime.year + 543)

def format_full_month_year(datetime):
    return "%s %d" % (unicode(THAI_MONTH_NAME[datetime.month], "utf-8"), datetime.year + 543)

def format_abbr_month_year(datetime):
    return "%s %d" % (unicode(THAI_MONTH_ABBR_NAME[datetime.month], "utf-8"), datetime.year + 543)

# QUARTER
def find_quarter_number(date):
    month_elapse = date.month - settings.QUARTER_START_MONTH
    if month_elapse < 0: month_elapse = month_elapse + 12
    return month_elapse / 3 + 1

# AUTH UTILITIES
allow_password_chars = '0123456789'
random_password_length = 6
def make_random_user_password():
    from random import choice
    return ''.join([choice(allow_password_chars) for i in range(random_password_length)])

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