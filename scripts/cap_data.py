"""
Connect to the CAP database, perform data operations,
and retrieve data associated with the given office_id.

Programmer: Oriya Alperin
Since: 2023-07
"""

from database_utils import Database
from collections import defaultdict
import json
import pandas as pd
from unidecode import unidecode

import logging
logger = logging.getLogger(__name__)

class CapData():
    """
    Connects to the CAP database, performs data operations,
    and retrieves data associated with the given office_id.
    """
    def __init__(self, office_id:str=1,results=None):
        self.database = Database()
        self.office_id = office_id
        self.results = results
    
    def close_mysql_connection(self):
        self.database.close_connection()
    
    def students_list(self, condition:str="1") -> dict:
        """
        OUTPUT:  student_details - details of students.
        """
        #if self.students:
        #    return self.students

        student_details = {}
        self.students_by_il_id = {}
        query = f"""
            SELECT api_student.id, student_id, email, first_name, last_name, amount_elective, program, date_joined, last_login
            FROM api_student 
            JOIN auth_user ON api_student.user_id = auth_user.id 
            WHERE api_student.office_id={self.office_id}
            AND {condition}
            """
        students = self.database.execute_query(query)
        for student_id, student_il_id,email,first_name,last_name,amount_elective, program,date_joined,last_login in students:
            student_details[student_id] = {'student_id': student_il_id,'email': email,'first_name': first_name,'last_name': last_name, 'amount_elective':amount_elective, 'program': program, 'date_joined': date_joined, 'last_login': last_login}
            self.students_by_il_id[str(student_il_id)] = str(student_id)

        # svaing calls:
        self.students = student_details
        return student_details

    def get_student_id(self,student_il_id: str) -> str:
        """
        INPUT: student Israeli id.
        OUTPUT: the corresponding student entity id.
        """
        if not hasattr(self,'students_by_il_id'):
            self.students_list()
        # print(self.students_by_il_id)
        return self.students_by_il_id[student_il_id]


    def course_group_list(self) -> dict:
        """
        OUTPUT: course_details - details of group courses.
        """
        course_details = {}
        query = f'SELECT api_course_group.id, api_course.id, name, sum(capacity) FROM api_course JOIN api_course_group ON api_course.course_group_id = api_course_group.id WHERE api_course_group.office_id={self.office_id} GROUP BY api_course_group.id,api_course.id'
        courses = self.database.execute_query(query)
        for course_group_id, course_id, name, capacity in courses:
            course_details[course_group_id] = {'course_id': course_id,'name': name, 'capacity': int(capacity)}
        return course_details

    def courses_list(self) -> dict:
        """
        OUTPUT: course_details - details of group courses.
        """
        course_details = {}
        query = f'SELECT api_course.id, api_course.course_id, name, capacity FROM api_course JOIN api_course_group ON api_course.course_group_id = api_course_group.id WHERE api_course_group.office_id={self.office_id}'
        courses = self.database.execute_query(query)
        for course_id,course_num_id, name, capacity in courses:
            course_details[course_id] = {'course_id': course_num_id, 'name': name, 'capacity': int(capacity)}
        return course_details

    def ranking_list(self) -> dict:
        """
        OUTPUT: studnt_rankings dictionary in this format: [student_id][course_id] contains
                the details of the student's course ranking
        """
        stuednt_rankings = defaultdict(dict)
        query = f"""
            SELECT api_ranking.student_id, course_id, `rank`, is_acceptable 
            FROM api_ranking,api_student 
            WHERE api_ranking.student_id = api_student.id 
            AND api_student.office_id = {self.office_id}
            """
        rankings = self.database.execute_query(query)
        for student_id, course_id, rank, is_acceptable in rankings:
            stuednt_rankings[student_id][course_id] = {"rank": rank, "is_acceptable":bool(is_acceptable)}
        stuednt_rankings = dict(stuednt_rankings)
        return stuednt_rankings
        

    def rankers_list(self):
        """
        OUTPUT: rankers list that contains all students id of students that rank courses 
        """
        rankers = []
        query = f'SELECT DISTINCT student_id FROM api_ranking, api_student \
        WHERE api_ranking.student_id = api_student.id AND api_student.office_id = {self.office_id}'
        rankings = self.database.execute_query(query)
        for student_id, in rankings:
            rankers.append(student_id)
        return rankers


    def course_times_list(self) -> list:
        """
        OUTPUT: course_times - details of time courses.
        """
        course_times = []

        def add_course_times(queries: list):
            """
            for each query, get time data and add it to course_times list.
            """
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
                    same_course = c1['course_group_id'] == c2['course_group_id'] and c1['course_id'] !=c2['course_id']
                    is_overlap = interval1.overlaps(pd.Interval(pd.Timestamp(c2['time_start']), pd.Timestamp(c2['time_end'])))
                    same_time =  c1['day-sem'] == c2['day-sem'] and is_overlap
                    if same_course or same_time:
                            overlap_courses[c1['course_id']].append(c2['course_id'])
                            overlap_courses[c2['course_id']].append(c1['course_id'])                        
                            #print(f"{c1['course_id']}: {c1['day-sem']}, {c1['time_start']} - {c1['time_end']} VS {c2['course_id']}: {c2['day-sem']}, {c2['time_start']} - {c2['time_end']}")
                
        return dict(overlap_courses)


    def course_title_list(self) -> dict:
        """
        OUTPUT: a dictionary where the keys represent course ids,
        and the corresponding values are the course titles.
        """
        courses_group_list = self.course_group_list()
        course_times = self.course_times_list()
        courses_list = self.courses_list()
        # print("courses_list",courses_list)

        from collections import Counter
        counter = Counter([course['name'] for course in courses_list.values()])
        # print(counter)

        def time_hm(time: str) -> str:
            """
            INPUT: time string in HH:MM:SS format
            OUTPUT: time string in HH:MM format
            """
            return time.rsplit(':',1)[0]

        def title(course_time):
            """
            INPUT: course_time - course details, including their times 
            OUTPUT: generated course title 
            """
            course_group_id = course_time['course_group_id']
            name = courses_group_list[course_group_id]['name']
            if counter[name]==1:
                return name
            else:
                day,sem = course_time['day-sem']
                time = time_hm(course_time['time_start'])# + " - "+ time_hm(course_time['time_end'])
                return f"{name} ביום {day} {time}"

        return {course_time['course_id']: title(course_time) for course_time in course_times}


    def input_for_fair_allocation_algorithm(self, transliterate_hebrew=False, hide_studentid=False) -> tuple[dict,dict,dict,dict,dict]:
        students_list = self.students_list() # "date_joined > '2024-01-01'")
        print("\nNum students: ", len(students_list))
        # for k,d in students_list.items():
        #     print("   "+d["first_name"]+"-"+d["last_name"]+"-"+d["email"]+" "+str(d["date_joined"])+" "+str(d["last_login"]))

        courses_list = self.courses_list()
        course_times = self.course_times_list()
        overlap_courses = self.overlap_courses()
        rankings = self.ranking_list()
        course_titles = self.course_title_list()

        def sid(student_num):
            if hide_studentid:
                return f"s{student_num}"
            else:
                return students_list[student_num]["student_id"]

        def cid(course_num):
            course_title = course_titles[course_num]
            if transliterate_hebrew:
                course_title = unidecode(course_title)
            return course_title

        valuations = defaultdict(dict)
        agent_conflicts = defaultdict(set)
        for student_num,student_details in students_list.items():
        # for student_num, student_values in rankings.items():
            student_id = student_details["student_id"]
            if student_num in rankings:
                student_values = rankings[student_num]
                for course_num, student_course_values in student_values.items():
                    if course_num not in course_titles:
                        logger.warn(f"Course num {course_num} is in the ranking of student num {student_num} with id {student_id}, but not in the list of course titles.")
                        continue
                    valuations[sid(student_num)][cid(course_num)] = student_course_values["rank"]
                    if not student_course_values["is_acceptable"]:
                        agent_conflicts[sid(student_num)].add(cid(course_num))
                # print(f"There are rankings for student {student_details}!")
            else:
                # print(f"No rankings for student {student_details}!")
                pass

        print("\nNum students with rankings: ", len(valuations))
        print("Student names with rankings: ", list(valuations.keys()))

        agent_capacities = {sid(student_num): student_details["amount_elective"] for student_num,student_details in students_list.items()
            if student_num in rankings}
        item_capacities  = {cid(course_num): course_details["capacity"] for course_num,course_details in courses_list.items()}

        item_conflicts = {
            cid(course_num):  {cid(conflicted_course_num) for conflicted_course_num in conflicted_courses}
            for course_num, conflicted_courses in overlap_courses.items()
        }
        return (dict(valuations), agent_capacities, item_capacities, dict(agent_conflicts), item_conflicts, course_titles)

    
    def results_full_info(self, results: dict) -> tuple[dict,dict]:
        """
        OUTPUT:  two output variables: student_details - details of students, including their allocation;
                 course_details - details of courses.
        """
        rankers = self.rankers_list()
        students = self.students_list()
        courses = self.courses_list()        
        for student_id, student_info in students:
            if student_id in rankers:
                try:
                    student_courses = results.get(student_id)
                    print("courses: ",student_courses)
                    students[student_id]['courses']=[course_details[course_id] for course_id in student_courses]
                except Exception as e:
                    student_id = student_info['student_id']
                    student_name = student_info['first_name'] + " " + student_info['last_name']
                    raise Exception(
                        f'The student with id no. {student_id}, aka {student_name}, ranked courses, but is not found in courses dictonary'
                    )
        return students
    

    def update_student_results(self,student_id: str,courses_txt: str ,explanation:str ):
        """
        INPUT: student entity ID, text containing algorithm-generated course results,
               and an explanation of the algorithm's iterations.
        OUTPUT: Number of affected rows resulting from the insertion/update of student result info in MySQL database.
        """

        query = "INSERT INTO api_result_info (student_id, courses_txt, explanation) " \
                "VALUES (%s, %s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "courses_txt = VALUES(courses_txt), explanation = VALUES(explanation)"

        try:
            values = (student_id, courses_txt, explanation)
            return self.database.execute_query(query,values)
        except Exception as e:
            raise explanation("Error: failed to insert/update student result info")

    def write_input_to_json(self, filename:str):
        input = { }
        # input_tuple = cap_data.input_for_fair_allocation_algorithm()
        (input["valuations"], input["agent_capacities"], input["item_capacities"], input["agent_conflicts"], input["item_conflicts"], _) = \
            self.input_for_fair_allocation_algorithm(transliterate_hebrew=True, hide_studentid=True)

        for agent in input["agent_conflicts"].keys():
            input["agent_conflicts"][agent] = list(input["agent_conflicts"][agent])

        for item in input["item_conflicts"].keys():
            input["item_conflicts"][item] = list(input["item_conflicts"][item])

        agent_capacities = input["agent_capacities"].values()
        print("sum capacities: ", sum(agent_capacities), "num capacity: ",  len(agent_capacities), "avg capacity: ", sum(agent_capacities)/len(agent_capacities), )

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(input, file)

def print_results():
    results = {}

    students_list = cap_data.students_list()
    ("date_joined > '2000-01-14'")
    ("last_login > '2024-01-14'")
    print("students_list: ",students_list, "\n")
    print("students num: ",len(students_list), "\n")

    courses_list = cap_data.courses_list()
    course_times = cap_data.course_times_list()
    overlap_courses = cap_data.overlap_courses()
    rankings = cap_data.ranking_list()
    course_titles = cap_data.course_title_list()

    (valuations, agent_capacities, item_capacities, agent_conflicts, item_conflicts,titles) = \
        cap_data.input_for_fair_allocation_algorithm()
    
    print ("\n valuations = ", valuations)
    print ("\n agent_capacities = ", agent_capacities)
    print ("\n item_capacities = ", item_capacities)
    print ("\n agent_conflicts = ", agent_conflicts)
    print ("\n item_conflicts = ", item_conflicts)



if __name__=="__main__":
    import codecs, sys
    office_id = '1'
    cap_data = CapData(office_id)
    cap_data.write_input_to_json("../files/input2.json")
    cap_data.close_mysql_connection()
