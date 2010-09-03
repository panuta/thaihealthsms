from accounts.models import UserRoleResponsibility, UserPermission, AdminPermission
from domain.models import SectorMasterPlan

def access_obj(user, permissions, obj, at_least_one_permission=True):
    """
    If 'at_least_one_permission' is True, return True if one of permissions is meet
    If 'at_least_one_permission' is False, return True if every permission is meet 
    """
    
    if type(permissions).__name__ in ('str', 'unicode'):
        permissions = [permissions]
    
    if user.is_superuser:
        checked_permission_count = 0
        for permission in permissions:
            try:
                AdminPermission.objects.get(permission=permission)
                checked_permission_count = checked_permission_count + 1
            except AdminPermission.DoesNotExist:
                pass
        
        if at_least_one_permission:
            return checked_permission_count > 0
        else:
            return len(permissions) == checked_permission_count
    
    else:
        passed_permissions = []
        
        for responsibility in UserRoleResponsibility.objects.filter(user=user.get_profile()):
            
            for permission in permissions:
                has_access = False
                
                try:
                    user_permission = UserPermission.objects.get(role=responsibility.role, permission=permission)
                    
                    if not user_permission.only_responsible:
                        has_access = True
                    else:
                        has_responsibility = False
                        
                        if type(obj).__name__ == 'Sector':
                            if obj in responsibility.sectors.all():
                                has_responsibility = True
                            
                            if user.get_profile().sector.id == obj.id:
                                has_responsibility = True
                                
                        elif type(obj).__name__ == 'MasterPlan':
                            has_responsibility = SectorMasterPlan.objects.filter(sector__in=responsibility.sectors.all(), master_plan=obj).count() > 0
                            
                        elif type(obj).__name__ == 'Project':
                            if obj in responsibility.projects.all():
                                has_responsibility = True
                        
                        if has_responsibility:
                            has_access = has_responsibility
                except:
                    pass
                
                if has_access:
                    passed_permissions.append(permission)
            
            for permission in passed_permissions:
                try:
                    permissions.remove(permission)
                except: # Permission is already removed
                    pass
        
        if at_least_one_permission:
            return len(passed_permissions) > 0
        else:
            return len(permissions) == 0

def role_access(user, roles):
    user_groups = user.groups.all()
    roles = roles.split(',')
    
    if user_groups:
        user_roles = set([group.name for group in user_groups])
        roles = set(roles)
        
        if user_roles.intersection(roles): return True
        
    return False

def who_program_manager(program):
    if program.manager_name:
        return program.manager_name
    else:
        responsibility = UserRoleResponsibility.objects.filter(role__name='program_manager', programs__in=(program,))
        
        if responsibility:
            names = ''
            for user in responsibility:
                if names: names = names + ', '
                names = names + user.user.firstname + ' ' + user.user.lastname
            return names
        else:
            return ''