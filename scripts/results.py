#!python3
from cap_data import CapData
import fairpy.courses as crs
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

def instance(cap_data:CapData,total_seats_allocated=1115):
    (valuations, agent_capacities, item_capacities, agent_conflicts, item_conflicts, course_titles) = cap_data.input_for_fair_allocation_algorithm()
    instance = crs.Instance.random_sample(
        max_num_of_agents = total_seats_allocated, 
        max_total_agent_capacity = total_seats_allocated,
        prototype_agent_conflicts=agent_conflicts,
        prototype_agent_capacities=agent_capacities, 
        prototype_valuations=valuations,
        item_capacities=item_capacities,
        item_conflicts=item_conflicts)
    return instance

def experiment(instance):
    algorithms = [
        crs.serial_dictatorship, 
        crs.round_robin, 
        crs.bidirectional_round_robin, 
        crs.utilitarian_matching, 
        # crs.almost_egalitarian_without_donation, # ERROR in finding a fractional egalitarian allocation!
        # crs.almost_egalitarian_with_donation,
        crs.iterated_maximum_matching_unadjusted, 
        crs.iterated_maximum_matching_adjusted
    ]

    for algorithm in algorithms:
        print (f"\n*** {algorithm.__name__} ***\n")
        allocation = crs.divide(algorithm, instance)
        matrix:crs.AgentBundleValueMatrix = crs.AgentBundleValueMatrix(instance, allocation)
        print("  utilitarian value: ", matrix.utilitarian_value())
        print("  egalitarian value: ",matrix.egalitarian_value())
        print("  max envy: ",matrix.max_envy())
        print("  mean envy: ",matrix.mean_envy())

    return matrix

def experiment_random():
    random_instance = crs.Instance.random(
    num_of_agents=70, num_of_items=10, normalized_sum_of_values=1000,
    agent_capacity_bounds=[6,6], item_capacity_bounds=[40,40], item_base_value_bounds=[100,200], item_subjective_ratio_bounds=[0.5,1.5])

    # import sys, logging
    # crs.iterated_maximum_matching.logger.addHandler(logging.StreamHandler(sys.stdout))
    # crs.iterated_maximum_matching.logger.setLevel(logging.INFO)
    return experiment(random_instance)


def run_algorithm(instance, allocation_file):
    algorithm = crs.iterated_maximum_matching_adjusted
    string_explanation_logger = crs.StringsExplanationLogger(instance.agents)
    files_explanation_logger = crs.FilesExplanationLogger({
        agent: f"../files/explanations/{agent}.log"
        for agent in instance.agents
    },language='he', mode='w', encoding="utf-8")
    
    allocation = crs.divide(algorithm=algorithm, instance=instance, explanation_logger=files_explanation_logger)

    import json
    with open(allocation_file, "w", encoding="utf-8") as outfile:
        outfile.write(json.dumps(allocation, indent=4, ensure_ascii=False))

    matrix:crs.AgentBundleValueMatrix = crs.AgentBundleValueMatrix(instance, allocation)
    print("Utilitarian value: ", matrix.utilitarian_value())
    print("Egalitarian value: ",matrix.egalitarian_value())
    print("Max envy: ",matrix.max_envy())
    print("Mean envy: ",matrix.mean_envy())
    # print("\nExplanations:\n", string_explanation_logger.map_agent_to_explanation())

if __name__ == '__main__':
    cap_data = CapData()
    cap_data.write_input_to_json( '../files/input.json')

    import sys
    sys.exit()

    # Compute the output:

    instance = instance(cap_data)
    # matrix = experiment(instance)
    
    allocation_file = '../files/allocation.json'
    run_algorithm(instance, allocation_file)

    with open(allocation_file, "r") as file:
                results = file.read()
                student_results = dict(json.loads(results))
                for student_il_id, courses in student_results.items():
                    if student_il_id.startswith("random"):
                        continue
                    with open(f'../files/explanations/{student_il_id}.log', "r") as file:
                        explantion = file.read()
                        student_id = cap_data.get_student_id(student_il_id)
                        row_count = cap_data.update_student_results(
                             student_id,courses_txt_readable(courses),explantion
                            )
                        logging.debug(f"{row_count} row/s affected")
                        logging.info(f"{student_id}: \n \
                                    courses_list: {courses} \n \
                                    explanation: {explantion} \n")
    cap_data.close_mysql_connection()
