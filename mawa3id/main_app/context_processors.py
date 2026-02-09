from .models import Profile

def user_role(request):
    role = None
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        if profile:
            role = profile.role
    return {"user_role": role}
