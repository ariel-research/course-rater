from cap_data import CapData  
import fairpy.courses as crs

def instance(office_id=1,total_seats_allocated=1115):
    cap_data = CapData(office_id)
    (valuations, agent_capacities, item_capacities, agent_conflicts, item_conflicts) = cap_data.input_for_fair_allocation_algorithm()
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


def run_algorithm(instance):
    algorithm = crs.iterated_maximum_matching_adjusted
    string_explanation_logger = crs.StringsExplanationLogger(instance.agents)
    files_explanation_logger = crs.FilesExplanationLogger({
        agent: f"../files/explanations/{agent}.log"
        for agent in instance.agents
    }, mode='w', encoding="utf-8")

    allocation = crs.divide(algorithm=algorithm, instance=instance, explanation_logger=files_explanation_logger)

    import json
    with open("../files/allocation.json", "w", encoding="utf-8") as outfile:
        outfile.write(json.dumps(allocation, indent=4, ensure_ascii=False))

    matrix:crs.AgentBundleValueMatrix = crs.AgentBundleValueMatrix(instance, allocation)
    print("Utilitarian value: ", matrix.utilitarian_value())
    print("Egalitarian value: ",matrix.egalitarian_value())
    print("Max envy: ",matrix.max_envy())
    print("Mean envy: ",matrix.mean_envy())
    # print("\nExplanations:\n", string_explanation_logger.map_agent_to_explanation())

if __name__ == '__main__':
    instance = instance()
    # matrix = experiment(instance)
    run_algorithm(instance)
