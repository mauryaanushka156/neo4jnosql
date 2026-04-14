from flask import Flask, jsonify, render_template
from flask_cors import CORS
from database import db

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------
def success_response(data=None, message="Success", status=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data if data is not None else []
    }), status


def error_response(message="Something went wrong", status=500):
    return jsonify({
        "success": False,
        "message": message,
        "data": []
    }), status


# ---------------------------------------------------------
# Home page
# ---------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------
@app.route("/health")
def health():
    try:
        result = db.run_query("RETURN 'Neo4j connection successful' AS message")
        return success_response(result, "Application is running properly")
    except Exception as e:
        return error_response(f"Database connection failed: {str(e)}", 500)


# ---------------------------------------------------------
# 1. Recommend employees for a project
# Project requirement:
# Recommend employees for projects based on skills
# ---------------------------------------------------------
@app.route("/recommend/employees/<project_id>")
def recommend_employees(project_id):
    try:
        project_check = db.run_query(
            "MATCH (p:Project {id: $project_id}) RETURN p.name AS name, p.status AS status",
            {"project_id": project_id}
        )

        if not project_check:
            return error_response(f"Project with id '{project_id}' not found", 404)

        query = """
        MATCH (p:Project {id: $project_id})-[req:REQUIRES_SKILL]->(requiredSkill:Skill)
        WITH p, collect({
            skill: requiredSkill.name,
            min_level: req.min_level
        }) AS requirements

        MATCH (e:Employee)
        OPTIONAL MATCH (e)-[hs:HAS_SKILL]->(empSkill:Skill)
        WITH p, requirements, e,
             collect({
                skill: empSkill.name,
                level: hs.level
             }) AS employee_skills

        WITH p, requirements, e, employee_skills,
             [req IN requirements
                WHERE any(es IN employee_skills
                          WHERE es.skill = req.skill AND es.level >= req.min_level)
             ] AS matched_requirements

        WITH p, e, requirements, employee_skills, matched_requirements,
             size(requirements) AS total_required,
             size(matched_requirements) AS matched_count

        RETURN
            e.id AS employee_id,
            e.name AS employee_name,
            e.department AS department,
            matched_count,
            total_required,
            CASE
                WHEN total_required = 0 THEN 0
                ELSE round((toFloat(matched_count) / total_required) * 100, 2)
            END AS match_percent,
            [req IN requirements
                WHERE NOT any(es IN employee_skills
                              WHERE es.skill = req.skill AND es.level >= req.min_level)
            ] AS missing_requirements
        ORDER BY match_percent DESC, matched_count DESC, employee_name ASC
        """

        results = db.run_query(query, {"project_id": project_id})

        return success_response({
            "project": project_check[0],
            "recommendations": results
        }, "Employee recommendations generated successfully")

    except Exception as e:
        return error_response(f"Error while recommending employees: {str(e)}", 500)


# ---------------------------------------------------------
# 2. Identify skill gaps for a project
# Project requirement:
# Identify skill gaps in teams
# ---------------------------------------------------------
@app.route("/gaps/project/<project_id>")
def skill_gaps_for_project(project_id):
    try:
        project_check = db.run_query(
            "MATCH (p:Project {id: $project_id}) RETURN p.id AS id, p.name AS name, p.status AS status",
            {"project_id": project_id}
        )

        if not project_check:
            return error_response(f"Project with id '{project_id}' not found", 404)

        query = """
        MATCH (p:Project {id: $project_id})-[r:REQUIRES_SKILL]->(s:Skill)
        OPTIONAL MATCH (e:Employee)-[hs:HAS_SKILL]->(s)
        WHERE hs.level >= r.min_level
        WITH p, s.name AS skill,
             r.min_level AS required_level,
             count(DISTINCT e) AS qualified_employees
        RETURN
            skill,
            required_level,
            qualified_employees,
            CASE
                WHEN qualified_employees = 0 THEN 'Critical Gap'
                WHEN qualified_employees = 1 THEN 'Risk'
                ELSE 'Covered'
            END AS status
        ORDER BY qualified_employees ASC, skill ASC
        """

        results = db.run_query(query, {"project_id": project_id})

        return success_response({
            "project": project_check[0],
            "skill_gaps": results
        }, "Project skill gap analysis completed")

    except Exception as e:
        return error_response(f"Error while finding project skill gaps: {str(e)}", 500)


