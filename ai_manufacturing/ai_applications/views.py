from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import PredictiveMaintenance, QualityControl, ProcessOptimization, SupplyChain
import joblib, os, tempfile
import numpy as np

# ─── Auth decorator ─────────────────────────────────────────
def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ─── AI: Process Recommendation Engine ──────────────────────
def generate_ai_recommendation(process_name, eff_before, eff_after):
    improvement = ((eff_after - eff_before) / eff_before) * 100
    suggestions = []

    if eff_before < 50:
        suggestions.append("Critical efficiency level. Immediate process redesign and root-cause analysis required.")
    elif eff_before < 65:
        suggestions.append("Low efficiency detected. Apply lean manufacturing and eliminate top 3 waste categories.")
    elif eff_before < 75:
        suggestions.append("Below-average efficiency. Deploy real-time IoT monitoring to identify hidden bottlenecks.")

    if improvement < 0:
        suggestions.append("Efficiency declined — review recent changes and roll back last process modification.")
    elif improvement < 5:
        suggestions.append("Marginal gain only. Consider deploying edge AI for real-time adaptive parameter tuning.")
    elif improvement < 15:
        suggestions.append("Moderate improvement achieved. Continue monitoring — further gains likely with predictive scheduling.")
    elif improvement >= 15:
        suggestions.append("Strong improvement. Document process parameters and replicate across similar production lines.")
    elif improvement >= 25:
        suggestions.append("Exceptional gain. Standardize this process immediately as a company-wide best practice.")

    name_lower = process_name.lower()
    if 'weld' in name_lower:
        suggestions.append("Welding line: AI vision inspection can further reduce defect rates by 15-30%.")
    if 'assembly' in name_lower:
        suggestions.append("Assembly process: Cobot integration recommended to boost throughput by 20-40%.")
    if 'paint' in name_lower or 'coat' in name_lower:
        suggestions.append("Coating/painting: AI spray control reduces material waste by up to 25%.")
    if 'cut' in name_lower or 'machine' in name_lower:
        suggestions.append("Machining: Predictive tool-wear monitoring can prevent 80% of unplanned downtime.")
    if 'pack' in name_lower:
        suggestions.append("Packaging: Computer vision quality checks at line-end reduce customer returns significantly.")
    if 'quality' in name_lower or 'inspect' in name_lower:
        suggestions.append("Inspection: Upgrade to AI-powered optical inspection for 100% coverage vs manual sampling.")

    if not suggestions:
        suggestions.append("Continuously monitor KPIs. Integrate IoT sensors for deeper real-time insights.")

    return " ".join(suggestions)


# ─── AI: Supply Chain Insight Generator ─────────────────────
def generate_supply_insight(supplier_name, component, delivery_days,
                            risk_level, price_volatility, past_delays, distance_km):
    insights = []

    if risk_level == 'high':
        insights.append(f"HIGH RISK ALERT: {supplier_name} poses significant supply disruption risk.")
        insights.append("Immediately identify and qualify 2-3 alternative suppliers for this component.")
    elif risk_level == 'medium':
        insights.append(f"MEDIUM RISK: {supplier_name} requires close monitoring and contingency planning.")
        insights.append("Maintain 4-6 weeks safety stock for this component.")
    else:
        insights.append(f"LOW RISK: {supplier_name} is a reliable supplier.")
        insights.append("Continue standard monitoring with quarterly performance reviews.")

    if delivery_days > 45:
        insights.append(f"Delivery time of {delivery_days} days is critically high — consider air freight for urgent orders.")
    elif delivery_days > 30:
        insights.append(f"Delivery time of {delivery_days} days exceeds optimal threshold of 30 days.")
    elif delivery_days <= 7:
        insights.append(f"Excellent delivery time of {delivery_days} days supports just-in-time manufacturing.")

    if past_delays > 5:
        insights.append(f"Supplier has {past_delays} recorded delays — initiate supplier improvement program.")
    if price_volatility > 0.7:
        insights.append("High price volatility detected — negotiate long-term fixed-price contracts.")
    if distance_km > 3000:
        insights.append(f"Distance of {distance_km}km creates geopolitical and logistics risk — explore nearshoring.")

    return " ".join(insights)


# ─── VIEWS ──────────────────────────────────────────────────

@login_required_custom
def ai_home(request):
    return render(request, 'ai_applications/home.html')


