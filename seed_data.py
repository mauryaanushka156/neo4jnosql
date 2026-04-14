from database import db

def clear_db():
    db.run_query("MATCH (n) DETACH DELETE n")

def create_skills():
    skills = [
        "Python", "Java", "JavaScript", "React", "Node.js",
        "Machine Learning", "Data Analysis", "SQL", "MongoDB",
        "Neo4j", "Docker", "Kubernetes", "AWS", "Communication",
        "Project Management", "UI/UX Design", "TensorFlow", "Spark"
    ]
    for skill in skills:
        db.run_query(
            "MERGE (s:Skill {name: $name})",
            {"name": skill}
        )
    print("Skills created.")

def create_employees():
    employees = [
        {"id": "E001", "name": "Himanshu Mishra",  "department": "Engineering"},
        {"id": "E002", "name": "Anushka Maurya",     "department": "Data Science"},
        {"id": "E003", "name": "Anusha Mendon",    "department": "Engineering"},
        {"id": "E004", "name": "Priya Sharma",   "department": "DevOps"},
        {"id": "E005", "name": "Rohan Mehta",     "department": "Data Science"},
        {"id": "E006", "name": "Raj Sharma",   "department": "Design"},
        {"id": "E007", "name": "Sia Singh",    "department": "Engineering"},
    ]
    for emp in employees:
        db.run_query(
            "MERGE (e:Employee {id: $id, name: $name, department: $department})",
            emp
        )
    print("Employees created.")

def create_employee_skills():
    # Format: (employee_id, skill_name, level 1-5)
    links = [
        ("E001", "Python",             5),
        ("E001", "Machine Learning",   4),
        ("E001", "TensorFlow",         3),
        ("E001", "SQL",                4),
        ("E002", "Python",             4),
        ("E002", "Data Analysis",      5),
        ("E002", "Spark",              3),
        ("E002", "SQL",                5),
        ("E003", "JavaScript",         5),
        ("E003", "React",              4),
        ("E003", "Node.js",            4),
        ("E003", "MongoDB",            3),
        ("E004", "Docker",             5),
        ("E004", "Kubernetes",         4),
        ("E004", "AWS",                4),
        ("E004", "Python",             3),
        ("E005", "Machine Learning",   5),
        ("E005", "TensorFlow",         5),
        ("E005", "Python",             4),
        ("E005", "Data Analysis",      4),
        ("E006", "UI/UX Design",       5),
        ("E006", "JavaScript",         3),
        ("E006", "React",              3),
        ("E007", "Java",               5),
        ("E007", "Python",             3),
        ("E007", "Docker",             3),
        ("E007", "AWS",                3),
    ]
    for emp_id, skill, level in links:
        db.run_query("""
            MATCH (e:Employee {id: $emp_id})
            MATCH (s:Skill {name: $skill})
            MERGE (e)-[:HAS_SKILL {level: $level}]->(s)
        """, {"emp_id": emp_id, "skill": skill, "level": level})
    print("Employee-Skill links created.")

def create_projects():
    projects = [
        {"id": "P001", "name": "AI Chatbot",          "status": "Active"},
        {"id": "P002", "name": "E-Commerce Platform",  "status": "Active"},
        {"id": "P003", "name": "Data Pipeline",        "status": "Planning"},
        {"id": "P004", "name": "Cloud Migration",      "status": "Active"},
    ]
    for proj in projects:
        db.run_query(
            "MERGE (p:Project {id: $id, name: $name, status: $status})",
            proj
        )
    print("Projects created.")

def create_project_requirements():
    # (project_id, skill_name, required_level)
    reqs = [
        ("P001", "Python",           4),
        ("P001", "Machine Learning", 4),
        ("P001", "TensorFlow",       3),
        ("P002", "JavaScript",       4),
        ("P002", "React",            4),
        ("P002", "Node.js",          3),
        ("P002", "MongoDB",          3),
        ("P003", "Python",           3),
        ("P003", "Spark",            4),
        ("P003", "SQL",              4),
        ("P003", "Data Analysis",    4),
        ("P004", "Docker",           4),
        ("P004", "Kubernetes",       4),
        ("P004", "AWS",              4),
    ]
    for proj_id, skill, level in reqs:
        db.run_query("""
            MATCH (p:Project {id: $proj_id})
            MATCH (s:Skill {name: $skill})
            MERGE (p)-[:REQUIRES_SKILL {min_level: $level}]->(s)
        """, {"proj_id": proj_id, "skill": skill, "level": level})
    print("Project requirements created.")

