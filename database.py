import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import cache
from contextlib import contextmanager
import numpy as np
import openpyxl
import pandas as pd
from helpertools import elegant_time, student_report


class Rank(Enum):
    Admin = 1
    Assistant = 2
    Teacher = 3


@dataclass
class Account:
    id: int
    username: str
    password: str
    name: str
    email: str
    rank: Rank | str
    blocked: bool = False
    birthday: str = None

    def __eq__(self, other):
        return other.id == self.id


@dataclass
class Lecture:
    name: str
    duration: float
    duration_simplified: str
    stage_id: int
    lecture_id: int
    stage: str
    assistant: str = None
    absence: bool = True


RANKS_NAMES = {1: "Admiral", 2: "Assistant", 3: "Teacher"}


@dataclass
class Student:
    name: str
    email: str
    id: int
    qr_id: int
    stage_id: int


@dataclass
class LectureInfo:
    id: int
    name: str
    course: str
    weeks: int
    duration: int | float
    stage_id: int
    user_id: int
    assistant_id: int
    is_lab: bool = False
    association_link: str = None
    signed_weeks: int = 0


@dataclass
class Attendance:
    pk: int
    student: list[Student]
    lecture: LectureInfo


@contextmanager
def get_db_connection():
    conn = sqlite3.connect('attendance.db')
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_db_cursor(conn):
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()


def gather_lectures(stage_id):
    with get_db_connection() as conn, get_db_cursor(conn) as cursor:
        cursor.execute("SELECT Lecture_name FROM Lectures WHERE Stage_id = ?", (stage_id,))
        lectures = cursor.fetchall()
    return np.ravel(lectures)


def get_database():
    conn = sqlite3.connect('attendance.db')
    Cursor = conn.cursor()
    Cursor.execute('''SELECT User_id, User_name, User_email, User_username, User_password, User_rank FROM Users''')
    rows = Cursor.fetchall()
    data = []
    for row in rows:
        id = row[0]
        name = row[1]
        email = row[2]
        username = row[3]
        password = row[4]
        rank = row[5]
        data.append(Account(id=id, username=username, password=password, name=name, email=email, rank=Rank(rank)))
    conn.commit()
    conn.close()
    return data


def get_theories_lectures():
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute("SELECT Lecture_name FROM Lectures WHERE Is_LAB = 0")
    data = Cursor.fetchall()
    Cursor.close()
    Connection.close()
    return np.ravel(data)


def get_users():
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute('''SELECT * FROM Users''')
    data = Cursor.fetchall()
    result = []
    for row in data:
        result.append(Account(id=row[0],
                              name=row[1],
                              email=row[2],
                              username=row[3],
                              password=row[4],
                              birthday=row[5],
                              rank=RANKS_NAMES.get(row[-1])))
    Connection.commit()
    Connection.close()
    return result


def add_new(name, email, username, password, birthday, authority, rank):
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute(
        "INSERT INTO Users (User_name, User_email, User_username, User_password, User_dob, User_authority, User_rank) "
        f"VALUES ('{name}', '{email}', '{username}', '{password}', '{birthday}', '{authority}', '{rank}')")
    Connection.commit()
    Connection.close()


def get_from_id(id):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()

    user_id = id
    query = '''
    SELECT Lectures.Lecture_name, Lectures.duration, Lectures.Stage_id, Stages.Stage_description, Lectures.Lecture_id, COALESCE(Users.User_name, 'No Assistant') AS Assistant_name
    FROM Lectures
    LEFT JOIN Stages ON Lectures.Stage_id = Stages.Stage_id
    LEFT JOIN Users ON Lectures.User_assistant_id = Users.User_id
    WHERE Lectures.User_id = {};
    '''.format(user_id)
    Cursor.execute(query)
    result = Cursor.fetchall()
    final_result = []
    for row in result:
        final_result.append(Lecture(name=row[0], duration=row[1], stage_id=row[2], stage=row[3], lecture_id=row[4],
                                    assistant=row[5],
                                    duration_simplified=elegant_time(row[1])))
    Connection.commit()
    Connection.close()
    return final_result


def get_students(stage_id):
    with get_db_connection() as conn, get_db_cursor(conn) as cursor:
        All_Stage_Students = f"SELECT Student_id, Student_qr_code_id, Student_name, Student_email, Stage_id FROM Students WHERE Stage_id = {stage_id}"
        cursor.execute(All_Stage_Students)
        Display = cursor.fetchall()
        result = dict()
        for value in Display:
            result[value[1]] = Student(id=value[0], qr_id=value[1], name=value[2], email=value[3], stage_id=value[4])
    return result


