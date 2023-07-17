import sqlite3


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
        agent_capacities[student_id] = amount_elective

    item_capacities = {}
    cursor.execute('SELECT api_course.id, sum(capacity) FROM api_course JOIN api_course_group ON api_course.course_group_id = api_course_group.id GROUP BY api_course_group.id')
    courses = cursor.fetchall()
    for name, capacity in courses:
        item_capacities[name] = capacity

    valuations = {}
    cursor.execute('SELECT student_id, course_id, rank FROM api_ranking')
    rankings = cursor.fetchall()
    for student_id, course_id, rank in rankings:
        if student_id not in valuations:
            valuations[student_id] = {}
        valuations[student_id][course_id] = rank

    conn.close()

    return (agent_capacities, item_capacities, valuations)

if __name__=="__main__":
    DATABASE_FILENAME = 'db.sqlite3'
    agent_capacities, item_capacities, valuations = sqlite2python(DATABASE_FILENAME)

    print('agent_capacities:')
    print(agent_capacities)
    print('item_capacities:')
    print(item_capacities)
    print('valuations:')
    print(valuations)