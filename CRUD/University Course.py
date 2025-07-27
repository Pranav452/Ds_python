# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict
from datetime import date

app = FastAPI()

# In-memory "databases"
students: Dict[int, dict] = {}
courses: Dict[int, dict] = {}
professors: Dict[int, dict] = {}
enrollments: Dict[tuple, dict] = {}  # key: (student_id, course_id)

# --- Pydantic Models ---

class StudentBase(BaseModel):
    name: str
    email: EmailStr
    major: str
    year: int = Field(..., ge=1, le=8)
    gpa: float = Field(0.0, ge=0.0, le=4.0)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    major: Optional[str]
    year: Optional[int]
    gpa: Optional[float]

class Student(StudentBase):
    id: int

class ProfessorBase(BaseModel):
    name: str
    email: EmailStr
    department: str
    hire_date: date

class ProfessorCreate(ProfessorBase):
    pass

class ProfessorUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    department: Optional[str]
    hire_date: Optional[date]

class Professor(ProfessorBase):
    id: int

class CourseBase(BaseModel):
    name: str
    code: str
    credits: int = Field(..., ge=1, le=10)
    professor_id: int
    max_capacity: int = Field(..., ge=1)

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: Optional[str]
    code: Optional[str]
    credits: Optional[int]
    professor_id: Optional[int]
    max_capacity: Optional[int]

class Course(CourseBase):
    id: int

class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int
    enrollment_date: date
    grade: Optional[float] = None  # None means not graded yet

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentUpdate(BaseModel):
    grade: Optional[float]

class Enrollment(EnrollmentBase):
    pass

# --- Helper Functions ---

def calculate_gpa(student_id: int):
    grades = [
        e['grade']
        for (sid, _), e in enrollments.items()
        if sid == student_id and e['grade'] is not None
    ]
    if grades:
        gpa = round(sum(grades) / len(grades), 2)
    else:
        gpa = 0.0
    students[student_id]['gpa'] = gpa

def get_next_id(db: Dict[int, dict]) -> int:
    return max(db.keys(), default=0) + 1

# --- Student Endpoints ---

@app.post("/students", response_model=Student)
def create_student(student: StudentCreate):
    student_id = get_next_id(students)
    for s in students.values():
        if s['email'] == student.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    students[student_id] = student.dict()
    students[student_id]['id'] = student_id
    return students[student_id]

@app.get("/students", response_model=List[Student])
def get_students():
    return list(students.values())

@app.get("/students/{id}", response_model=Student)
def get_student(id: int):
    if id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return students[id]

@app.put("/students/{id}", response_model=Student)
def update_student(id: int, student: StudentUpdate):
    if id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    for field, value in student.dict(exclude_unset=True).items():
        students[id][field] = value
    return students[id]

@app.delete("/students/{id}")
def delete_student(id: int):
    if id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    # Remove enrollments
    to_delete = [key for key in enrollments if key[0] == id]
    for key in to_delete:
        del enrollments[key]
    del students[id]
    return {"detail": "Student deleted"}

@app.get("/students/{id}/courses", response_model=List[Course])
def get_student_courses(id: int):
    if id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    course_ids = [cid for (sid, cid) in enrollments if sid == id]
    return [courses[cid] for cid in course_ids if cid in courses]

# --- Professor Endpoints ---

@app.post("/professors", response_model=Professor)
def create_professor(prof: ProfessorCreate):
    prof_id = get_next_id(professors)
    for p in professors.values():
        if p['email'] == prof.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    professors[prof_id] = prof.dict()
    professors[prof_id]['id'] = prof_id
    return professors[prof_id]

@app.get("/professors", response_model=List[Professor])
def get_professors():
    return list(professors.values())

@app.get("/professors/{id}", response_model=Professor)
def get_professor(id: int):
    if id not in professors:
        raise HTTPException(status_code=404, detail="Professor not found")
    return professors[id]

@app.put("/professors/{id}", response_model=Professor)
def update_professor(id: int, prof: ProfessorUpdate):
    if id not in professors:
        raise HTTPException(status_code=404, detail="Professor not found")
    for field, value in prof.dict(exclude_unset=True).items():
        professors[id][field] = value
    return professors[id]