@login_required_custom
def predictive_maintenance(request):
    prediction_result = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'predict':
            try:
                machine_id    = request.POST.get('machine_id', 'M001').strip()
                temperature   = float(request.POST.get('temperature'))
                vibration     = float(request.POST.get('vibration'))
                pressure      = float(request.POST.get('pressure'))
                runtime       = float(request.POST.get('runtime_hours'))

                model_path = os.path.join('ai_models', 'maintenance_model.pkl')
                if os.path.exists(model_path):
                    model    = joblib.load(model_path)
                    features = np.array([[temperature, vibration, pressure, runtime]])
                    pred     = model.predict(features)[0]
                    score    = float(model.predict_proba(features)[0][1])

                    # Feature importance insight
                    importances = model.feature_importances_
                    feat_names  = ['Temperature', 'Vibration', 'Pressure', 'Runtime Hours']
                    top_feature = feat_names[int(np.argmax(importances))]

                    prediction_result = {
                        'failure':      bool(pred),
                        'score':        round(score * 100, 2),
                        'machine_id':   machine_id,
                        'top_factor':   top_feature,
                        'temperature':  temperature,
                        'vibration':    vibration,
                        'pressure':     pressure,
                        'runtime':      runtime,
                    }

                    PredictiveMaintenance.objects.create(
                        machine_id=machine_id,
                        temperature=temperature,
                        vibration=vibration,
                        pressure=pressure,
                        runtime_hours=runtime,
                        failure_predicted=bool(pred),
                        prediction_score=score
                    )
                    status = "⚠ FAILURE RISK" if pred else "✓ HEALTHY"
                    messages.success(request, f'Machine {machine_id}: {status} — Risk Score: {round(score*100,2)}%')
                else:
                    messages.error(request, '❌ ML model not found. Run: python ai_models/train_model.py')

            except ValueError as e:
                messages.error(request, f'Invalid input: {e}')
            except Exception as e:
                messages.error(request, f'Prediction error: {e}')

        elif action == 'delete':
            PredictiveMaintenance.objects.filter(pk=request.POST.get('pk')).delete()
            messages.success(request, 'Record deleted.')
            return redirect('ai_applications:predictive')

    records       = PredictiveMaintenance.objects.all()
    failure_count = records.filter(failure_predicted=True).count()
    healthy_count = records.filter(failure_predicted=False).count()
    avg_score     = 0
    if records.exists():
        avg_score = round(sum(r.prediction_score for r in records) / records.count() * 100, 1)

    return render(request, 'ai_applications/predictive.html', {
        'prediction_result': prediction_result,
        'records':           records[:15],
        'failure_count':     failure_count,
        'healthy_count':     healthy_count,
        'avg_score':         avg_score,
    })


