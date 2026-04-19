import heapq
import math

def calculate_h(node_n, node_dest, coords):
    if node_n not in coords or node_dest not in coords:
        return 0
    lat1, lon1 = coords[node_n]
    lat2, lon2 = coords[node_dest]
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def find_path(start_id, dest_id, graph, coords):
    queue = [(0, 0, start_id, [start_id])]
    visited = {}

    while queue:
        f, g, current, path = heapq.heappop(queue)

        if current in visited and visited[current] <= g:
            continue
        visited[current] = g

        if current == dest_id:
            return path, round(g, 2)

        if current in graph:
            for neighbor, weight in graph[current].items():
                new_g = g + weight
                if neighbor not in visited or new_g < visited[neighbor]:
                    h = calculate_h(neighbor, dest_id, coords)
                    new_f = new_g + h
                    heapq.heappush(queue, (new_f, new_g, neighbor, path + [neighbor]))

    return [], 0