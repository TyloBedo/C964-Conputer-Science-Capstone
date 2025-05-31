from data_import import RoutingData

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class Router:

    def __init__(self, rd:RoutingData):
        self.solution = None

        self.rd = rd
        self.dm:list[list] = rd.distance_matrix
        self.vehicles:int = rd.teams # change to len capacity?
        self.capacity:list[int] = rd.vehicle_capacities
        self.demands:list[int] = rd.demands


        self.manager = pywrapcp.RoutingIndexManager(
            len(self.dm), self.vehicles, 0
        )
        self.routing = pywrapcp.RoutingModel(self.manager)

        self._set_dimensions()


    def _set_dimensions(self):
        # Set max distance traveled by any vehicle.
        # Once we add capacity maybe not required? We'll see.

        # Create and register a transit callback.
        transit_callback_index = self.routing.RegisterTransitCallback(self.get_distance)
        demand_callback_index = self.routing.RegisterUnaryTransitCallback(self.demand_callback)

        # Define cost of each arc.
        ### I think we adjust this for 2-3-4 person teams..
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        self.routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            15000,  # vehicle maximum travel distance miles * 100
            True,  # start cumul to zero
            "Distance",
        )
        self.routing.GetDimensionOrDie("Distance").SetGlobalSpanCostCoefficient(100)


        self.routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            self.capacity,  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity",
        )


    def solve(self):
        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

        self.solution = self.routing.SolveWithParameters(search_parameters)

    ###############################
    #
    #   "Callback" functions start
    #
    ###############################

    def demand_callback(self, l1:int):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node:int = self.manager.IndexToNode(l1)
        return self.demands[from_node]

    def get_distance(self, l1:int, l2:int):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node:int = self.manager.IndexToNode(l1)
        to_node:int = self.manager.IndexToNode(l2)
        return self.dm[from_node][to_node]

    ###############################
    #
    #   "Callback" functions end
    #
    ###############################

    def print_solution(self):
        """Prints solution on console."""
        if not self.solution:
            print("No solution found !")
            return

        print(f"Objective: {self.solution.ObjectiveValue()}")
        total_route_distance:int = 0
        for vehicle_id in range(self.vehicles):
            if not self.routing.IsVehicleUsed(self.solution, vehicle_id):
                continue
            index = self.routing.Start(vehicle_id)
            plan_output = f"Route for vehicle {vehicle_id}:\n"
            route_distance = 0
            while not self.routing.IsEnd(index):
                plan_output += f" {self.manager.IndexToNode(index)} -> "
                previous_index = index
                index = self.solution.Value(self.routing.NextVar(index))
                route_distance += self.routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            plan_output += f"{self.manager.IndexToNode(index)}\n"
            plan_output += f"Distance of the route: {route_distance / 100} miles\n"
            print(plan_output)

            total_route_distance += route_distance

        print(f"Total of the route distances: {total_route_distance / 100} miles")






if __name__ == "__main__":

    _teams = 8
    _emp = 26

    rd = RoutingData(_teams, _emp)


    route = Router(rd)

    route.solve()

    route.print_solution()