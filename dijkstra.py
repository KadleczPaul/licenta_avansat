import heapq


def find_path(start_id, dest_id, graph):
    if start_id not in graph and any(start_id in neighbors for neighbors in graph.values()) == False:
        if start_id == dest_id: return [start_id], 0
        return [], 0

    distances = {node: float('inf') for node in graph}
    for neighbors in graph.values():
        for neighbor in neighbors:
            if neighbor not in distances:
                distances[neighbor] = float('inf')

    distances[start_id] = 0


    pq = [(0, start_id, [start_id])]

    while pq:
        current_distance, current_node, path = heapq.heappop(pq)

        if current_node == dest_id:
            return path, round(current_distance, 2)


        if current_distance > distances[current_node]:
            continue


        if current_node in graph:
            for neighbor, weight in graph[current_node].items():
                distance = current_distance + weight


                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(pq, (distance, neighbor, path + [neighbor]))


    return [], 0