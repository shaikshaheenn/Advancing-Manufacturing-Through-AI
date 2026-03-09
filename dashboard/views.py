from django.shortcuts import render, redirect
from ai_applications.models import PredictiveMaintenance, QualityControl, ProcessOptimization, SupplyChain
from technologies.models import TechnologyModule

def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required_custom
def dashboard_home(request):
    context = {
        'total_maintenance': PredictiveMaintenance.objects.count(),
        'failures_predicted': PredictiveMaintenance.objects.filter(failure_predicted=True).count(),
        'total_quality_issues': QualityControl.objects.filter(resolved=False).count(),
        'total_processes': ProcessOptimization.objects.count(),
        'total_techs': TechnologyModule.objects.filter(is_active=True).count(),
        'recent_maintenance': PredictiveMaintenance.objects.order_by('-recorded_at')[:5],
        'recent_quality': QualityControl.objects.order_by('-detected_at')[:5],
    }
    return render(request, 'dashboard/home.html', context)
