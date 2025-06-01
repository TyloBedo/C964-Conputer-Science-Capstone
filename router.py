from typing import Callable
from data_import import RoutingData

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class Router:

    def __init__(self, rd:"RoutingData"):

        self.rd = rd

        self.routes:list = []
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

    def _parse_solution(self, solution):

        for team in range(self.rd.teams):
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
                team_data['budget_minutes'] += self.rd.demands[self.manager.IndexToNode(index)]
                team_data['team_size'] = self.rd.team_sizes[team]
                team_data['distance'] += self.routing.GetArcCostForVehicle(
                    previous_index, index, team) / 100 / self.rd.team_sizes[team]




            self.routes.append(team_data)

    def _route_list(self, solution):

        for team in range(self.rd.teams):
            # skip vehicle if team has no jobs
            if not self.routing.IsVehicleUsed(solution, team):
                continue

            index = self.routing.Start(team)
            team_data:list = [self.manager.IndexToNode(index)]

            while not self.routing.IsEnd(index):
                index = solution.Value(self.routing.NextVar(index))
                team_data.append(self.manager.IndexToNode(index))

            self.routes.append(team_data)






if __name__ == "__main__":

    _teams = 8
    _emp = 26

    from pathlib import Path
    data_path: Path = Path(__file__).resolve().parent / "data/test_data1.csv"
    _rd = RoutingData(_teams, _emp, data_path)


    route = Router(_rd)

    route.solve()

    routes = route.routes

    # for _r in routes:
    #     print(_r)

    import pandas as pd

    df = pd.DataFrame.from_records(routes)

    df['people_distance'] = df['distance'] * df['team_size']

    # we assume 30 mph

    df['travel_minutes'] = df['people_distance'] * 2

    df['travel_percent'] = df['travel_minutes'] / (df['budget_minutes'] * 4)




    print(df)
