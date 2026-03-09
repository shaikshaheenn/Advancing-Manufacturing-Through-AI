import os
import django
import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_manufacturing.settings')
django.setup()

from accounts.models import UserProfile
from technologies.models import TechnologyModule
from reports.models import Challenge, Recommendation


def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def seed():
    print("Seeding database...")

    # ── Users ─────────────────────────────────────────────────────────────
    UserProfile.objects.all().delete()

    UserProfile.objects.create(
        full_name='Admin User',
        email='admin@gmail.com',
        password=hash_password('admin'),
        role='admin',
        organization='AI Manufacturing HQ',
        is_active=True,
    )
    UserProfile.objects.create(
        full_name='user',
        email='user@gmail.com',
        password=hash_password('user'),
        role='industry_user',
        organization='Tata Motors',
        is_active=True,
    )
    UserProfile.objects.create(
        full_name='Priya Sharma',
        email='priya@gmail.com',
        password=hash_password('user'),
        role='industry_user',
        organization='Mahindra & Mahindra',
        is_active=True,
    )
    UserProfile.objects.create(
        full_name='Ravi Kumar',
        email='ravi@gmail.com',
        password=hash_password('user'),
        role='industry_user',
        organization='Bosch India',
        is_active=True,
    )
    print("  ✅ Users seeded (1 Admin, 3 Industry Users)")

    # ── Technology Modules ─────────────────────────────────────────────────
    TechnologyModule.objects.all().delete()

    techs = [
        {
            'title': 'Explainable AI (XAI)',
            'tech_type': 'xai',
            'description': 'Makes AI decision-making transparent and interpretable for manufacturing engineers.',
            'benefits': 'Builds trust, enables debugging, supports regulatory compliance.',
            'use_cases': 'Fault diagnosis explanation, quality prediction rationale, maintenance scheduling.',
        },
        {
            'title': 'Industrial IoT Integration',
            'tech_type': 'iot',
            'description': 'Connects physical manufacturing assets to digital systems via sensor networks.',
            'benefits': 'Real-time monitoring, remote diagnostics, predictive insights.',
            'use_cases': 'Machine health tracking, energy consumption monitoring, production line telemetry.',
        },
        {
            'title': 'Edge Computing',
            'tech_type': 'edge',
            'description': 'Processes AI inference at the machine level, reducing latency and cloud dependency.',
            'benefits': 'Sub-millisecond response, offline capability, data privacy.',
            'use_cases': 'Real-time defect detection, CNC machine optimization, assembly line control.',
        },
        {
            'title': 'Human-Robot Collaboration (HRC)',
            'tech_type': 'hrc',
            'description': 'Enables safe and efficient cooperation between human workers and robotic systems.',
            'benefits': 'Increased throughput, reduced ergonomic injuries, flexible automation.',
            'use_cases': 'Cobot-assisted assembly, welding assistance, material handling.',
        },
    ]
    for t in techs:
        TechnologyModule.objects.create(**t)
    print("  ✅ Technology modules seeded")

    # ── Challenges ─────────────────────────────────────────────────────────
    Challenge.objects.all().delete()

    challenges = [
        {
            'title': 'Data Silos in Manufacturing',
            'industry_area': 'Data Management',
            'severity': 'high',
            'description': 'Manufacturing data is fragmented across machines, ERP, MES, and SCADA systems, preventing unified AI analysis.',
            'ai_solution': 'Deploy a unified data lake with real-time ETL pipelines. Use AI-powered data harmonization to normalize formats across systems.',
        },
        {
            'title': 'Skilled Workforce Gap',
            'industry_area': 'Workforce',
            'severity': 'high',
            'description': 'Shortage of engineers capable of implementing and maintaining AI systems in traditional manufacturing environments.',
            'ai_solution': 'Implement no-code/low-code AI tools, provide AI literacy training programs, and use explainable AI to bridge knowledge gaps.',
        },
        {
            'title': 'Legacy System Integration',
            'industry_area': 'Infrastructure',
            'severity': 'medium',
            'description': 'Older machinery and control systems lack APIs or connectivity required for modern AI integration.',
            'ai_solution': 'Use industrial IoT gateways and edge devices to retrofit legacy machines with sensor capabilities without replacing them.',
        },
        {
            'title': 'High AI Implementation Costs',
            'industry_area': 'Finance',
            'severity': 'medium',
            'description': 'SME manufacturers face prohibitive upfront costs for AI hardware, software licenses, and consulting.',
            'ai_solution': 'Adopt cloud-based ML platforms with pay-per-use pricing. Start with high-ROI quick wins like predictive maintenance.',
        },
        {
            'title': 'Real-time Data Processing',
            'industry_area': 'Technology',
            'severity': 'medium',
            'description': 'Processing high-velocity sensor data from production lines in real time exceeds traditional IT infrastructure capabilities.',
            'ai_solution': 'Implement edge computing with on-device ML inference and use stream processing frameworks for real-time analytics.',
        },
        {
            'title': 'Quality Consistency Across Shifts',
            'industry_area': 'Quality Control',
            'severity': 'low',
            'description': 'Product quality varies significantly across different shifts and operators due to human variability.',
            'ai_solution': 'Deploy computer vision quality inspection systems that apply consistent standards 24/7 regardless of shift or operator.',
        },
    ]
    for c in challenges:
        Challenge.objects.create(**c)
    print("  ✅ Challenges seeded")

    # ── Recommendations ────────────────────────────────────────────────────
    Recommendation.objects.all().delete()

    recommendations = [
        {
            'title': 'Start with Predictive Maintenance',
            'category': 'Quick Wins',
            'priority': 'high',
            'description': 'Predictive maintenance offers the fastest and clearest ROI for AI adoption. Begin by instrumenting your 3-5 most critical machines with vibration and temperature sensors. Deploy a Random Forest or LSTM model to predict failures 48-72 hours in advance. Expected outcome: 20-35% reduction in unplanned downtime within 6 months.',
            'ai_generated': False,
        },
        {
            'title': 'Build a Unified Data Infrastructure',
            'category': 'Strategy',
            'priority': 'high',
            'description': 'Before scaling AI, establish a solid data foundation. Implement an industrial data lake that aggregates data from all machines, ERP, MES, and quality systems. Standardize data formats and establish data governance policies. This infrastructure investment enables all future AI initiatives.',
            'ai_generated': False,
        },
        {
            'title': 'Deploy Computer Vision for Quality Inspection',
            'category': 'Technology',
            'priority': 'medium',
            'description': 'Replace manual visual inspection with AI-powered cameras at critical checkpoints. Modern CNN models achieve 99%+ accuracy on defect detection and can inspect 100% of products vs typical 5-10% sampling in manual inspection. Expected outcome: 60-80% reduction in defect escape rate.',
            'ai_generated': False,
        },
        {
            'title': 'Upskill Your Workforce in AI Literacy',
            'category': 'Workforce',
            'priority': 'medium',
            'description': 'Technical AI adoption fails without workforce readiness. Develop a 3-tier training program: AI awareness for all staff, AI tools usage for operators and supervisors, and AI development skills for engineers. Partner with local technical institutes for ongoing training programs.',
            'ai_generated': False,
        },
    ]
    for r in recommendations:
        Recommendation.objects.create(**r)
    print("  ✅ Recommendations seeded")

    print("\n✅ Database seeded successfully!")
    print("\nLogin Credentials:")
    print("  Admin:         admin@gmail.com  / admin")
    print("  Industry User: user@gmail.com   / user")
    print("  Industry User: priya@gmail.com  / user")
    print("  Industry User: ravi@gmail.com   / user")


if __name__ == '__main__':
    seed()
