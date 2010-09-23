from django.shortcuts import render_to_response
from django.template import RequestContext

def render_response(request, *args, **kwargs):
	first_time_login = request.session.get('first_time_login', False)
	kwargs['context_instance'] = RequestContext(request, {'first_time_login':first_time_login})
	return render_to_response(*args, **kwargs)

def render_page_response(request, page, *args, **kwargs):
	first_time_login = request.session.get('first_time_login', False)
	kwargs['context_instance'] = RequestContext(request, {'page':page, 'first_time_login':first_time_login})
	return render_to_response(*args, **kwargs)

def access_denied(request):
	return render_response(request, 'access_denied.html')