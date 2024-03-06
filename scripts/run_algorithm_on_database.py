"""
Run the fair course allocation algorithm,
and write the results and explanations to the database.
"""

#!python3
from cap_data import CapData, logger as cap_data_logger
import fairpyx

import json
import logging

def courses_txt_readable(courses_list:list[str]) -> str :
    """
    INPUT: list of courses, where each course type is a string.
    OUTPUT: The courses listed and numbered, separated by lines, returned as text.
    """
    text = str()
    for index,course_str in enumerate(courses_list):
        text += f"{index+1}. {course_str} \n"
    return text


def experiment(instance):
    algorithms = [
        fairpyx.algorithms.serial_dictatorship,
        fairpyx.algorithms.round_robin, 
        fairpyx.algorithms.bidirectional_round_robin, 
        fairpyx.algorithms.utilitarian_matching, 
        # fairpyx.algorithms.almost_egalitarian_without_donation, # ERROR in finding a fractional egalitarian allocation!
        # fairpyx.algorithms.almost_egalitarian_with_donation,
        fairpyx.algorithms.iterated_maximum_matching_unadjusted, 
        fairpyx.algorithms.iterated_maximum_matching_adjusted
    ]

    for algorithm in algorithms:
        print (f"\n*** {algorithm.__name__} ***\n")
        allocation = fairpyx.divide(algorithm, instance)
        matrix:fairpyx.AgentBundleValueMatrix = fairpyx.AgentBundleValueMatrix(instance, allocation)
        print("  utilitarian value: ", matrix.utilitarian_value())
        print("  egalitarian value: ",matrix.egalitarian_value())
        print("  max envy: ",matrix.max_envy())
        print("  mean envy: ",matrix.mean_envy())

    return matrix

def experiment_random():
    random_instance = fairpyx.Instance.random(
    num_of_agents=70, num_of_items=10, normalized_sum_of_values=1000,
    agent_capacity_bounds=[6,6], item_capacity_bounds=[40,40], item_base_value_bounds=[100,200], item_subjective_ratio_bounds=[0.5,1.5])

    # import sys, logging
    # fairpyx.iterated_maximum_matching.logger.addHandler(logging.StreamHandler(sys.stdout))
    # fairpyx.iterated_maximum_matching.logger.setLevel(logging.INFO)
    return experiment(random_instance)


def run_algorithm(instance, allocation_file):
    algorithm = fairpyx.algorithms.iterated_maximum_matching_adjusted
    string_explanation_logger = fairpyx.StringsExplanationLogger(instance.agents)
    files_explanation_logger = fairpyx.FilesExplanationLogger({
        agent: f"../files/explanations/{agent}.log"
        for agent in instance.agents
    },language='he', mode='w', encoding="utf-8")
    
    allocation = fairpyx.divide(algorithm=algorithm, instance=instance, explanation_logger=files_explanation_logger)

    import json
    with open(allocation_file, "w", encoding="utf-8") as outfile:
        outfile.write(json.dumps(allocation, indent=4, ensure_ascii=False))

    matrix:fairpyx.AgentBundleValueMatrix = fairpyx.AgentBundleValueMatrix(instance, allocation)
    print("\nUtilitarian value: ", matrix.utilitarian_value())
    print("Egalitarian value: ",matrix.egalitarian_value())
    print("Max envy: ",matrix.max_envy())
    print("Mean envy: ",matrix.mean_envy())
    # print("\nExplanations:\n", string_explanation_logger.map_agent_to_explanation())

if __name__ == '__main__':
    from datetime import datetime

    cap_data_logger.addHandler(logging.StreamHandler())
    cap_data_logger.setLevel(logging.ERROR)   # mute warnings

    cap_data = CapData()

    # write the input to a file, for debug only:
    cap_data.write_input_to_json( '../files/input.json')   

    # read the input from the database: 
    (valuations, agent_capacities, item_capacities, agent_conflicts, item_conflicts, course_titles) = \
        cap_data.input_for_fair_allocation_algorithm()
    total_seats_allocated = 1115

    # create a random sample from the input:
    instance = fairpyx.Instance.random_sample(
        max_num_of_agents = total_seats_allocated, 
        max_total_agent_capacity = 2000,
        prototype_agent_conflicts=agent_conflicts,
        prototype_agent_capacities=agent_capacities, 
        prototype_valuations=valuations,
        item_capacities=item_capacities,
        item_conflicts=item_conflicts)


    # Run an experiment on the random sample, for comparing different algorithms:
    # matrix = experiment(instance)

    # compute the allocation for the random sample, and save to a file:
    allocation_file = '../files/allocation.json'
    run_algorithm(instance, allocation_file)
    print("\n")         

    # write explanations for the computed allocation to files, and also to the database:
    with open(allocation_file, "r") as file:
        results = file.read()
        student_results = dict(json.loads(results))
        for student_il_id, courses in student_results.items():
            if student_il_id.startswith("random"):
                continue
            with open(f'../files/explanations/{student_il_id}.log', "r") as file:
                explanation = file.read()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                explanation = f"{now}\n\n{explanation}"
                student_id = cap_data.get_student_id(student_il_id)
                row_count = cap_data.update_student_results(
                        student_id,courses_txt_readable(courses),explanation
                )
                logging.debug(f"{row_count} row/s affected")
                logging.info(f"{student_id}: \n \
                            courses_list: {courses} \n \
                            explanation: {explanation} \n")
                
    
    cap_data.close_mysql_connection()
