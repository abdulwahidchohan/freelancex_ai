# Skill suggestions
def recommend_skills(profile):
    print(f"Recommending skills for profile: {profile}...")
    
    # Define common skill categories
    tech_skills = ["Python Programming", "JavaScript", "Data Analysis", "Machine Learning", "Web Development"]
    business_skills = ["Project Management", "Business Analysis", "Digital Marketing", "Content Writing"]
    soft_skills = ["Communication", "Problem Solving", "Team Leadership", "Time Management"]
    
    recommended_skills = []
    
    # Basic profile analysis and skill matching
    if isinstance(profile, dict):
        # Check experience level
        experience = profile.get('experience_years', 0)
        if experience < 2:
            recommended_skills.extend(tech_skills[:2])  # Basic technical skills
            recommended_skills.extend(soft_skills[:2])  # Basic soft skills
        elif 2 <= experience < 5:
            recommended_skills.extend(tech_skills[2:4])  # Intermediate technical skills
            recommended_skills.extend(business_skills[:2])  # Basic business skills
        else:
            recommended_skills.extend(tech_skills[3:])  # Advanced technical skills
            recommended_skills.extend(business_skills[2:])  # Advanced business skills
            
        # Check current role/interests
        if profile.get('interests'):
            for interest in profile['interests']:
                if 'tech' in interest.lower():
                    recommended_skills.extend(tech_skills)
                elif 'business' in interest.lower():
                    recommended_skills.extend(business_skills)
                    
    # If profile analysis fails or profile is not in expected format,
    # return default recommendations
    if not recommended_skills:
        recommended_skills = ["Python Programming", "Data Analysis", "Machine Learning"]
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(recommended_skills))
