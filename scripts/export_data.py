"""
Get the algorithm results as Python variables,
and convert them to JSON for uploading to the database.

Note:
    Please be aware that MySQL has a list of reserved words that have special meanings.

    If you encounter this error:
    mysql.connector.errors.ProgrammingError
    1064 (42000): You have an error in your SQL syntax;

    it may be due to using a reserved word in your SQL query.
    To troubleshoot, check the list of MySQL reserved words:
    https://en.wikipedia.org/wiki/List_of_SQL_reserved_words

    To use a reserved word, wrap it with backticks (` `) in your SQL query.

Programmer: Oriya Alperin
Since: 2023-07
"""

from connect2mysql import conn
import json
import pandas as pd
from enum import Enum


def students_list(office_id:str) -> dict:
    student_details = {}
    cursor.execute(f'SELECT api_student.id, student_id, email, first_name, last_name FROM api_student JOIN auth_user ON api_student.user_id = auth_user.id WHERE api_student.office_id={office_id}')
    students = cursor.fetchall()
    for id, student_id,email,first_name,last_name in students:
        student_details[id] = {student_id,email,first_name,last_name}
    
    return student_details


def course_group_list(office_id:str) -> dict:
    """
    INPUT:   a dict containing the algorithm resutls.
    OUTPUT:  two output variables: student_details - details of students, including their allocation; course_details - details of courses.
    """
    course_details = {}
    cursor.execute('SELECT api_course_group.id, api_course.id, name, sum(capacity) FROM api_course JOIN api_course_group ON api_course.course_group_id = api_course_group.id GROUP BY api_course_group.id,api_course.id')
    courses = cursor.fetchall()
    for course_group_id, course_id, name, capacity in courses:
        course_details[course_group_id] = {course_id,name,int(capacity)}

    return course_details

def courses_list(office_id:str) -> dict:
    """
    INPUT:   a dict containing the algorithm resutls.
    OUTPUT:  two output variables: student_details - details of students, including their allocation; course_details - details of courses.
    """
    course_details = {}
    cursor.execute(f'SELECT api_course.id, name, capacity FROM api_course JOIN api_course_group ON api_course.course_group_id = api_course_group.id WHERE api_course_group.office_id={office_id}')
    courses = cursor.fetchall()
    for course_id, name, capacity in courses:
        course_details[course_id] = {name,int(capacity)}

    return course_details


def overlap_courses(office_id:str) -> dict:
    time_courses = []
    overlap_courses = {}

    def add_time_courses(queries: list):
        for query in queries:
            cursor.execute(query)
            courses = cursor.fetchall()
            for course_id,time_start,time_end,day,semester,course_group_id in courses:
                time_courses.append({'course_id':course_id,
                                    'time_start':str(time_start),
                                    'time_end':str(time_end),
                                    'day-sem': (day,semester),
                                    'course_group_id':course_group_id})

    queries = [
        f"SELECT api_course.id, time_start, time_end, day, Semester, course_group_id FROM api_course, api_course_group \
        WHERE api_course_group.id = api_course.course_group_id AND api_course_group.office_id={office_id}",
        
        f"SELECT api_course_time.course_id, api_course_time.time_start, \
        api_course_time.time_end, api_course_time.day, api_course.Semester, api_course.course_group_id \
        FROM api_course_group, api_course RIGHT JOIN api_course_time ON api_course.id  = api_course_time.course_id \
        WHERE api_course_group.id = api_course.course_group_id AND api_course_group.office_id={office_id}"
    ]

    add_time_courses(queries)
    
    for i, c1 in enumerate(time_courses):
        overlap_courses.setdefault(c1['course_id'], [])
        interval1 = pd.Interval(pd.Timestamp(c1['time_start']), pd.Timestamp(c1['time_end']))
        for j, c2 in enumerate(time_courses[i+1:], start=i+1):
                overlap_courses.setdefault(c2['course_id'], [])
                if (c1['course_group_id'] == c2['course_group_id'] and c1['course_id'] !=c2['course_id']) or c1['day-sem'] == c2['day-sem'] and interval1.overlaps(pd.Interval(pd.Timestamp(c2['time_start']), pd.Timestamp(c2['time_end']))):
                        overlap_courses[c1['course_id']].append(c2['course_id'])
                        overlap_courses[c2['course_id']].append(c1['course_id'])                        
                        print(f"{c1['course_id']}: {c1['day-sem']}, {c1['time_start']} - {c1['time_end']} VS {c2['course_id']}: {c2['day-sem']}, {c2['time_start']} - {c2['time_end']}")

                        
    return overlap_courses


if __name__=="__main__":
    import codecs
    cursor = conn.cursor()
    office_id = '1'
    
    #agent_capacities, item_capacities, valuations = mysql2python()
    agent_details = students_list(office_id)
    item_capacities = courses_list(office_id)
    overlap_courses = overlap_courses(office_id)
    print('agent_details:')
    print(agent_details)
    print('item_capacities:')
    print(item_capacities)
    print('overlap courses:')
    print(overlap_courses)
    conn.close()
