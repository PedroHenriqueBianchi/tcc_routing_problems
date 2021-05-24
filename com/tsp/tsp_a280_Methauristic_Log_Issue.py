from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from ortools.init import pywrapinit
from com.utils.intMatrix import IntMatrix
from com.utils.streamToLogger import StreamToLogger
from os import getcwd, environ
from os.path import dirname
from logging import basicConfig, getLogger, StreamHandler, Formatter
from logging import INFO, ERROR, DEBUG, NOTSET
from pytz import timezone
from datetime import datetime
import sys


# environ['GLOG_minloglevel'] = "0"
# environ['GLOG_log_dir'] = r"{}\tsp\files\a280\logs".format(dirname(getcwd()))
# environ['GLOG_logbufsecs'] = "1"
# environ['GLOG_logtostderr'] = "0"
# environ['GLOG_stderrthreshold'] = "3"


file_name = f"tsp_a280_{datetime.now(timezone('America/Sao_Paulo'))}".replace(" ", "_").replace(".", "_").replace(":", "_")
file_name += ".log"

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

basicConfig(filename=r"{}\tsp\files\a280\logs\{}".format(dirname(getcwd()), file_name),
            filemode='a',
            level=NOTSET,
            format=log_format)


logger = getLogger()

# pywrapinit.CppBridge.InitLogging(r"{}\tsp\files\a280\logs\{}".format(dirname(getcwd()), f"{file_name}test"))
# cpp_flags = pywrapinit.CppFlags()
# cpp_flags.logtostderr = False
# cpp_flags.log_prefix = True
# pywrapinit.CppBridge.SetFlags(cpp_flags)

# handler = StreamHandler(sys.stderr)
# handler.setLevel(INFO)
# formatter = Formatter(log_format)
# handler.setFormatter(formatter)
#
# logger.addHandler(handler)
#
# handler = StreamHandler(sys.stdout)
# handler.setLevel(INFO)
# formatter = Formatter(log_format)
# handler.setFormatter(formatter)
#
# logger.addHandler(handler)

# stdout_logger = getLogger('STDOUT')
# slout = StreamToLogger(stdout_logger, INFO)
# sys.stdout = slout
#
# stderr_logger = getLogger('STDERR')
# slerr = StreamToLogger(stderr_logger, ERROR)
# sys.stderr = slerr
#
# stdin_logger = getLogger('STDIN')
# slin = StreamToLogger(stdin_logger, INFO)
# sys.stdin = slin


def create_data_model():
    distance_matrix = IntMatrix(rows_size=280, columns_size=280)
    local_file_path = r"{}\tsp\files\a280\TSP_a280.txt".format(dirname(getcwd()))
    distance_matrix.construct_matrix_from_euclid_int_dist_2d_file(file_path=local_file_path)

    data = {'distance_matrix': distance_matrix.matrix, 'num_vehicles': 1, 'depot': 0}
    return data


def print_solution(manager, routing, solution, strategy, time_limit=None):
    """Prints solution on console."""
    if time_limit is None:
        print(f'Solution achieved by {strategy} strategy')
        logger.info(f'Solution achieved by {strategy} strategy')
    else:
        print(f'Solution achieved by {strategy} strategy with time limit on {time_limit} seconds')
        logger.info(f'Solution achieved by {strategy} strategy with time limit on {time_limit} seconds')
    print(f'Objective: {format(solution.ObjectiveValue())} Unit of Measure')
    logger.info(f'Objective: {format(solution.ObjectiveValue())} Unit of Measure')
    index = routing.Start(0)
    plan_output = 'Route for vehicle 1:\n'
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += f' {format(manager.IndexToNode(index) + 1)} ->'
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += f' {format(manager.IndexToNode(index) + 1)}\n'
    print(plan_output)
    logger.info(plan_output)


def print_opt_solution(opt_file_path, distance_matrix):
    opt_file = open(file=opt_file_path, mode='r')
    plan_output = 'Route on opt file:\n'
    route_distance = 0
    index = 0
    previous_index = 0

    for line in opt_file:
        index = int(line.strip()) - 1
        plan_output += f'{index + 1} -> '
        route_distance += distance_matrix[index][previous_index]
        previous_index = index

    plan_output += '1'
    route_distance += distance_matrix[index][0]

    print("Optimum Solution")
    logger.info("Optimum Solution")
    print(f'Objective: {route_distance} Unit of Measure')
    logger.info(f'Objective: {route_distance} Unit of Measure')
    print(plan_output)
    logger.info(plan_output)


def print_solution_and_opt_solution(manager, routing, solution, search_parameters, opt_file_path, distance_matrix):
    print_solution(manager, routing, solution, search_parameters)
    print('\n')
    print_opt_solution(opt_file_path, distance_matrix)


def main(time_limit, log_search):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])

    ''' Solving with first solution heuristic - PATH_CHEAPEST_ARC '''
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Define strategy to solve the problem
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print_solution(manager, routing, solution, strategy="PATH_CHEAPEST_ARC")

    ''' Solving with first solution heuristic - GLOBAL_CHEAPEST_ARC '''
    # Resetting Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc after reset.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Define strategy to solve the problem
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print_solution(manager, routing, solution, strategy="GLOBAL_CHEAPEST_ARC")

    ''' Solving with Metaheuristic - GUIDED_LOCAL_SEARCH '''
    # Resetting Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc after reset.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Define strategy to solve the problem
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.seconds = time_limit
    search_parameters.log_search = log_search

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print_solution(manager, routing, solution, strategy="Metaheuristic - GUIDED_LOCAL_SEARCH", time_limit=time_limit)

    ''' Printing Optimum solution from TSPLIB '''
    local_opt_solution_file_path = r"{}\tsp\files\a280\TSP_a280_opt_tour.txt".format(dirname(getcwd()))
    print_opt_solution(opt_file_path=local_opt_solution_file_path,
                       distance_matrix=data['distance_matrix'])


if __name__ == '__main__':
    main(time_limit=2, log_search=True)
    # main(time_limit=703, log_search=False)


#Melhorar o log
#Depois partir para soluções do problema de Rio Claro