def create_job_roles():
    roles = [
        {"title": "ML Engineer",       "level": "Senior"},
        {"title": "Frontend Developer","level": "Mid"},
        {"title": "Data Engineer",     "level": "Senior"},
        {"title": "DevOps Engineer",   "level": "Senior"},
        {"title": "Full Stack Dev",    "level": "Mid"},
    ]
    for role in roles:
        db.run_query(
            "MERGE (j:JobRole {title: $title, level: $level})",
            role
        )
    print("Job roles created.")

def create_role_skill_requirements():
    reqs = [
        ("ML Engineer",        "Python",           4),
        ("ML Engineer",        "Machine Learning", 4),
        ("ML Engineer",        "TensorFlow",       4),
        ("ML Engineer",        "Data Analysis",    3),
        ("Frontend Developer", "JavaScript",       4),
        ("Frontend Developer", "React",            4),
        ("Frontend Developer", "UI/UX Design",     3),
        ("Data Engineer",      "Python",           3),
        ("Data Engineer",      "SQL",              4),
        ("Data Engineer",      "Spark",            4),
        ("Data Engineer",      "Data Analysis",    4),
        ("DevOps Engineer",    "Docker",           4),
        ("DevOps Engineer",    "Kubernetes",       4),
        ("DevOps Engineer",    "AWS",              4),
        ("Full Stack Dev",     "JavaScript",       4),
        ("Full Stack Dev",     "React",            3),
        ("Full Stack Dev",     "Node.js",          3),
        ("Full Stack Dev",     "MongoDB",          3),
        ("Full Stack Dev",     "SQL",              3),
    ]
    for title, skill, level in reqs:
        db.run_query("""
            MATCH (j:JobRole {title: $title})
            MATCH (s:Skill {name: $skill})
            MERGE (j)-[:REQUIRES_SKILL {min_level: $level}]->(s)
        """, {"title": title, "skill": skill, "level": level})
    print("Role-Skill requirements created.")

def create_courses():
    courses = [
        {"name": "Deep Learning Specialization", "platform": "Coursera"},
        {"name": "AWS Cloud Practitioner",        "platform": "AWS"},
        {"name": "React Complete Guide",          "platform": "Udemy"},
        {"name": "Spark & Big Data",              "platform": "Udemy"},
        {"name": "Kubernetes Mastery",            "platform": "Udemy"},
        {"name": "SQL Bootcamp",                  "platform": "Udemy"},
        {"name": "UX Design Fundamentals",        "platform": "Google"},
    ]
    teaches = [
        ("Deep Learning Specialization", "TensorFlow"),
        ("Deep Learning Specialization", "Machine Learning"),
        ("Deep Learning Specialization", "Python"),
        ("AWS Cloud Practitioner",       "AWS"),
        ("React Complete Guide",         "React"),
        ("React Complete Guide",         "JavaScript"),
        ("Spark & Big Data",             "Spark"),
        ("Spark & Big Data",             "Data Analysis"),
        ("Kubernetes Mastery",           "Kubernetes"),
        ("Kubernetes Mastery",           "Docker"),
        ("SQL Bootcamp",                 "SQL"),
        ("SQL Bootcamp",                 "Data Analysis"),
        ("UX Design Fundamentals",       "UI/UX Design"),
    ]
    for course in courses:
        db.run_query(
            "MERGE (c:Course {name: $name, platform: $platform})",
            course
        )
    for course_name, skill_name in teaches:
        db.run_query("""
            MATCH (c:Course {name: $course})
            MATCH (s:Skill {name: $skill})
            MERGE (c)-[:TEACHES]->(s)
        """, {"course": course_name, "skill": skill_name})
    print("Courses created.")

if __name__ == "__main__":
    print("Seeding database...")
    clear_db()
    create_skills()
    create_employees()
    create_employee_skills()
    create_projects()
    create_project_requirements()
    create_job_roles()
    create_role_skill_requirements()
    create_courses()
    print("Done! Database seeded successfully.")