# ---------------------------------------------------------
# 3. Identify department/team skill gaps
# Extra useful feature for viva/demo
# ---------------------------------------------------------
@app.route("/gaps/department/<department_name>")
def skill_gaps_for_department(department_name):
    try:
        dept_check = db.run_query(
            "MATCH (e:Employee {department: $department}) RETURN count(e) AS total",
            {"department": department_name}
        )

        if not dept_check or dept_check[0]["total"] == 0:
            return error_response(f"No employees found in department '{department_name}'", 404)

        query = """
        MATCH (s:Skill)
        OPTIONAL MATCH (e:Employee {department: $department})-[hs:HAS_SKILL]->(s)
        WITH s.name AS skill,
             count(hs) AS employees_with_skill,
             avg(hs.level) AS average_level
        RETURN
            skill,
            employees_with_skill,
            CASE
                WHEN average_level IS NULL THEN 0
                ELSE round(average_level, 2)
            END AS average_level,
            CASE
                WHEN employees_with_skill = 0 THEN 'Gap'
                WHEN employees_with_skill = 1 THEN 'Limited Coverage'
                ELSE 'Available'
            END AS status
        ORDER BY employees_with_skill ASC, average_level ASC, skill ASC
        """

        results = db.run_query(query, {"department": department_name})

        return success_response({
            "department": department_name,
            "skill_gaps": results
        }, "Department skill gap analysis completed")

    except Exception as e:
        return error_response(f"Error while finding department skill gaps: {str(e)}", 500)


# ---------------------------------------------------------
# 4. Suggest training paths for an employee
# Project requirement:
# Suggest training paths for employees
# ---------------------------------------------------------
@app.route("/training/<employee_id>")
def training_path(employee_id):
    try:
        employee_check = db.run_query(
            "MATCH (e:Employee {id: $employee_id}) RETURN e.id AS id, e.name AS name, e.department AS department",
            {"employee_id": employee_id}
        )

        if not employee_check:
            return error_response(f"Employee with id '{employee_id}' not found", 404)

        query = """
        MATCH (j:JobRole)-[r:REQUIRES_SKILL]->(s:Skill)
        OPTIONAL MATCH (e:Employee {id: $employee_id})-[hs:HAS_SKILL]->(s)
        WITH j, s,
             r.min_level AS required_level,
             COALESCE(hs.level, 0) AS current_level
        WHERE current_level < required_level

        WITH j,
             collect({
                skill: s.name,
                current_level: current_level,
                required_level: required_level,
                gap: required_level - current_level
             }) AS missing_skills,
             sum(required_level - current_level) AS total_gap

        OPTIONAL MATCH (c:Course)-[:TEACHES]->(skill:Skill)
        WHERE skill.name IN [ms IN missing_skills | ms.skill]

        RETURN
            j.title AS job_role,
            j.level AS role_level,
            total_gap,
            missing_skills,
            collect(DISTINCT {
                course: c.name,
                platform: c.platform
            }) AS recommended_courses
        ORDER BY total_gap ASC, job_role ASC
        LIMIT 3
        """

        results = db.run_query(query, {"employee_id": employee_id})

        return success_response({
            "employee": employee_check[0],
            "training_paths": results
        }, "Training recommendations generated successfully")

    except Exception as e:
        return error_response(f"Error while generating training path: {str(e)}", 500)


# ---------------------------------------------------------
# 5. Recommend job roles for an employee
# Good extra feature: very aligned with project title
# ---------------------------------------------------------
@app.route("/recommend/jobs/<employee_id>")
def recommend_job_roles(employee_id):
    try:
        employee_check = db.run_query(
            "MATCH (e:Employee {id: $employee_id}) RETURN e.id AS id, e.name AS name, e.department AS department",
            {"employee_id": employee_id}
        )

        if not employee_check:
            return error_response(f"Employee with id '{employee_id}' not found", 404)

        query = """
        MATCH (j:JobRole)-[req:REQUIRES_SKILL]->(s:Skill)
        OPTIONAL MATCH (e:Employee {id: $employee_id})-[hs:HAS_SKILL]->(s)
        WITH j,
             count(s) AS total_required,
             sum(
                CASE
                    WHEN hs.level IS NOT NULL AND hs.level >= req.min_level THEN 1
                    ELSE 0
                END
             ) AS matched_count,
             collect(
                CASE
                    WHEN hs.level IS NULL OR hs.level < req.min_level
                    THEN {
                        skill: s.name,
                        required_level: req.min_level,
                        current_level: COALESCE(hs.level, 0)
                    }
                    ELSE NULL
                END
             ) AS raw_missing

        WITH j, total_required, matched_count,
             [x IN raw_missing WHERE x IS NOT NULL] AS missing_skills
        RETURN
            j.title AS job_role,
            j.level AS role_level,
            matched_count,
            total_required,
            CASE
                WHEN total_required = 0 THEN 0
                ELSE round((toFloat(matched_count) / total_required) * 100, 2)
            END AS match_percent,
            missing_skills
        ORDER BY match_percent DESC, matched_count DESC, job_role ASC
        """

        results = db.run_query(query, {"employee_id": employee_id})

        return success_response({
            "employee": employee_check[0],
            "job_recommendations": results
        }, "Job role recommendations generated successfully")

    except Exception as e:
        return error_response(f"Error while recommending job roles: {str(e)}", 500)