def get_students_emails(stage_id):
    with get_db_connection() as conn, get_db_cursor(conn) as cursor:
        All_Stage_Students = f"SELECT Student_email FROM Students WHERE Stage_id = {stage_id}"
        cursor.execute(All_Stage_Students)
        result = cursor.fetchall()
    return np.ravel(result)


def get_teachers_emails():
    with get_db_connection() as conn, get_db_cursor(conn) as cursor:
        users = f"SELECT User_email FROM Users"
        cursor.execute(users)
        result = cursor.fetchall()
    return np.ravel(result)


def delete_student(student_id):
    with get_db_connection() as conn, get_db_cursor(conn) as cursor:
        cursor.execute("DELETE FROM Attendance WHERE Student_id=?", (student_id,))
        cursor.execute("DELETE FROM Students WHERE Student_id=?", (student_id,))
        conn.commit()


def get_stages():
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute("SELECT Stage_description FROM Stages")
    data = Cursor.fetchall()
    Connection.commit()
    Connection.close()
    return np.ravel(data)


def reset_password(user_id, new_password):
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute("UPDATE Users SET User_password = ? WHERE User_id = ?", (new_password, user_id))
    Connection.commit()
    Cursor.close()
    Connection.close()


def get_lectures_info():
    with get_db_connection() as conn, get_db_cursor(conn) as cursor:
        cursor.execute("SELECT * FROM Lectures")
        lectures = cursor.fetchall()
        result = []
        for lecture in lectures:
            print(lecture)
            result.append(LectureInfo(id=lecture[0], name=lecture[1], course=lecture[2], duration=lecture[3],
                                      weeks=lecture[4], stage_id=lecture[5], user_id=lecture[6],
                                      assistant_id=lecture[7], is_lab=lecture[8], association_link=lecture[9]))
        conn.commit()
    return result


get_lectures_info()


def get_teachers_by_stage(stage_id):
    with get_db_connection() as conn, get_db_cursor(conn) as cursor:
        cursor.execute('''SELECT DISTINCT Users.User_email, Assistant.User_email 
                          FROM Lectures 
                          JOIN Users ON Lectures.User_id = Users.User_id 
                          LEFT JOIN Users AS Assistant ON Lectures.User_assistant_id = Assistant.User_id 
                          WHERE Lectures.Stage_id = ?;''', (stage_id,))
        Instructors = cursor.fetchall()

        cursor.execute('''SELECT User_email, NULL
                          FROM Users 
                          WHERE User_rank = 1 OR User_rank = 2;''')
        HeadQuarters = cursor.fetchall()
        result = set(filter(None, np.ravel(Instructors + HeadQuarters)))
    return result


def get_lectures():
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute("SELECT * FROM Lectures")
    lectures = Cursor.fetchall()
    Connection.commit()
    Connection.close()
    return lectures


def get_teachers_names():
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute("SELECT User_name FROM Users WHERE User_rank = 3")
    data = Cursor.fetchall()
    Connection.commit()
    Connection.close()
    return np.ravel(data)


@cache
def get_weeks_name(lecture_name):
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute(
        "SELECT Lecture_weeks FROM Lectures WHERE Lecture_name = ?", (lecture_name,))
    result = Cursor.fetchall()
    Connection.commit()
    Connection.close()
    return result[0][0]


def get_duration(lecture_name):
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute(
        "SELECT Duration FROM Lectures WHERE Lecture_name = ?", (lecture_name,))
    result = Cursor.fetchall()
    Connection.commit()
    Connection.close()
    return result[0][0]


@cache
def get_weeks(lecture_id):
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute(
        "SELECT Lecture_weeks FROM Lectures WHERE Lecture_id = ?", (lecture_id,))
    result = Cursor.fetchall()
    Connection.commit()
    Connection.close()
    return result[0][0]


def delete_lecture(pk):
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute(
        "DELETE FROM Lectures Where Lecture_id = ?", (pk,))
    Connection.commit()
    Connection.close()


def get_teacher_id(teacher_name):
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute(f"SELECT User_id FROM Users WHERE User_name = '{teacher_name}'")
    result = Cursor.fetchall()
    Connection.commit()
    Connection.close()
    return result[0][0] if result else None


def insert_data(lecture_name: str, course_name: str, duration: float, lecture_weeks: int, stage_id: int,
                user_id: int, user_assistant_id: int = None, is_lab=False, association_link=None):
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute(
        "INSERT INTO Lectures (Lecture_name, Course_name, Duration, Lecture_weeks, Stage_id, User_id, "
        "User_assistant_id, Is_LAB, Association_Link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (lecture_name, course_name, duration, lecture_weeks, stage_id, user_id, user_assistant_id, is_lab,
         association_link))
    Connection.commit()
    Connection.close()


