from django.shortcuts import render, redirect, get_object_or_404
from .models import TechnologyModule

def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required_custom
def tech_home(request):
    tech_type = request.GET.get('type', '')
    techs = TechnologyModule.objects.filter(is_active=True)
    if tech_type:
        techs = techs.filter(tech_type=tech_type)
    return render(request, 'technologies/home.html', {'techs': techs, 'tech_type': tech_type})

@login_required_custom
def tech_detail(request, pk):
    tech = get_object_or_404(TechnologyModule, pk=pk)
    return render(request, 'technologies/detail.html', {'tech': tech})
