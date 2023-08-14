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

from database_utils import Database
from collections import defaultdict
import json
import pandas as pd
from enum import Enum

class CapData():

    def __init__(self, office_id:str,results=None):
        self.database = Database()
        self.office_id = office_id
        self.results = results
        
    def students_list(self) -> dict:
        student_details = {}
        query = f'SELECT api_student.id, student_id, email, first_name, last_name FROM api_student JOIN auth_user ON api_student.user_id = auth_user.id WHERE api_student.office_id={self.office_id}'
        students = self.database.execute_query(query)
        for id, student_id,email,first_name,last_name in students:
            student_details[id] = {student_id,email,first_name,last_name}
        
        return student_details


    def course_group_list(self) -> dict:
        """
        OUTPUT:  course_details - details of group courses.
        """
        course_details = {}
        query = f'SELECT api_course_group.id, api_course.id, name, sum(capacity) FROM api_course JOIN api_course_group ON api_course.course_group_id = api_course_group.id GROUP BY api_course_group.id,api_course.id WHERE api_course_group.office_id={self.office_id}'
        courses = self.database.execute_query(query)
        for course_group_id, course_id, name, capacity in courses:
            course_details[course_group_id] = {course_id,name,int(capacity)}

        return course_details

    def courses_list(self) -> dict:
        """
        OUTPUT:  course_details - details of courses.
        """
        course_details = {}
        query = f'SELECT api_course.id, name, capacity FROM api_course JOIN api_course_group ON api_course.course_group_id = api_course_group.id WHERE api_course_group.office_id={self.office_id}'
        courses = self.database.execute_query(query)
        for course_id, name, capacity in courses:
            course_details[course_id] = {name,int(capacity)}

        return course_details

    def course_times_list(self) -> list:
        
        course_times = []

        def add_course_times(queries: list):
            for query in queries:
                courses = self.database.execute_query(query)
                for course_id,time_start,time_end,day,semester,course_group_id in courses:
                    course_times.append({'course_id':course_id,
                                        'time_start':str(time_start),
                                        'time_end':str(time_end),
                                        'day-sem': (day,semester),
                                        'course_group_id':course_group_id})

        queries = [
            f"SELECT api_course.id, time_start, time_end, day, Semester, course_group_id FROM api_course, api_course_group \
            WHERE api_course_group.id = api_course.course_group_id AND api_course_group.office_id={self.office_id}",
            
            f"SELECT api_course_time.course_id, api_course_time.time_start, \
            api_course_time.time_end, api_course_time.day, api_course.Semester, api_course.course_group_id \
            FROM api_course_group, api_course RIGHT JOIN api_course_time ON api_course.id  = api_course_time.course_id \
            WHERE api_course_group.id = api_course.course_group_id AND api_course_group.office_id={self.office_id}"
        ]

        add_course_times(queries)
        course_times.sort(key=lambda course : course['course_id'])    

        return course_times
        

    def overlap_courses(self) -> dict:
        """
        OUTPUT: a dictionary where the keys represent courses, 
                and the corresponding values list the courses 
                that students cannot enroll in simultaneously with the given course.        
        """
        overlap_courses = defaultdict(list)
        course_times = self.course_times_list()
        
        for i, c1 in enumerate(course_times):
            interval1 = pd.Interval(pd.Timestamp(c1['time_start']), pd.Timestamp(c1['time_end']))
            for j, c2 in enumerate(course_times[i+1:], start=i+1):
                    if (c1['course_group_id'] == c2['course_group_id'] and c1['course_id'] !=c2['course_id']) or c1['day-sem'] == c2['day-sem'] and interval1.overlaps(pd.Interval(pd.Timestamp(c2['time_start']), pd.Timestamp(c2['time_end']))):
                            overlap_courses[c1['course_id']].append(c2['course_id'])
                            overlap_courses[c2['course_id']].append(c1['course_id'])                        
                            #print(f"{c1['course_id']}: {c1['day-sem']}, {c1['time_start']} - {c1['time_end']} VS {c2['course_id']}: {c2['day-sem']}, {c2['time_start']} - {c2['time_end']}")
                
        return dict(overlap_courses)


if __name__=="__main__":
    import codecs
    office_id = '1'
    cap_data = CapData(office_id)
    #agent_capacities, item_capacities, valuations = mysql2python()
    students_list = cap_data.students_list()
    courses_list = cap_data.courses_list()
    course_times = cap_data.course_times_list()
    overlap_courses = cap_data.overlap_courses()
    print('students_list:')
    print(students_list)
    print('courses_list:')
    print(courses_list)
    print('overlap courses:')
    print(overlap_courses)
    print('course times:')
    print(course_times)
    cap_data.database.close_connection()