# THIS MUSIC IS SOOOO "GOD"
def delete_user(user_id):
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()

    # Delete attendance records for the user's lectures
    Cursor.execute('''DELETE FROM Attendance WHERE Student_id IN (
        SELECT Student_id FROM Students WHERE Stage_id IN (
            SELECT Stage_id FROM Lectures WHERE User_id = ?
        )
    );''', (user_id,))

    Cursor.execute('DELETE FROM Lectures WHERE User_id = ?;', (user_id,))

    Cursor.execute('DELETE FROM Users WHERE User_id = ?;', (user_id,))

    Connection.commit()
    Connection.close()


def get_teacher_name(teacher_id):
    if teacher_id is None:
        return
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute(f"SELECT User_name FROM Users WHERE User_id = ?", (teacher_id,))
    result = Cursor.fetchall()
    Connection.commit()
    Connection.close()
    return None if not result else result[0][0]


def new_student(name, email, stage_id, qr_id):
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute(
        "INSERT INTO Students (Student_name, Student_email, Stage_id, Student_qr_code_id) VALUES (?, ?, ?, ?)",
        (name, email, stage_id, qr_id))
    Connection.commit()
    Connection.close()


def delete_from_id(user_id):
    Connection = sqlite3.connect('attendance.db')
    Cursor = Connection.cursor()
    Cursor.execute("DELETE FROM Users WHERE User_id = ?", (user_id,))
    Connection.commit()
    Connection.close()


@dataclass(slots=True)
class SimplifiedData:
    pk: int
    student_id: int
    student_name: str
    student_email: str
    student_qr_code: int
    stage_name: str
    stage_id: int
    lecture_id: int
    lecture_name: str
    lecture_week: int
    absence: bool
    date: str


class SpecialLecture:
    __slots__ = ['name', 'total', 'last_value', 'duration', 'taken', 'all_values']

    def __init__(self, name, total, duration):
        self.name = name
        self.total = total
        self.last_value = 0
        self.duration = duration
        self.taken = 0
        self.all_values = []

    def test(self, value):
        if value not in self.all_values:
            self.all_values.append(value)
            self.last_value = value
            self.taken += 1

    def taken_duration(self):
        return self.duration * self.taken

    def total_duration(self):
        return self.duration * self.total


@cache
def lab(connection, lecture_name):
    cursor = connection.cursor()
    cursor.execute("SELECT Association_Link FROM Lectures WHERE Lecture_Name=?", (lecture_name,))
    result = cursor.fetchone()
    return result and result[0]