@app.delete("/professors/{id}")
def delete_professor(id: int):
    if id not in professors:
        raise HTTPException(status_code=404, detail="Professor not found")
    # Remove professor from courses (set professor_id to None)
    for c in courses.values():
        if c['professor_id'] == id:
            c['professor_id'] = None
    del professors[id]
    return {"detail": "Professor deleted"}

@app.get("/professors/{id}/courses", response_model=List[Course])
def get_professor_courses(id: int):
    if id not in professors:
        raise HTTPException(status_code=404, detail="Professor not found")
    return [c for c in courses.values() if c['professor_id'] == id]

# --- Course Endpoints ---

@app.post("/courses", response_model=Course)
def create_course(course: CourseCreate):
    if course.professor_id not in professors:
        raise HTTPException(status_code=400, detail="Professor does not exist")
    course_id = get_next_id(courses)
    for c in courses.values():
        if c['code'] == course.code:
            raise HTTPException(status_code=400, detail="Course code already exists")
    courses[course_id] = course.dict()
    courses[course_id]['id'] = course_id
    return courses[course_id]

@app.get("/courses", response_model=List[Course])
def get_courses():
    return list(courses.values())

@app.get("/courses/{id}", response_model=Course)
def get_course(id: int):
    if id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    return courses[id]

@app.put("/courses/{id}", response_model=Course)
def update_course(id: int, course: CourseUpdate):
    if id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    update_data = course.dict(exclude_unset=True)
    if 'professor_id' in update_data and update_data['professor_id'] not in professors:
        raise HTTPException(status_code=400, detail="Professor does not exist")
    for field, value in update_data.items():
        courses[id][field] = value
    return courses[id]

@app.delete("/courses/{id}")
def delete_course(id: int):
    if id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    # Remove enrollments for this course
    to_delete = [key for key in enrollments if key[1] == id]
    for key in to_delete:
        del enrollments[key]
    del courses[id]
    return {"detail": "Course deleted"}

@app.get("/courses/{id}/students", response_model=List[Student])
def get_course_students(id: int):
    if id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    student_ids = [sid for (sid, cid) in enrollments if cid == id]
    return [students[sid] for sid in student_ids if sid in students]

# --- Enrollment Endpoints ---

@app.post("/enrollments", response_model=Enrollment)
def enroll_student(enrollment: EnrollmentCreate):
    sid, cid = enrollment.student_id, enrollment.course_id
    if sid not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    if cid not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    # Check for duplicate enrollment
    if (sid, cid) in enrollments:
        raise HTTPException(status_code=400, detail="Student already enrolled in this course")
    # Check course capacity
    enrolled_count = sum(1 for (s, c) in enrollments if c == cid)
    if enrolled_count >= courses[cid]['max_capacity']:
        raise HTTPException(status_code=400, detail="Course is at full capacity")
    enrollments[(sid, cid)] = enrollment.dict()
    return enrollments[(sid, cid)]

@app.get("/enrollments", response_model=List[Enrollment])
def get_enrollments():
    return list(enrollments.values())

@app.put("/enrollments/{student_id}/{course_id}", response_model=Enrollment)
def update_enrollment(student_id: int, course_id: int, update: EnrollmentUpdate):
    key = (student_id, course_id)
    if key not in enrollments:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    if update.grade is not None:
        enrollments[key]['grade'] = update.grade
        calculate_gpa(student_id)
    return enrollments[key]

@app.delete("/enrollments/{student_id}/{course_id}")
def delete_enrollment(student_id: int, course_id: int):
    key = (student_id, course_id)
    if key not in enrollments:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    del enrollments[key]
    calculate_gpa(student_id)
    return {"detail": "Enrollment deleted"}

# --- GPA Calculation Endpoints (Optional) ---

@app.get("/students/{id}/gpa")
def get_student_gpa(id: int):
    if id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    calculate_gpa(id)
    return {"gpa": students[id]['gpa']}
