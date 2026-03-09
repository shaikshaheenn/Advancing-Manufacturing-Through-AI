from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from accounts.models import UserProfile
from ai_applications.models import (
    PredictiveMaintenance,
    QualityControl,
    ProcessOptimization,
    SupplyChain,
)
from technologies.models import TechnologyModule
from reports.models import Report, Recommendation, Challenge
from reports.gemini_service import (
    generate_recommendation,
    analyze_challenge,
    generate_report_summary,
    generate_manufacturing_insights,
)


# ─── Admin Auth Decorator ─────────────────────────────────────────────────────
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, 'Please login to continue.')
            return redirect('accounts:login')
        if request.session.get('user_role') != 'admin':
            messages.error(request, 'Admin access required.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ─── Admin Dashboard ──────────────────────────────────────────────────────────
@admin_required
def admin_dashboard(request):
    maintenance_records = PredictiveMaintenance.objects.all()
    quality_records     = QualityControl.objects.all()
    process_records     = ProcessOptimization.objects.all()

    failure_count   = maintenance_records.filter(failure_predicted=True).count()
    quality_issues  = quality_records.filter(resolved=False).count()
    high_severity   = quality_records.filter(severity='high', resolved=False).count()
    high_risk_sup   = SupplyChain.objects.filter(risk_level='high').count()
    avg_improvement = 0
    if process_records.exists():
        avg_improvement = round(
            sum(p.improvement_percent for p in process_records) / process_records.count(), 1
        )

    # Gemini Live Insights
    stats = {
        'total_machines':      maintenance_records.count(),
        'failure_count':       failure_count,
        'quality_issues':      quality_issues,
        'high_severity':       high_severity,
        'high_risk_suppliers': high_risk_sup,
        'total_processes':     process_records.count(),
        'avg_improvement':     avg_improvement,
    }
    gemini_insights, insights_ok = generate_manufacturing_insights(stats)

    context = {
        'total_users':        UserProfile.objects.filter(role='industry_user').count(),
        'active_users':       UserProfile.objects.filter(role='industry_user', is_active=True).count(),
        'total_reports':      Report.objects.count(),
        'total_maintenance':  maintenance_records.count(),
        'failure_count':      failure_count,
        'quality_issues':     quality_issues,
        'high_severity':      high_severity,
        'total_processes':    process_records.count(),
        'avg_improvement':    avg_improvement,
        'total_supply':       SupplyChain.objects.count(),
        'high_risk_sup':      high_risk_sup,
        'total_techs':        TechnologyModule.objects.count(),
        'total_challenges':   Challenge.objects.count(),
        'total_recs':         Recommendation.objects.count(),
        'gemini_insights':    gemini_insights,
        'insights_ok':        insights_ok,
        'recent_users':       UserProfile.objects.filter(
                                  role='industry_user'
                              ).order_by('-created_at')[:5],
        'recent_maintenance': maintenance_records.order_by('-recorded_at')[:5],
    }
    return render(request, 'adminpanel/dashboard.html', context)


# ─── User Management ──────────────────────────────────────────────────────────
@admin_required
def manage_users(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        pk     = request.POST.get('pk')
        user   = get_object_or_404(UserProfile, pk=pk)

        if action == 'toggle':
            user.is_active = not user.is_active
            user.save()
            status = 'activated' if user.is_active else 'deactivated'
            messages.success(request, f'User "{user.full_name}" has been {status}.')

        elif action == 'delete':
            name = user.full_name
            user.delete()
            messages.success(request, f'User "{name}" deleted permanently.')

        return redirect('adminpanel:users')

    users = UserProfile.objects.filter(role='industry_user').order_by('-created_at')
    return render(request, 'adminpanel/users.html', {'users': users})


# ─── Content Management ───────────────────────────────────────────────────────
@admin_required
def manage_content(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        # ── Challenges ─────────────────────────────────────────────────────
        if action == 'add_challenge':
            title         = request.POST.get('title', '').strip()
            industry_area = request.POST.get('industry_area', '').strip()
            description   = request.POST.get('description', '').strip()
            ai_solution   = request.POST.get('ai_solution', '').strip()
            severity      = request.POST.get('severity', 'medium')

            if not title or not description:
                messages.error(request, 'Title and Description are required.')
                return redirect('adminpanel:content')

            ai_analysis = None
            if request.POST.get('gemini_analyze') == 'on':
                ai_analysis, success = analyze_challenge(
                    title, description, industry_area
                )
                if success:
                    messages.success(request,
                        f'Gemini analyzed challenge: "{title}"')
                else:
                    messages.warning(request,
                        'Gemini unavailable. Saved without AI analysis.')
                    ai_analysis = None

            Challenge.objects.create(
                title=title,
                industry_area=industry_area,
                description=description,
                ai_solution=ai_solution,
                severity=severity,
                ai_analysis=ai_analysis,
            )
            if not ai_analysis and request.POST.get('gemini_analyze') != 'on':
                messages.success(request, f'Challenge "{title}" added.')

        elif action == 'analyze_challenge':
            pk        = request.POST.get('pk')
            challenge = get_object_or_404(Challenge, pk=pk)
            analysis, success = analyze_challenge(
                challenge.title,
                challenge.description,
                challenge.industry_area
            )
            if success:
                challenge.ai_analysis = analysis
                challenge.save()
                messages.success(request,
                    f'Gemini analysis complete for "{challenge.title}"')
            else:
                messages.error(request, f'Gemini error: {analysis}')

        elif action == 'delete_challenge':
            ch   = get_object_or_404(Challenge, pk=request.POST.get('pk'))
            name = ch.title
            ch.delete()
            messages.success(request, f'Challenge "{name}" deleted.')

        # ── Recommendations ────────────────────────────────────────────────
        elif action == 'add_recommendation':
            title    = request.POST.get('title', '').strip()
            category = request.POST.get('category', '').strip()
            desc     = request.POST.get('description', '').strip()
            priority = request.POST.get('priority', 'medium')

            if not title or not desc:
                messages.error(request, 'Title and Description are required.')
                return redirect('adminpanel:content')

            Recommendation.objects.create(
                title=title,
                category=category,
                description=desc,
                priority=priority,
                ai_generated=False,
            )
            messages.success(request, f'Recommendation "{title}" added.')

        elif action == 'generate_ai_recommendation':
            topic    = request.POST.get('ai_topic', '').strip()
            category = request.POST.get('ai_category', '').strip()
            priority = request.POST.get('ai_priority', 'medium')

            if not topic:
                messages.error(request, 'Topic is required.')
                return redirect('adminpanel:content')

            ai_content, success = generate_recommendation(topic, category)
            if success:
                Recommendation.objects.create(
                    title=topic,
                    category=category,
                    description=ai_content,
                    priority=priority,
                    ai_generated=True,
                    gemini_response=ai_content,
                )
                messages.success(request,
                    f'Gemini generated recommendation: "{topic}"')
            else:
                messages.error(request, f'Gemini error: {ai_content}')

        elif action == 'delete_recommendation':
            rec  = get_object_or_404(Recommendation, pk=request.POST.get('pk'))
            name = rec.title
            rec.delete()
            messages.success(request, f'Recommendation "{name}" deleted.')

        # ── Technologies ───────────────────────────────────────────────────
        elif action == 'add_tech':
            title     = request.POST.get('title', '').strip()
            tech_type = request.POST.get('tech_type', 'xai')
            desc      = request.POST.get('description', '').strip()
            benefits  = request.POST.get('benefits', '').strip()
            use_cases = request.POST.get('use_cases', '').strip()

            if not title or not desc:
                messages.error(request, 'Title and Description are required.')
                return redirect('adminpanel:content')

            TechnologyModule.objects.create(
                title=title,
                tech_type=tech_type,
                description=desc,
                benefits=benefits,
                use_cases=use_cases,
            )
            messages.success(request, f'Technology module "{title}" added.')

        elif action == 'delete_tech':
            tech = get_object_or_404(TechnologyModule, pk=request.POST.get('pk'))
            name = tech.title
            tech.delete()
            messages.success(request, f'Technology module "{name}" deleted.')

        else:
            messages.warning(request, 'Unknown action.')

        return redirect('adminpanel:content')

    return render(request, 'adminpanel/content.html', {
        'challenges':      Challenge.objects.all(),
        'recommendations': Recommendation.objects.all(),
        'techs':           TechnologyModule.objects.all(),
    })


# ─── Reports ──────────────────────────────────────────────────────────────────
@admin_required
def admin_reports(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'generate':
            title       = request.POST.get('title', '').strip()
            content     = request.POST.get('content', '').strip()
            report_type = request.POST.get('report_type', 'Performance')

            if not title or not content:
                messages.error(request, 'Title and Content are required.')
                return redirect('adminpanel:reports')

            ai_summary, success = generate_report_summary(title, content, report_type)
            if not success:
                ai_summary = None
                messages.warning(request,
                    'Report saved. Gemini summary unavailable — check API key.')

            Report.objects.create(
                title=title,
                content=content,
                generated_by=request.session.get('user_name', 'Admin'),
                report_type=report_type,
                ai_summary=ai_summary,
            )
            if success:
                messages.success(request,
                    f'Report "{title}" saved with Gemini AI executive summary!')

        elif action == 'delete':
            report = get_object_or_404(Report, pk=request.POST.get('pk'))
            name   = report.title
            report.delete()
            messages.success(request, f'Report "{name}" deleted.')

        return redirect('adminpanel:reports')

    reports = Report.objects.all()
    return render(request, 'adminpanel/reports.html', {'reports': reports})


# ─── System Monitoring ────────────────────────────────────────────────────────
@admin_required
def system_monitoring(request):
    maintenance = PredictiveMaintenance.objects.all()
    quality     = QualityControl.objects.all()

    context = {
        'db_status':           'Online',
        'server_time':         timezone.now(),
        # User stats — only industry_user role
        'total_users':         UserProfile.objects.filter(role='industry_user').count(),
        'active_users':        UserProfile.objects.filter(
                                   role='industry_user', is_active=True
                               ).count(),
        'inactive_users':      UserProfile.objects.filter(
                                   role='industry_user', is_active=False
                               ).count(),
        # AI Application stats
        'total_maintenance':   maintenance.count(),
        'failure_count':       maintenance.filter(failure_predicted=True).count(),
        'healthy_count':       maintenance.filter(failure_predicted=False).count(),
        'total_quality':       quality.count(),
        'open_quality':        quality.filter(resolved=False).count(),
        'resolved_quality':    quality.filter(resolved=True).count(),
        'ai_detected_q':       quality.filter(ai_detected=True).count(),
        'total_process':       ProcessOptimization.objects.count(),
        'total_supply':        SupplyChain.objects.count(),
        'high_risk_supply':    SupplyChain.objects.filter(risk_level='high').count(),
        'ai_supply':           SupplyChain.objects.filter(ai_predicted=True).count(),
        # Content stats
        'total_techs':         TechnologyModule.objects.count(),
        'total_challenges':    Challenge.objects.count(),
        'analyzed_challenges': Challenge.objects.exclude(
                                   ai_analysis=None
                               ).exclude(ai_analysis='').count(),
        'total_recs':          Recommendation.objects.count(),
        'ai_recs':             Recommendation.objects.filter(ai_generated=True).count(),
        'total_reports':       Report.objects.count(),
        'ai_reports':          Report.objects.exclude(
                                   ai_summary=None
                               ).exclude(ai_summary='').count(),
    }
    return render(request, 'adminpanel/monitoring.html', context)
