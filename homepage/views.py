from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from accounts.models import UserRoleResponsibility

from helper.shortcuts import render_response

def view_homepage(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/login/')
    else:
        roles = request.user.groups.all()
        if roles:
            responsibilities = UserRoleResponsibility.objects.get(user=request.user.get_profile())
            return render_response(request, 'page_user/user_dashboard.html', {'responsibilities':responsibilities, 'roles':roles})
        
        if request.user.is_superuser:
            return redirect('view_administration')
        
        raise Http404