from typing import Callable

from data_import import RoutingData

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class Router:

    def __init__(self, rd:RoutingData):
        self.solution = None

        self.rd = rd

        self.manager = pywrapcp.RoutingIndexManager(
            len(self.rd.dm), self.rd.teams, 0
        )
        self.routing = pywrapcp.RoutingModel(self.manager)

        self._set_dimensions()

    def _set_dimensions(self):

        distance_callback_index = self.routing.RegisterTransitCallback(self.get_distance)

        for vehicle in range(self.rd.teams):
            callback = self.make_cost_callback(vehicle)
            callback_index = self.routing.RegisterTransitCallback(callback)
            self.routing.SetArcCostEvaluatorOfVehicle(callback_index, vehicle)

        self.routing.AddDimension(
            distance_callback_index,
            0,
            15000,  # vehicle maximum travel distance miles * 100
            True,
            "Distance",
        )
        self.routing.GetDimensionOrDie("Distance").SetGlobalSpanCostCoefficient(100)


        demand_callback_index = self.routing.RegisterUnaryTransitCallback(self.demand_callback)
        self.routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            self.rd.capacities,
            True,
            "Capacity",
        )


    def solve(self):
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

    def make_cost_callback(self, vehicle) -> Callable[[int, int], int]:

        def cost_callback(l1:int, l2:int) -> int:
            return self.get_distance(l1, l2) * self.rd.team_sizes[vehicle]

        return cost_callback


    def demand_callback(self, l1:int) -> int:
        """Returns the demand of the node."""
        from_node:int = self.manager.IndexToNode(l1)
        return self.rd.demands[from_node]

    def get_distance(self, l1:int, l2:int) -> int:
        """Returns the distance between the two nodes."""
        from_node:int = self.manager.IndexToNode(l1)
        to_node:int = self.manager.IndexToNode(l2)
        return self.rd.dm[from_node][to_node]

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

        total_route_distance:int = 0
        for vehicle_id in range(self.rd.teams):

            if not self.routing.IsVehicleUsed(self.solution, vehicle_id):
                continue

            people:int = self.rd.team_sizes[vehicle_id]
            route_distance:int = 0
            budget_minutes:int = 0
            index = self.routing.Start(vehicle_id)

            print(f"Route for vehicle {vehicle_id}:")
            plan_output = ""
            while not self.routing.IsEnd(index):
                plan_output += f"{self.manager.IndexToNode(index)} -> "
                previous_index = index
                index = self.solution.Value(self.routing.NextVar(index))
                budget_minutes += self.rd.demands[self.manager.IndexToNode(index)]
                route_distance += self.routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            plan_output += f"{self.manager.IndexToNode(index)}"

            print(plan_output)

            print(f"Distance of the route: {route_distance / 100 / people} miles")
            print(f"Number of people: {people} people")
            print(f"Total Cleaning Minutes: {budget_minutes} minutes\n")


            total_route_distance += route_distance / people

        print(f"Total of the route distances: {total_route_distance / 100} miles")






if __name__ == "__main__":

    _teams = 8
    _emp = 26

    _rd = RoutingData(_teams, _emp)


    route = Router(_rd)

    route.solve()

    route.print_solution()