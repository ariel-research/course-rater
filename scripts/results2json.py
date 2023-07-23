"""
Get the algorithm results as Python variables,
and convert them to JSON for uploading to the database.

Programmer: Oriya Alperin
Since: 2023-07
"""

import sqlite3
import json

def rankers_list(database_filename:str):
    conn = sqlite3.connect(database_filename)
    cursor = conn.cursor()
    rankers = []
    cursor.execute('SELECT DISTINCT student_id rank FROM api_ranking')
    rankings = cursor.fetchall()
    for student_id in rankings:
        rankers.append(student_id)
    return rankers

def id2data(database_filename:str, results: dict) -> tuple[dict,dict]:
    """
    INPUT:   path to an sqlite3 database containing input for course-allocation problem.
    OUTPUT:  the two input variables: agent_capacities, item_capacities.
    """
    conn = sqlite3.connect(database_filename)
    cursor = conn.cursor()
    
    rankers= rankers_list(database_filename)
    agent_capacities = {}
    student_details =[]
    cursor.execute('SELECT api_student.id, student_id, email, first_name, last_name FROM api_student JOIN auth_user ON api_student.user_id = auth_user.id')
    students = cursor.fetchall()
    for id, student_id,email,first_name,last_name in students:
        agent_capacities[id] = {student_id,email,first_name,last_name}
        student_data = {'id': id, 'student_id' : student_id, 'email': email, 'first_name': first_name, 'last_name': last_name}
        
        if id in rankers:
            try:
                courses = results.get(id)
                student_data.append(courses)

            except Exception as e:
                raise('The student with id no. {} (aka {} {}) ranked courses, but is not found in courses dictonary'.format(student_id,first_name,last_name))
            
        student_details.append(student_data)
        
    item_capacities = {}
    course_details = []
    cursor.execute('SELECT api_course_group.id, api_course.id, name, sum(capacity) FROM api_course JOIN api_course_group ON api_course.course_group_id = api_course_group.id GROUP BY api_course_group.id')
    courses = cursor.fetchall()
    for id, course_id, name, capacity in courses:
        item_capacities[id] = {course_id,name,capacity}
        course_data = {'id': id, 'course_id' : course_id, 'name': name, 'capacity': capacity}
        course_details.append(course_data)



    conn.close()

    return (student_details,course_details)

"""def valuations_detailed(agent_details:dict, item_details: dict, placements: dict) -> dict:
    student_courses = {}
    for sudent,courses in placements:
        
"""


if __name__=="__main__":
    DATABASE_FILENAME = '../dbold.sqlite3'
    results = {}
    #agent_capacities, item_capacities, valuations = sqlite2python(DATABASE_FILENAME)
    agent_details, item_details = id2data(DATABASE_FILENAME, results)
    print('agent_details:')
    print(agent_details)
    print('item_capacities:')
    print(item_details)
    with open('../files/student_details.json', 'w') as file:
        json.dump(agent_details, file, indent=4, ensure_ascii=False)
    with open('../files/course_details.json', 'w') as file:
        json.dump(item_details, file, indent=4, ensure_ascii=False)
