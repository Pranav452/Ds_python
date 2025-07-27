# main.py

from fastapi import FastAPI, HTTPException, Query, status, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import re

app = FastAPI(title="Enhanced University System")

# In-memory storage
students: Dict[int, dict] = {}
courses: Dict[str, dict] = {}
professors: Dict[int, dict] = {}
enrollments: List[dict] = []

student_email_set = set()
professor_email_set = set()
course_code_set = set()

# Helper functions
def error_response(message: str, details: Any = None, code: int = 400):
    return JSONResponse(
        status_code=code,
        content={"error": message, "details": details}
    )

def get_next_id(entity_dict: Dict[int, dict]) -> int:
    return max(entity_dict.keys(), default=0) + 1

def course_code_valid(code: str) -> bool:
    return bool(re.match(r"^[A-Z]{2,4}\d{3}-\d{3}$", code))

def is_email_unique(email: str) -> bool:
    return email not in student_email_set and email not in professor_email_set

def get_student_credits(student_id: int) -> int:
    return sum(
        courses[enr['course_code']]['credits']
        for enr in enrollments
        if enr['student_id'] == student_id and enr['status'] == "enrolled"
    )

def get_professor_courses(prof_id: int) -> int:
    return sum(
        1 for c in courses.values() if c.get('professor_id') == prof_id
    )

def get_student_gpa(student_id: int) -> float:
    grades = [
        enr['grade'] for enr in enrollments
        if enr['student_id'] == student_id and enr['status'] == "enrolled" and enr['grade'] is not None
    ]
    if not grades:
        return 0.0
    return round(sum(grades) / len(grades), 2)

def check_prerequisites(student_id: int, course_code: str) -> bool:
    prereqs = courses[course_code].get('prerequisites', [])
    completed = [
        enr['course_code'] for enr in enrollments
        if enr['student_id'] == student_id and enr['grade'] is not None and enr['grade'] >= 2.0
    ]
    return all(pr in completed for pr in prereqs)

# Pydantic Models
class StudentModel(BaseModel):
    name: str
    email: EmailStr
    year: int = Field(..., ge=1, le=4)
    major: str
    gpa: float = Field(..., ge=0.0, le=4.0)

    @validator('email')
    def email_unique(cls, v):
        if not is_email_unique(v):
            raise ValueError("Email must be unique")
        return v

class CourseModel(BaseModel):
    code: str
    name: str
    department: str
    credits: int = Field(..., ge=1, le=6)
    capacity: int = Field(..., ge=1)
    professor_id: int
    prerequisites: Optional[List[str]] = []

    @validator('code')
    def code_format(cls, v):
        if not course_code_valid(v):
            raise ValueError("Course code must be in format DEPT###-###")
        return v

class ProfessorModel(BaseModel):
    name: str
    email: EmailStr
    department: str
    hire_date: date

    @validator('email')
    def email_unique(cls, v):
        if not is_email_unique(v):
            raise ValueError("Email must be unique")
        return v

    @validator('hire_date')
    def hire_date_valid(cls, v):
        if v > date.today():
            raise ValueError("Hire date cannot be in the future")
        if v.year < 1950:
            raise ValueError("Hire date must be after 1950")
        return v

class EnrollmentModel(BaseModel):
    student_id: int
    course_code: str
    enrollment_date: date
    grade: Optional[float] = Field(None, ge=0.0, le=4.0)
    status: str = "enrolled"  # enrolled, withdrawn, waitlisted

    @validator('enrollment_date')
    def enrollment_date_valid(cls, v):
        if v > date.today():
            raise ValueError("Enrollment date cannot be in the future")
        return v

    @validator('grade')
    def grade_valid(cls, v):
        if v is not None and (v < 0.0 or v > 4.0):
            raise ValueError("Grade must be between 0.0 and 4.0")
        return v

# CRUD Endpoints

@app.post("/students", status_code=201)
def create_student(student: StudentModel):
    if not is_email_unique(student.email):
        return error_response("Email already exists", code=409)
    student_id = get_next_id(students)
    students[student_id] = student.dict()
    student_email_set.add(student.email)
    return {"id": student_id, **student.dict()}

@app.get("/students")
def list_students(
    page: int = 1,
    limit: int = 10,
    major: Optional[str] = None,
    year: Optional[int] = None
):
    filtered = [
        {"id": sid, **s}
        for sid, s in students.items()
        if (major is None or s['major'] == major) and (year is None or s['year'] == year)
    ]
    start = (page - 1) * limit
    end = start + limit
    return {"total": len(filtered), "students": filtered[start:end]}

@app.get("/students/{student_id}")
def get_student(student_id: int):
    if student_id not in students:
        return error_response("Student not found", code=404)
    return {"id": student_id, **students[student_id]}

@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentModel):
    if student_id not in students:
        return error_response("Student not found", code=404)
    students[student_id] = student.dict()
    return {"id": student_id, **student.dict()}

@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    if student_id not in students:
        return error_response("Student not found", code=404)
    student_email_set.discard(students[student_id]['email'])
    del students[student_id]
    return

# Similar CRUD for courses and professors...

