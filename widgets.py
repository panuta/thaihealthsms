from datetime import date

from django.conf import settings
from django.forms.widgets import Input
from django.utils import datetime_safe
from django.utils.dateformat import format
from django.utils.safestring import mark_safe

class YUICalendar(Input):
    input_type = 'text'
    format = '%Y-%m-%d'

    def __init__(self, attrs=None):
        self.attrs = attrs
	
    def _format_value(self, value):
        if value is None:
            return ''
        elif hasattr(value, 'strftime'):
            value = datetime_safe.new_date(value)
            return value.strftime(self.format)
        return value
    
    def render(self, name, value, attrs=None):
        input_id = self.attrs.get('id', 'date_picker') if self.attrs else 'date_picker'
        
        if not value:
            display_value = ''
            value = ''
        else:
            if type(value).__name__ == 'unicode':
                (year, month, day) = value.split('-')
                value = date(int(year), int(month), int(day))
            
            display_value = '%s %s' % (format(value, 'j F'), (value.year+543))
            value = '%d-%d-%d' % (value.year, value.month, value.day)
        
        value_input = '<input type="hidden" name="%s" value="%s" id="%s_value"/>' % (name, value, input_id)
        display_input = '<input type="text" value="%s" id="%s_display" readonly="readonly" class="yui_date_picker_textbox"/>' % (display_value, input_id)
        calendar_icon = '<img src="%s/images/icons/date_picker.png" id="%s" class="yui_date_picker"/>' % (settings.MEDIA_URL, input_id)
        
        return mark_safe(u'<span class="yui_date_picker_panel">%s%s %s</span>' % (value_input, display_input, calendar_icon))
    
    def _has_changed(self, initial, data):
        return super(YUICalendar, self)._has_changed(self._format_value(initial), data)
    
    class Media:
        css = {
            'all': (
                settings.MEDIA_URL + '/yui/build/container/assets/skins/sam/container.css',
                settings.MEDIA_URL + '/yui/build/calendar/assets/skins/sam/calendar.css',
                settings.MEDIA_URL + '/css/yui.calendar.widget.css',
            ),
        }
        js = (
            settings.MEDIA_URL + '/yui/build/yahoo-dom-event/yahoo-dom-event.js',
            settings.MEDIA_URL + '/yui/build/element/element-min.js',
            settings.MEDIA_URL + '/yui/build/container/container-min.js',
            settings.MEDIA_URL + '/yui/build/calendar/calendar-min.js',
            settings.MEDIA_URL + '/scripts/yui.calendar.widget.js',
        )
