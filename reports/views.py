from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Challenge, Recommendation, Report
from .gemini_service import (
    generate_recommendation,
    analyze_challenge,
    generate_report_summary,
)


def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


@login_required_custom
def reports_home(request):
    reports = Report.objects.all()
    return render(request, 'reports/home.html', {'reports': reports})


@login_required_custom
def challenges_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'analyze':
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
                    f'Gemini AI analysis complete for "{challenge.title}"')
            else:
                messages.error(request, f'Gemini error: {analysis}')

        return redirect('reports:challenges')

    challenges = Challenge.objects.all()
    analyzed   = challenges.filter(ai_analysis__isnull=False).exclude(ai_analysis='').count()

    return render(request, 'reports/challenges.html', {
        'challenges': challenges,
        'analyzed':   analyzed,
    })


@login_required_custom
def recommendations_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'generate_ai':
            topic    = request.POST.get('topic', '').strip()
            category = request.POST.get('category', '').strip()
            context  = request.POST.get('context', '').strip()
            priority = request.POST.get('priority', 'medium')

            if not topic or not category:
                messages.error(request, 'Topic and Category are required.')
                return redirect('reports:recommendations')

            ai_content, success = generate_recommendation(topic, category, context)

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
                    f'Gemini AI generated recommendation for "{topic}"')
            else:
                messages.error(request, f'Gemini error: {ai_content}')

        elif action == 'add_manual':
            title    = request.POST.get('title', '').strip()
            category = request.POST.get('category', '').strip()
            desc     = request.POST.get('description', '').strip()
            priority = request.POST.get('priority', 'medium')

            if not title or not desc:
                messages.error(request, 'Title and Description are required.')
                return redirect('reports:recommendations')

            Recommendation.objects.create(
                title=title,
                category=category,
                description=desc,
                priority=priority,
                ai_generated=False,
            )
            messages.success(request, 'Recommendation added manually.')

        elif action == 'delete':
            Recommendation.objects.filter(pk=request.POST.get('pk')).delete()
            messages.success(request, 'Recommendation deleted.')

        return redirect('reports:recommendations')

    recommendations = Recommendation.objects.all()
    ai_count        = recommendations.filter(ai_generated=True).count()
    manual_count    = recommendations.filter(ai_generated=False).count()
    high_priority   = recommendations.filter(priority='high').count()

    return render(request, 'reports/recommendations.html', {
        'recommendations': recommendations,
        'ai_count':        ai_count,
        'manual_count':    manual_count,
        'high_priority':   high_priority,
    })
