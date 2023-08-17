"""
Read the lists of courses, students and rankings from the sqlite database,
and convert them to Python variables.

Programmer: Oriya Alperin
Since: 2023-07
"""


from connect2mysql import conn
from collections import defaultdict

def sid(student_id:int):
    return f"s{student_id}"

def cid(course_id:int):
    return f"c{course_id}"

def offices_list() -> list:
    cursor = conn.cursor()
    cursor.execute(f'SELECT id, name from api_office')
    offices = cursor.fetchall()
    conn.close()
    return offices

def mysql2python(office_id:str) -> tuple[dict,dict,dict]:
    """
    INPUT:   path to an sqlite3 database containing input for course-allocation problem.
    OUTPUT:  the three input variables: valuations, agent_capacities, item_capacities.
    """
    import numpy as np
    FORBIDDEN_ALLOCATION = -np.inf

    cursor = conn.cursor()

    agent_capacities = {}
    cursor.execute(f'SELECT api_student.id, amount_elective FROM api_student JOIN auth_user ON api_student.user_id = auth_user.id WHERE api_student.office_id ={office_id}')
    students = cursor.fetchall()
    for student_id, amount_elective in students:
        agent_capacities[sid(student_id)] = amount_elective

    item_capacities = {}
    cursor.execute(f'SELECT api_course.id, sum(capacity) FROM api_course JOIN api_course_group ON api_course.course_group_id = api_course_group.id WHERE api_course_group.office_id = {office_id} GROUP BY api_course_group.id, api_course.id')
    courses = cursor.fetchall()
    for course_id, capacity in courses:
        item_capacities[cid(course_id)] = int(capacity)

    valuations = defaultdict(dict)
    agent_conflicts = defaultdict(set)
    cursor.execute('SELECT student_id, course_id, `rank`, is_acceptable FROM api_ranking')
    rankings = cursor.fetchall()
    #rankings = filter(lambda ranking: sid(ranking[0]) in agent_capacities, rankings)
    for student_id, course_id, rank, is_acceptable in rankings:
        if sid(student_id) in agent_capacities:
            is_acceptable = bool(is_acceptable)
            if not is_acceptable:
                agent_conflicts[sid(student_id)].add(cid(course_id))
                # rank = FORBIDDEN_ALLOCATION
            valuations[sid(student_id)][cid(course_id)] = rank
    conn.close()
    return (agent_capacities, item_capacities, dict(valuations), dict(agent_conflicts))

if __name__=="__main__":
    """
    # uncomment to select a different office"
    offices = offices_list()
    print("offices list: (id, name):\n" ,offices)
    office_id = input("enter the required office id: ")
    """

    office_id = '1'
    agent_capacities, item_capacities, valuations, agent_conflicts = mysql2python(office_id)

    print('agent_capacities:')
    print(agent_capacities)
    print('item_capacities:')
    print(item_capacities)
    print('valuations:')
    print(valuations)
    print('agent_conflicts:')
    print(agent_conflicts)