# ---------------------------------------------------------
# 6. List all employees
# ---------------------------------------------------------
@app.route("/employees")
def list_employees():
    try:
        query = """
        MATCH (e:Employee)
        RETURN e.id AS id, e.name AS name, e.department AS department
        ORDER BY e.name
        """
        results = db.run_query(query)
        return success_response(results, "Employees fetched successfully")
    except Exception as e:
        return error_response(f"Error while fetching employees: {str(e)}", 500)


# ---------------------------------------------------------
# 7. List all projects
# ---------------------------------------------------------
@app.route("/projects")
def list_projects():
    try:
        query = """
        MATCH (p:Project)
        RETURN p.id AS id, p.name AS name, p.status AS status
        ORDER BY p.name
        """
        results = db.run_query(query)
        return success_response(results, "Projects fetched successfully")
    except Exception as e:
        return error_response(f"Error while fetching projects: {str(e)}", 500)


# ---------------------------------------------------------
# 8. List all job roles
# ---------------------------------------------------------
@app.route("/jobroles")
def list_job_roles():
    try:
        query = """
        MATCH (j:JobRole)
        RETURN j.title AS title, j.level AS level
        ORDER BY j.title
        """
        results = db.run_query(query)
        return success_response(results, "Job roles fetched successfully")
    except Exception as e:
        return error_response(f"Error while fetching job roles: {str(e)}", 500)


# ---------------------------------------------------------
# 9. Get skills of a specific employee
# ---------------------------------------------------------
@app.route("/employee/<employee_id>/skills")
def employee_skills(employee_id):
    try:
        employee_check = db.run_query(
            "MATCH (e:Employee {id: $employee_id}) RETURN e.name AS name, e.department AS department",
            {"employee_id": employee_id}
        )

        if not employee_check:
            return error_response(f"Employee with id '{employee_id}' not found", 404)

        query = """
        MATCH (e:Employee {id: $employee_id})-[hs:HAS_SKILL]->(s:Skill)
        RETURN
            e.name AS employee_name,
            e.department AS department,
            s.name AS skill,
            hs.level AS level
        ORDER BY hs.level DESC, s.name ASC
        """
        results = db.run_query(query, {"employee_id": employee_id})

        return success_response({
            "employee": employee_check[0],
            "skills": results
        }, "Employee skills fetched successfully")

    except Exception as e:
        return error_response(f"Error while fetching employee skills: {str(e)}", 500)


# ---------------------------------------------------------
# 10. Get requirements of a project
# Useful for demo clarity
# ---------------------------------------------------------
@app.route("/project/<project_id>/requirements")
def project_requirements(project_id):
    try:
        project_check = db.run_query(
            "MATCH (p:Project {id: $project_id}) RETURN p.id AS id, p.name AS name, p.status AS status",
            {"project_id": project_id}
        )

        if not project_check:
            return error_response(f"Project with id '{project_id}' not found", 404)

        query = """
        MATCH (p:Project {id: $project_id})-[r:REQUIRES_SKILL]->(s:Skill)
        RETURN
            s.name AS skill,
            r.min_level AS min_level
        ORDER BY r.min_level DESC, s.name ASC
        """
        results = db.run_query(query, {"project_id": project_id})

        return success_response({
            "project": project_check[0],
            "requirements": results
        }, "Project requirements fetched successfully")

    except Exception as e:
        return error_response(f"Error while fetching project requirements: {str(e)}", 500)


# ---------------------------------------------------------
# 11. Dashboard summary
# Nice feature for homepage/demo
# ---------------------------------------------------------
@app.route("/dashboard/summary")
def dashboard_summary():
    try:
        query = """
        CALL {
            MATCH (e:Employee)
            RETURN count(e) AS total_employees
        }
        CALL {
            MATCH (s:Skill)
            RETURN count(s) AS total_skills
        }
        CALL {
            MATCH (p:Project)
            RETURN count(p) AS total_projects
        }
        CALL {
            MATCH (j:JobRole)
            RETURN count(j) AS total_job_roles
        }
        CALL {
            MATCH (c:Course)
            RETURN count(c) AS total_courses
        }
        RETURN total_employees, total_skills, total_projects, total_job_roles, total_courses
        """
        results = db.run_query(query)
        return success_response(results[0], "Dashboard summary fetched successfully")
    except Exception as e:
        return error_response(f"Error while fetching dashboard summary: {str(e)}", 500)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
    