@cache
def lab_connection(lecture_name):
    with sqlite3.connect('attendance.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT Association_Link FROM Lectures WHERE Lecture_Name=?", (lecture_name,))
        result = cursor.fetchone()
        return result and result[0]


def delete_attendances(stage_id):
    with sqlite3.connect('attendance.db') as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Attendance WHERE Stage_id = ?', (stage_id,))
        connection.commit()


def get_attendances(stage_id):
    with sqlite3.connect('attendance.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Attendance WHERE Stage_id = ?", (stage_id,))
        datum = cursor.fetchall()
        all_lectures = gather_lectures(stage_id)
        result: dict[str, dict[str, int]] = {k.name: {l: 0 for l in all_lectures} for k in
                                             get_students(stage_id).values()}
        real_lectures: dict[str, SpecialLecture] = {k: SpecialLecture(k, get_weeks_name(k), get_duration(k))
                                                    for k in all_lectures}

        for data in datum:
            data = SimplifiedData(*data)
            print(data)
            data.stage_id = stage_id
            if data.absence == "Attendant":
                result[data.student_name][data.lecture_name] += 1
            real_lectures[data.lecture_name].test(data.lecture_week)

        real_result = result.copy()
        for k, v in result.items():
            for r, j in v.copy().items():
                theory = real_lectures[r]
                ass_lecture = lab(connection, theory.name)
                if ass_lecture:
                    c = result[k][ass_lecture]
                    real = real_lectures[ass_lecture]
                    real_result[k][ass_lecture] = round(((real.taken_duration() - c * real.duration) +
                                                         ((theory.taken_duration() - (j * theory.duration)) / 2)
                                                         ) * 100 / (
                                                                theory.total_duration() / 2 + real.total_duration()),
                                                        2)
                    real_result[k].pop(r)
                    continue

                if real_result[k][r] == 0:
                    real_result[k][r] += round((theory.taken_duration() - j * theory.duration) * 100 /
                                               theory.total_duration(), 2)

    return real_result


class AdminLecture(SpecialLecture):
    def __init__(self, name, total, duration, stage, lab_lecture: SpecialLecture | str = None):
        super().__init__(name, total, duration)
        self.taken_weeks = [k.name for k in get_students(stage)]
        self.lab_lecture = lab_lecture if isinstance(lab_lecture, SpecialLecture) else AdminLecture(lab_lecture,
                                                                                                    total / 2,
                                                                                                    duration / 2,
                                                                                                    stage)


def get_students_states(stage_id, lecture_name, week):
    result = []
    with get_db_connection() as conn, get_db_cursor(conn) as cursor:
        cursor.execute("SELECT * FROM Attendance Where Stage_id = ? AND Lecture_name = ? AND Lecture_week = ?",
                       (stage_id, lecture_name, week))
        fetch = cursor.fetchall()
        for i in fetch:
            s = SimplifiedData(*i)
            result.append(s)

    return result


def get_admin_report(stage_id, lecture: SpecialLecture, week_name='Week'):
    all_students = list(sorted(get_students_states(stage_id, lecture.name, 1), key=lambda k: k.student_name))
    result = {week: get_students_states(stage_id, lecture.name, week)
              for week in range(1, lecture.total + 1)}
    excel_result = {lecture.name: [student.student_name for student in all_students]}
    for week in range(1, lecture.total + 1):
        excel_result[f'{week_name} {week}'] = [None] * len(all_students)
    excel_result['Total Absent Hours'] = [0] * len(all_students)
    for week, students in result.items():
        week = f'{week_name} {week}'
        if students:
            lecture.test(week)
            for student in students:
                index = excel_result[lecture.name].index(student.student_name)
                excel_result[week][index] = student.absence
                if student.absence == 'Absent':
                    excel_result['Total Absent Hours'][index] += lecture.duration
    return excel_result


# print(get_admin_report(4, SpecialLecture("Total Quality Management", 15, 2)))

def filter_lectures(stage_id):
    lectures = list(gather_lectures(stage_id))
    for lecture in lectures:
        n = lab_connection(lecture)
        if n:
            lectures.remove(n)
    return lectures


def make_admin_report(stage_id, output="results.xlsx"):
    lectures = filter_lectures(stage_id)
    writer = pd.ExcelWriter(output, "xlsxwriter")
    student_report(get_attendances(stage_id)).to_excel(writer, "Report", index=False)
    for lecture in lectures:
        origin = lab_connection(lecture)
        if origin:
            total = dict()
            f = SpecialLecture(origin, get_weeks_name(origin), get_duration(origin))
            first = get_admin_report(stage_id, f)
            s = SpecialLecture(lecture, get_weeks_name(lecture), get_duration(lecture) / 2)
            second = get_admin_report(stage_id, s, week_name="Week Lab")
            total['Theory'] = first
            total['Lab'] = second
            total['Total Hours'] = [
                first['Total Absent Hours'][i] + second['Total Absent Hours'][i]
                for i in range(len(first['Total Absent Hours']))]
            total['Percentage'] = []
            for hours in total['Total Hours']:
                total['Percentage'].append(round((hours /
                                                  (f.total_duration() + s.total_duration()) * 100), 2))
            first.update(second)
            first.pop("Total Absent Hours")
            first.pop(s.name)
            first["Total Absent Hours"] = total["Total Hours"]
            first['Percentage'] = total['Percentage']
            first['State'] = []
            for v in first['Percentage']:
                if v >= 15:
                    n = "فصل نهائي"
                elif v >= 10:
                    n = "فصل اولي"
                elif v >= 5:
                    n = "أنذار"
                elif v >= 3:
                    n = "تنبيه"
                else:
                    n = "لا يوجد حالة"
                first['State'].append(n)
            print(first)
            final = pd.DataFrame(first, index=None)
            final.to_excel(writer, sheet_name=f.name, index=False)
        else:
            f = SpecialLecture(lecture, get_weeks_name(lecture), get_duration(lecture))
            first = get_admin_report(stage_id, f)
            first['Percentage'] = []
            first['State'] = []
            for hours in first['Total Absent Hours']:
                print(f.taken_duration(), f.total_duration(), hours)
                print((f.taken_duration() - hours))
                first['Percentage'].append(
                    round(((hours / f.total_duration()) * 100), 2))
            for v in first['Percentage']:
                if v >= 15:
                    n = "فصل نهائي"
                elif v >= 10:
                    n = "فصل اولي"
                elif v >= 5:
                    n = "أنذار"
                elif v >= 3:
                    n = "تنبيه"
                else:
                    n = "لا يوجد حالة"
                first['State'].append(n)
            final = pd.DataFrame(first, index=None)
            final.to_excel(writer, sheet_name=f.name, index=False)
    writer.close()


