# router.py
from a_star import find_path as a_star_search
from dijkstra import find_path as dijkstra_search


class Router:
    """
    The Router acts as a Facade. 
    It doesn't know about the Database; it only knows about Graphs and Coordinates.
    """

    def __init__(self, graph, coords):
        self.graph = graph
        self.coords = coords

    def get_route(self, start_id, end_id, algorithm="astar"):
        """
        Orchestrates the search based on the chosen algorithm.
        """
        if not self.graph or start_id not in self.graph:
            return {"success": False, "error": "Start location not found in network."}


        if algorithm == "astar":
            path, distance = a_star_search(start_id, end_id, self.graph, self.coords)
        else:
            path, distance = dijkstra_search(start_id, end_id, self.graph)


        if path:
            return {
                "success": True,
                "path": path,
                "distance": round(distance, 2)
            }

        return {"success": False, "error": "No route possible between these points."}