@app.post("/courses", status_code=201)
def create_course(course: CourseModel):
    if course.code in courses:
        return error_response("Course code already exists", code=409)
    if course.professor_id not in professors:
        return error_response("Professor not found", code=404)
    if get_professor_courses(course.professor_id) >= 4:
        return error_response("Professor teaching load exceeded", code=409)
    courses[course.code] = course.dict()
    course_code_set.add(course.code)
    return {"code": course.code, **course.dict()}

@app.get("/courses")
def list_courses(
    department: Optional[str] = None,
    credits: Optional[int] = None
):
    filtered = [
        {"code": code, **c}
        for code, c in courses.items()
        if (department is None or c['department'] == department) and (credits is None or c['credits'] == credits)
    ]
    return {"total": len(filtered), "courses": filtered}

@app.post("/professors", status_code=201)
def create_professor(prof: ProfessorModel):
    if not is_email_unique(prof.email):
        return error_response("Email already exists", code=409)
    prof_id = get_next_id(professors)
    professors[prof_id] = prof.dict()
    professor_email_set.add(prof.email)
    return {"id": prof_id, **prof.dict()}

@app.get("/professors")
def list_professors(
    department: Optional[str] = None,
    hire_year: Optional[int] = None
):
    filtered = [
        {"id": pid, **p}
        for pid, p in professors.items()
        if (department is None or p['department'] == department) and (hire_year is None or p['hire_date'].year == hire_year)
    ]
    return {"total": len(filtered), "professors": filtered}

# Enrollment endpoints

@app.post("/enrollments", status_code=201)
def enroll_student(enr: EnrollmentModel):
    # Check student and course exist
    if enr.student_id not in students:
        return error_response("Student not found", code=404)
    if enr.course_code not in courses:
        return error_response("Course not found", code=404)
    # Check duplicate enrollment
    for e in enrollments:
        if e['student_id'] == enr.student_id and e['course_code'] == enr.course_code:
            return error_response("Duplicate enrollment", code=409)
    # Check prerequisites
    if not check_prerequisites(enr.student_id, enr.course_code):
        return error_response("Prerequisites not satisfied", code=409)
    # Check credit hour limit
    if get_student_credits(enr.student_id) + courses[enr.course_code]['credits'] > 18:
        return error_response("Credit hour limit exceeded", code=409)
    # Check course capacity
    enrolled_count = sum(1 for e in enrollments if e['course_code'] == enr.course_code and e['status'] == "enrolled")
    if enrolled_count >= courses[enr.course_code]['capacity']:
        enr.status = "waitlisted"
    enrollments.append(enr.dict())
    return enr.dict()

# Bulk operations

@app.post("/students/bulk", status_code=201)
def bulk_register_students(students_list: List[StudentModel]):
    created = []
    for s in students_list:
        if is_email_unique(s.email):
            sid = get_next_id(students)
            students[sid] = s.dict()
            student_email_set.add(s.email)
            created.append({"id": sid, **s.dict()})
    return {"created": created}

@app.post("/enrollments/bulk", status_code=201)
def bulk_enroll(enrollments_list: List[EnrollmentModel]):
    created = []
    for e in enrollments_list:
        try:
            enroll_student(e)
            created.append(e.dict())
        except Exception as ex:
            continue
    return {"created": created}

@app.put("/enrollments/grades/bulk")
def bulk_update_grades(grades: List[dict]):
    updated = []
    for g in grades:
        for e in enrollments:
            if e['student_id'] == g['student_id'] and e['course_code'] == g['course_code']:
                e['grade'] = g['grade']
                updated.append(e)
    return {"updated": updated}

# Analytics endpoints

@app.get("/analytics/students/gpa-distribution")
def gpa_distribution():
    dist = {"<2.0": 0, "2.0-3.0": 0, "3.0-4.0": 0}
    for sid in students:
        gpa = get_student_gpa(sid)
        if gpa < 2.0:
            dist["<2.0"] += 1
        elif gpa < 3.0:
            dist["2.0-3.0"] += 1
        else:
            dist["3.0-4.0"] += 1
    return dist

@app.get("/analytics/courses/enrollment-stats")
def course_enrollment_stats():
    stats = {}
    for code in courses:
        stats[code] = sum(1 for e in enrollments if e['course_code'] == code and e['status'] == "enrolled")
    return stats

@app.get("/analytics/professors/teaching-load")
def professor_teaching_load():
    stats = {}
    for pid in professors:
        stats[pid] = get_professor_courses(pid)
    return stats

@app.get("/analytics/departments/performance")
def department_performance():
    perf = {}
    for c in courses.values():
        dept = c['department']
        if dept not in perf:
            perf[dept] = []
        for e in enrollments:
            if e['course_code'] == c['code'] and e['grade'] is not None:
                perf[dept].append(e['grade'])
    return {d: round(sum(g)/len(g), 2) if g else 0.0 for d, g in perf.items()}

# Academic probation endpoint

@app.get("/students/{student_id}/probation")
def check_probation(student_id: int):
    if student_id not in students:
        return error_response("Student not found", code=404)
    gpa = get_student_gpa(student_id)
    return {"student_id": student_id, "on_probation": gpa < 2.0, "gpa": gpa}

# Error handler for validation errors
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return error_response("Validation error", details=exc.errors(), code=422)
