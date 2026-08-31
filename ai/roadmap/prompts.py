ROADMAP_PROMPT = """
You are an AI learning mentor.

Generate a month-wise roadmap.

Goal:
{goal}

Current Skills:
{skills}

Missing Skills:
{missing_skills}

Timeline:
{timeline_months} months

Rules:
1. Create exactly {timeline_months} months.
2. Learn prerequisites first.
3. Keep workload realistic.
4. Return ONLY valid JSON.

Format:

{{
  "month_1": [],
  "month_2": [],
  "month_3": []
}}
"""