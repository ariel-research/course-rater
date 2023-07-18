import sqlite3
from collections import defaultdict

def sid(student_id:int):
    return f"s{student_id}"

def cid(course_id:int):
    return f"c{course_id}"

def sqlite2python(database_filename:str) -> tuple[dict,dict,dict]:
    """
    INPUT:   path to an sqlite3 database containing input for course-allocation problem.
    OUTPUT:  the three input variables: valuations, agent_capacities, item_capacities.
    """
    conn = sqlite3.connect(database_filename)
    cursor = conn.cursor()

    agent_capacities = {}
    cursor.execute('SELECT api_student.id, amount_elective FROM api_student JOIN auth_user ON api_student.user_id = auth_user.id')
    students = cursor.fetchall()
    for student_id, amount_elective in students:
        agent_capacities[sid(student_id)] = amount_elective

    item_capacities = {}
    cursor.execute('SELECT api_course.id, sum(capacity) FROM api_course JOIN api_course_group ON api_course.course_group_id = api_course_group.id GROUP BY api_course_group.id')
    courses = cursor.fetchall()
    for course_id, capacity in courses:
        item_capacities[cid(course_id)] = capacity

    valuations = defaultdict(dict)
    cursor.execute('SELECT student_id, course_id, rank FROM api_ranking')
    rankings = cursor.fetchall()
    for student_id, course_id, rank in rankings:
        valuations[sid(student_id)][cid(course_id)] = rank
    valuations = dict(valuations)

    conn.close()

    return (agent_capacities, item_capacities, valuations)

if __name__=="__main__":
    DATABASE_FILENAME = 'dbold.sqlite3'
    agent_capacities, item_capacities, valuations = sqlite2python(DATABASE_FILENAME)

    print('agent_capacities:')
    print(agent_capacities)
    print('item_capacities:')
    print(item_capacities)
    print('valuations:')
    print(valuations)