@login_required_custom
def quality_control(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            product_id  = request.POST.get('product_id', '').strip()
            defect_type = request.POST.get('defect_type', '').strip()
            severity    = request.POST.get('severity', 'low')
            image       = request.FILES.get('image')
            ai_detected   = False
            ai_confidence = 0.0

            if image:
                try:
                    import torch
                    import torch.nn as nn
                    from torchvision import transforms, models as tv_models
                    from PIL import Image as PILImage

                    weights_path = os.path.join('ai_models', 'quality_resnet.pth')

                    model = tv_models.resnet18(weights=None)
                    model.fc = nn.Linear(model.fc.in_features, 3)

                    if os.path.exists(weights_path):
                        model.load_state_dict(
                            torch.load(weights_path, map_location='cpu')
                        )
                        model.eval()

                        transform = transforms.Compose([
                            transforms.Resize((224, 224)),
                            transforms.ToTensor(),
                            transforms.Normalize(
                                [0.485, 0.456, 0.406],
                                [0.229, 0.224, 0.225]
                            )
                        ])

                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
                            for chunk in image.chunks():
                                f.write(chunk)
                            tmp_path = f.name

                        img    = PILImage.open(tmp_path).convert('RGB')
                        tensor = transform(img).unsqueeze(0)

                        with torch.no_grad():
                            output = model(tensor)
                            probs  = torch.softmax(output, dim=1)
                            pred   = torch.argmax(probs).item()

                        os.unlink(tmp_path)
                        labels        = ['low', 'medium', 'high']
                        severity      = labels[pred]
                        ai_confidence = round(float(probs[0][pred]) * 100, 2)
                        ai_detected   = True
                        messages.success(request,
                            f'AI detected severity: {severity.upper()} ({ai_confidence}% confidence)')
                    else:
                        messages.warning(request,
                            'AI quality model not trained yet. Using manual severity.')
                except ImportError:
                    messages.warning(request,
                        'PyTorch not installed. Using manual severity. Run: pip install torch torchvision')
                except Exception as e:
                    messages.warning(request, f'AI detection failed ({e}). Using manual severity.')

                # Re-open file for saving (already read above)
                image.seek(0)

            QualityControl.objects.create(
                product_id=product_id,
                defect_type=defect_type,
                severity=severity,
                image=image,
                ai_confidence=ai_confidence,
                ai_detected=ai_detected,
            )
            if not ai_detected:
                messages.success(request, 'Quality issue recorded successfully.')

        elif action == 'resolve':
            issue          = get_object_or_404(QualityControl, pk=request.POST.get('pk'))
            issue.resolved = True
            issue.save()
            messages.success(request, f'Issue for {issue.product_id} marked as resolved.')

        elif action == 'delete':
            QualityControl.objects.filter(pk=request.POST.get('pk')).delete()
            messages.success(request, 'Record deleted.')

        return redirect('ai_applications:quality')

    issues         = QualityControl.objects.all()
    open_issues    = issues.filter(resolved=False).count()
    resolved_count = issues.filter(resolved=True).count()
    high_severity  = issues.filter(severity='high', resolved=False).count()
    ai_detected    = issues.filter(ai_detected=True).count()

    return render(request, 'ai_applications/quality.html', {
        'issues':          issues,
        'open_issues':     open_issues,
        'resolved_issues': resolved_count,
        'high_severity':   high_severity,
        'ai_detected':     ai_detected,
    })


@login_required_custom
def process_optimization(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            try:
                process_name = request.POST.get('process_name', '').strip()
                eff_before   = float(request.POST.get('efficiency_before'))
                eff_after    = float(request.POST.get('efficiency_after'))

                if eff_before <= 0 or eff_after <= 0:
                    raise ValueError("Efficiency values must be positive.")

                improvement = round(((eff_after - eff_before) / eff_before) * 100, 2)

                # AI generates recommendation automatically
                ai_rec = generate_ai_recommendation(process_name, eff_before, eff_after)

                ProcessOptimization.objects.create(
                    process_name=process_name,
                    efficiency_before=eff_before,
                    efficiency_after=eff_after,
                    improvement_percent=improvement,
                    ai_recommendation=ai_rec,
                )
                messages.success(request,
                    f'Process added. AI Recommendation generated. Efficiency Gain: +{improvement}%')

            except ValueError as e:
                messages.error(request, f'Invalid input: {e}')

        elif action == 'delete':
            ProcessOptimization.objects.filter(pk=request.POST.get('pk')).delete()
            messages.success(request, 'Record deleted.')

        return redirect('ai_applications:process')

    processes      = ProcessOptimization.objects.all()
    avg_improvement = 0
    best_process    = None
    if processes.exists():
        avg_improvement = round(
            sum(p.improvement_percent for p in processes) / processes.count(), 2
        )
        best_process = processes.order_by('-improvement_percent').first()

    return render(request, 'ai_applications/process.html', {
        'processes':       processes,
        'avg_improvement': avg_improvement,
        'total_processes': processes.count(),
        'best_process':    best_process,
    })


@login_required_custom
def supply_chain(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            try:
                supplier_name    = request.POST.get('supplier_name', '').strip()
                component        = request.POST.get('component', '').strip()
                delivery_days    = int(request.POST.get('delivery_days'))
                price_volatility = float(request.POST.get('price_volatility', 0.5))
                past_delays      = int(request.POST.get('past_delays', 0))
                distance_km      = int(request.POST.get('distance_km', 500))
                defect_rate      = float(request.POST.get('defect_rate', 0.02))

                # AI predicts risk level
                ai_predicted = False
                risk_level   = 'low'
                model_path   = os.path.join('ai_models', 'supply_model.pkl')
                le_path      = os.path.join('ai_models', 'supply_label_encoder.pkl')

                if os.path.exists(model_path) and os.path.exists(le_path):
                    sc_model = joblib.load(model_path)
                    le       = joblib.load(le_path)
                    features = np.array([[
                        delivery_days, price_volatility,
                        past_delays, distance_km, defect_rate
                    ]])
                    pred       = sc_model.predict(features)[0]
                    risk_level = le.inverse_transform([pred])[0]
                    ai_predicted = True
                    messages.success(request,
                        f'AI predicted risk level: {risk_level.upper()} for {supplier_name}')
                else:
                    risk_level = request.POST.get('risk_level', 'low')
                    messages.warning(request,
                        'Supply model not trained. Using manual risk. Run: python ai_models/train_supply_model.py')

                # AI generates insight text automatically
                ai_insight = generate_supply_insight(
                    supplier_name, component, delivery_days,
                    risk_level, price_volatility, past_delays, distance_km
                )

                SupplyChain.objects.create(
                    supplier_name=supplier_name,
                    component=component,
                    delivery_days=delivery_days,
                    price_volatility=price_volatility,
                    past_delays=past_delays,
                    distance_km=distance_km,
                    defect_rate=defect_rate,
                    risk_level=risk_level,
                    ai_insight=ai_insight,
                    ai_predicted=ai_predicted,
                )

            except ValueError as e:
                messages.error(request, f'Invalid input: {e}')

        elif action == 'delete':
            SupplyChain.objects.filter(pk=request.POST.get('pk')).delete()
            messages.success(request, 'Supplier record deleted.')

        return redirect('ai_applications:supply_chain')

    items      = SupplyChain.objects.all()
    high_risk  = items.filter(risk_level='high').count()
    medium_risk= items.filter(risk_level='medium').count()
    low_risk   = items.filter(risk_level='low').count()
    ai_auto    = items.filter(ai_predicted=True).count()

    return render(request, 'ai_applications/supply_chain.html', {
        'items':       items,
        'high_risk':   high_risk,
        'medium_risk': medium_risk,
        'low_risk':    low_risk,
        'ai_auto':     ai_auto,
    })
