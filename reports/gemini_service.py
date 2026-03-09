from google import genai
from django.conf import settings


def get_gemini_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_recommendation(topic, category, context=''):
    try:
        client = get_gemini_client()
        prompt = f"""
You are an expert AI consultant specializing in manufacturing industry transformation.

Generate a detailed, actionable recommendation for the following:

Topic: {topic}
Category: {category}
Additional Context: {context if context else 'None provided'}

Your recommendation must include:
1. Executive Summary (2-3 sentences)
2. Why this is important for manufacturing
3. Step-by-step implementation roadmap (3-5 steps)
4. Expected ROI and benefits
5. Potential risks and mitigation strategies
6. Timeline estimate

Keep the response practical, specific to manufacturing industry, and between 250-400 words.
Use plain text only, no markdown symbols like ** or ## etc.
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip(), True

    except Exception as e:
        return f"Gemini API error: {str(e)}", False


def analyze_challenge(title, description, industry_area):
    try:
        client = get_gemini_client()
        prompt = f"""
You are a Senior AI Manufacturing Consultant with 20 years of experience.

Analyze the following manufacturing challenge in depth:

Challenge Title: {title}
Industry Area: {industry_area}
Description: {description}

Provide a structured analysis covering:
1. Root Cause Analysis - Why does this challenge exist?
2. Impact Assessment - How does it affect production, cost, and quality?
3. AI-Powered Solution Strategy - Specific AI/ML techniques to address it
4. Technology Stack Recommendation - What tools, frameworks, or platforms to use
5. Quick Win (0-3 months) - What can be done immediately
6. Long-term Strategy (6-18 months) - Sustainable solution roadmap
7. Success Metrics - How to measure improvement

Keep it practical and manufacturing-specific. 300-450 words. Plain text only.
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip(), True

    except Exception as e:
        return f"Gemini API error: {str(e)}", False


def generate_report_summary(report_title, report_content, report_type):
    try:
        client = get_gemini_client()
        prompt = f"""
You are an AI manufacturing analyst. Generate a concise executive summary for the following report:

Report Title: {report_title}
Report Type: {report_type}
Report Content:
{report_content[:2000]}

Provide:
1. Executive Summary (3-4 sentences)
2. Key Findings (3 bullet points using plain dashes)
3. Priority Actions (2-3 recommendations)
4. Overall Assessment (1 sentence verdict)

Keep it under 200 words. Plain text only, no markdown.
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip(), True

    except Exception as e:
        return f"Gemini API error: {str(e)}", False


def generate_manufacturing_insights(stats: dict):
    try:
        client = get_gemini_client()
        prompt = f"""
You are an AI manufacturing intelligence system. Based on the following platform statistics,
generate 3 key actionable insights for the manufacturing manager:

Platform Statistics:
- Total machines monitored: {stats.get('total_machines', 0)}
- Machines with failure risk: {stats.get('failure_count', 0)}
- Open quality issues: {stats.get('quality_issues', 0)}
- High severity quality issues: {stats.get('high_severity', 0)}
- Supply chain high risk suppliers: {stats.get('high_risk_suppliers', 0)}
- Process optimization records: {stats.get('total_processes', 0)}
- Average process improvement: {stats.get('avg_improvement', 0)}%

Generate exactly 3 insights, each on a new line starting with 1. 2. 3.
Each insight should be 1-2 sentences. Focus on what needs immediate attention.
Plain text only.
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = response.text.strip()
        insights = []
        for line in text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                clean = line.lstrip('0123456789.-) ').strip()
                if clean:
                    insights.append(clean)
        return insights[:3], True

    except Exception as e:
        return [f"AI insights unavailable: {str(e)}"], False
