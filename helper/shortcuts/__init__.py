from django.shortcuts import render_to_response
from django.template import RequestContext

def render_response(request, *args, **kwargs):
	kwargs['context_instance'] = RequestContext(request)
	return render_to_response(*args, **kwargs)

def render_page_response(request, page, *args, **kwargs):
	kwargs['context_instance'] = RequestContext(request, {'page':page})
	return render_to_response(*args, **kwargs)

def access_denied(request):
	return render_response(request, 'access_denied.html')