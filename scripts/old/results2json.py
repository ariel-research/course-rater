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

def rankers_list():
    cursor = conn.cursor()
    rankers = []
    cursor.execute('SELECT DISTINCT student_id FROM api_ranking')
    rankings = cursor.fetchall()
    for student_id, in rankings:
        rankers.append(student_id)
    return rankers

def id2data(results: dict, office_id:str) -> tuple[dict,dict]:
    """
    INPUT:   a dict containing the algorithm resutls.
    OUTPUT:  two output variables: student_details - details of students, including their allocation; course_details - details of courses.
    """
    cursor = conn.cursor()

    rankers= rankers_list()
    print("rankers:", rankers)
    agent_capacities = {}
    student_details =[]
    cursor.execute(f'SELECT api_student.id, student_id, email, first_name, last_name FROM api_student JOIN auth_user ON api_student.user_id = auth_user.id WHERE api_student.office_id={office_id}')
    students = cursor.fetchall()
    for id, student_id,email,first_name,last_name in students:
        agent_capacities[id] = {student_id,email,first_name,last_name}
        student_data = {'id': id, 'student_id' : student_id, 'email': email, 'first_name': first_name, 'last_name': last_name}

        if id in rankers:
            try:
                courses = results.get(id)
                print("courses: ",courses)
                student_data['courses']=courses

            except Exception as e:
                raise Exception(f'The student with id no. {student_id} (aka {first_name} {last_name}) ranked courses, but is not found in courses dictonary')

        student_details.append(student_data)

    item_capacities = {}
    course_details = []
    cursor.execute('SELECT api_course_group.id, api_course.id, name, sum(capacity) FROM api_course JOIN api_course_group ON api_course.course_group_id = api_course_group.id GROUP BY api_course_group.id,api_course.id')
    courses = cursor.fetchall()
    for id, course_id, name, capacity in courses:
        item_capacities[id] = {course_id,name,capacity}
        course_data = {'id': id, 'course_id' : course_id, 'name': name, 'capacity': int(capacity)}
        course_details.append(course_data)

    conn.close()
    return (student_details,course_details)



if __name__=="__main__":
    import codecs
    results = {}
    office_id = '1'
    #agent_capacities, item_capacities, valuations = mysql2python()
    agent_details, item_details = id2data(results,office_id)
    print('agent_details:')
    print(agent_details)
    print('item_capacities:')
    print(item_details)
    with codecs.open('../files/student_details.json', 'w', encoding="utf-8") as file:
        json.dump(agent_details, file, indent=4, ensure_ascii=False)
    with codecs.open('../files/course_details.json', 'w', encoding="utf-8") as file:
        json.dump(item_details, file, indent=4, ensure_ascii=False)
