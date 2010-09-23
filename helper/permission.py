from accounts.models import UserRoleResponsibility, UserPermission, AdminPermission
from domain.models import SectorMasterPlan

def access_obj(user, permissions, obj, at_least_one_permission=True):
    """
    If 'at_least_one_permission' is True, return True if one of permissions is meet
    If 'at_least_one_permission' is False, return True if every permission is meet 
    """
    
    if type(permissions).__name__ in ('str', 'unicode'):
        permissions = [permissions]
    else:
        permissions = list(permissions)
    
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
                        if type(obj).__name__ == 'Sector':
                            if obj in responsibility.sectors.all():
                                has_access = True
                            
                        elif type(obj).__name__ == 'MasterPlan':
                            if SectorMasterPlan.objects.filter(sector__in=responsibility.sectors.all(), master_plan=obj).count() > 0:
                                has_access = True
                        
                        elif type(obj).__name__ == 'Program':
                            if responsibility.role.name == 'sector_manager':
                                obj_sectors = [smp.sector for smp in SectorMasterPlan.objects.filter(master_plan=obj.plan.master_plan)]
                                if set(obj_sectors).intersection(set(responsibility.sectors.all())):
                                    has_access = True
                            else:
                                if obj in responsibility.programs.all():
                                    has_access = True
                        
                        elif type(obj).__name__ == 'ReportSubmission':
                            if responsibility.role.name == 'sector_manager':
                                obj_sectors = [smp.sector for smp in SectorMasterPlan.objects.filter(master_plan=obj.program.plan.master_plan)]
                                if set(obj_sectors).intersection(set(responsibility.sectors.all())):
                                    has_access = True
                            else:
                                if obj.program in responsibility.programs.all():
                                    has_access = True
                        
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

def has_roles(user, roles):
    user_groups = user.groups.all()
    roles = roles.split(',')
    
    if user_groups:
        user_roles = set([group.name for group in user_groups])
        roles = set(roles)
        
        if user_roles.intersection(roles): return True
        
    return False

def has_role_with_obj(user, roles, obj):
    if type(roles).__name__ in ('str', 'unicode'):
        roles = [roles]
    else:
        roles = list(roles)
    
    if user.is_superuser: return False
    
    has_access = False
    for responsibility in UserRoleResponsibility.objects.filter(user=user.get_profile()):
        if responsibility.role in roles:
            if type(obj).__name__ == 'Sector':
                if obj in responsibility.sectors.all():
                    has_access = True
                
            elif type(obj).__name__ == 'MasterPlan':
                if SectorMasterPlan.objects.filter(sector__in=responsibility.sectors.all(), master_plan=obj).count() > 0:
                    has_access = True
                    
            elif type(obj).__name__ == 'Program':
                if responsibility.role.name == 'sector_manager':
                    obj_sectors = [smp.sector for smp in SectorMasterPlan.objects.filter(master_plan=obj.plan.master_plan)]
                    if set(obj_sectors).intersection(set(responsibility.sectors.all())):
                        has_access = True
                else:
                    if obj in responsibility.programs.all():
                        has_access = True
    
    return has_access

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