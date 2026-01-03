def extract_skills(text):
    with open("data/skills_list.txt", "r") as file:
        skills = [skill.strip().lower() for skill in file.readlines()]

    extracted_skills = []
    for skill in skills:
        if skill in text:
            extracted_skills.append(skill)

    return list(set(extracted_skills))
