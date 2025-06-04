from typing import Callable
import pandas as pd
from .routing_data import RoutingData
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class Router:

    def __init__(self, teams:int, employees:int, rd:"RoutingData"):

        # Teams must have between two and four people.
        # Adjust team or employee count down to match if required.
        if teams * 2 > employees:
            teams = employees / 2
        if teams * 4 < employees:
            employees = teams * 4

        self.rd = rd
        self.teams:int = teams # vehicles,
        self.employees:int = employees
        self._set_demands()

        self.routes:list = []
        self.manager = pywrapcp.RoutingIndexManager(
            len(self.rd.dm), self.teams, 0
        )
        self.routing = pywrapcp.RoutingModel(self.manager)

        self._set_dimensions()

    # O(n)
    def _set_demands(self):
        # demands is budget minutes per jobs.
        self.demands:list[int] = self.rd.df['budget'].tolist()
        total_demands:int = self.rd.df['budget'].sum()

        # interestingly, demands * 1.1 gives better results sometimes
        # 300 is max cleaning minutes per person
        # 1.25 is a modifier because OT is okay.
        max_demand:float = 300 * 1.25

        if total_demands / self.employees > max_demand:
            # need some more testing on this. Doesn't catch all errors.
            raise CapacityError("Not enough employees!")

        # we need to figure out how to distribute 2 3 or 4 person teams
        # ideally we will also test different distributions...
        # for now lets just distribute out the employees we have..
        self.team_sizes = [self.employees // self.teams] * self.teams
        for i in range(self.employees % self.teams ):
            self.team_sizes[i] += 1

        self.capacities:list[int] = \
            [int(capacity * max_demand) for capacity in self.team_sizes]

    # O(n)
    def _set_dimensions(self):

        distance_callback_index = self.routing.RegisterTransitCallback(self.get_distance)

        for vehicle in range(self.teams):
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
            self.capacities,
            True,
            "Capacity",
        )

    # O(...) good question
    def solve(self):
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

        solution = self.routing.SolveWithParameters(search_parameters)
        if not solution:
            print("No solution found !")
            return
        self._parse_solution(solution)

    ###############################
    #
    #   "Callback" functions start
    #
    ###############################

    # O(n)
    def make_cost_callback(self, vehicle) -> Callable[[int, int], int]:
        def cost_callback(l1:int, l2:int) -> int:
            return self.get_distance(l1, l2) * self.team_sizes[vehicle]

        return cost_callback
    # O(n)
    def demand_callback(self, l1:int) -> int:
        """Returns the demand of the node."""
        from_node:int = self.manager.IndexToNode(l1)
        return self.demands[from_node]

    # O(n)
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


    def _parse_solution(self, solution):
        for team in range(self.teams):
            if not self.routing.IsVehicleUsed(solution, team):
                continue

            index = self.routing.Start(team)
            team_data:dict = {"route":[self.manager.IndexToNode(index)],
                              'budget_minutes':0, 'distance':0, 'team':team,
                              'team_size': None}

            while not self.routing.IsEnd(index):
                previous_index = index
                index = solution.Value(self.routing.NextVar(index))
                team_data['route'].append(self.manager.IndexToNode(index))
                team_data['budget_minutes'] += self.demands[self.manager.IndexToNode(index)]
                team_data['team_size'] = self.team_sizes[team]
                team_data['distance'] += self.routing.GetArcCostForVehicle(
                    previous_index, index, team) / 100 / self.team_sizes[team]

            self.routes.append(team_data)

        self.df = pd.DataFrame.from_records(self.routes)
        self.df['people_distance'] = self.df['distance'] * self.df['team_size']
        self.df['travel_minutes'] = self.df['people_distance'] * 2
        self.df['travel_percent'] = self.df['travel_minutes'] / (self.df['budget_minutes'] * 4)
        self.df['route_string'] = self.df['route'].apply(self.get_route_string)

    def get_route_string(self, route):
        route_string: str = ""
        for location in route:
            name = self.rd.df.loc[location, 'location']
            route_string += f"{name} -> "
        return route_string[:-4]



class CapacityError(Exception):
    pass



