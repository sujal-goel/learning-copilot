PROFILE_EXTRACTION_PROMPT = """
You are an expert learner profiling AI system.
Your job is to analyze user onboarding input messages and extract a structured learner profile JSON.
Extract:

1. goal
2. current_skills
3. experience_level
4. study_hours_per_day
5. timeline_months
6. interests
Rules:
1. Extract career target 'goal' (e.g., 'Backend Developer', 'AI Engineer', 'Data Scientist', 'Frontend Developer').
2. Extract experience level: BEGINNER, INTERMEDIATE, or ADVANCED. Default to BEGINNER if not mentioned.
3. Extract available study hours per week (integer). Default to 10 if not mentioned.
4. Extract target timeline in months (integer). Default to 6 if not mentioned.
5. Extract all user-mentioned current skills with estimated proficiency (float from 0.0 to 1.0):
   - Mentioned basic knowledge or learning → 0.4 to 0.6
   - Strong / confident knowledge → 0.7 to 0.9
   - Complete beginner / no knowledge → 0.0 to 0.2

Return ONLY a valid JSON object with NO extra text or markdown formatting outside the JSON block.

JSON Schema:
{
  "goal": "Backend Developer",
  "experience_level": "BEGINNER",
  "study_hours_per_week": 10,
  "timeline_months": 6,
  "skills": [
    {"name": "Java", "proficiency": 0.8},
    {"name": "SQL", "proficiency": 0.6}
  ]
}

User Input / Messages:
{messages_text}
"""