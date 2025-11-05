# # systems/navigation.py
# import heapq
# from math import dist
# from shapely.geometry import Point, LineString

# class NavigationGraph:
#     def __init__(self, obstacles, width, height, spacing=40):
#         self.nodes = []
#         self.edges = []
#         self.obstacles = obstacles
#         self.build_graph(width, height, spacing)

#     def build_graph(self, width, height, spacing):
#         for x in range(0, width, spacing):
#             for y in range(0, height, spacing):
#                 point = Point(x, y)
#                 if not any(obs.polygon.contains(point) for obs in self.obstacles):
#                     self.nodes.append((x, y))

#         for a in self.nodes:
#             for b in self.nodes:
#                 if a == b: continue
#                 if (abs(a[0]-b[0]) < spacing*1.5) and (abs(a[1]-b[1]) < spacing*1.5):
#                     line = LineString([a, b])
#                     if not any(obs.polygon.intersects(line) for obs in self.obstacles):
#                         self.edges.append((a, b))
    


# def is_line_of_sight_clear(start, end, obstacles):
#     """Check if the line of sight between start and end points is clear of obstacles."""
#     line = LineString([start, end])
#     for obs in obstacles:
#         if obs.polygon.intersects(line):
#             return False
#     return True

# def a_star(start, goal, graph):
#     # ... (a_star function remains unchanged) ...
#     open_set = []
#     heapq.heappush(open_set, (0, start))
#     came_from = {}
#     g = {start: 0}
#     f = {start: dist(start, goal)}

#     while open_set:
#         _, current = heapq.heappop(open_set)
#         if dist(current, goal) < 1: # check if close enough to goal
#             path = reconstruct_path(came_from, current)
#             path.append(goal) # make sure to add the final goal
#             return path

#         # find neighbors from the edges list
#         neighbors = []
#         for a, b in graph.edges:
#             if a == current:
#                 neighbors.append(b)
#             elif b == current:
#                 neighbors.append(a)

#         for n in neighbors:
#             temp_g = g[current] + dist(current, n)
#             if n not in g or temp_g < g[n]:
#                 came_from[n] = current
#                 g[n] = temp_g
#                 f[n] = temp_g + dist(n, goal)
#                 if n not in [i[1] for i in open_set]:
#                     heapq.heappush(open_set, (f[n], n))
#     return None # no path found

# def reconstruct_path(came_from, current):
#     # ... (reconstruct_path function remains unchanged) ...
#     path = [current]
#     while current in came_from:
#         current = came_from[current]
#         path.append(current)
#     path.reverse()
#     return path


# def is_path_clear(start_coords, end_coords, obstacle_polygon):
#     """
#     Check if the direct path (straight line) between two points is clear of an obstacle polygon.
#
#     :param start_coords: Coordinates of the starting point.
#     :param end_coords: Coordinates of the ending point.
#     :param obstacle_polygon: Shapely Polygon object representing the obstacle.
#     :return: True if the path is clear, False if it is not.
#     """
#     path = LineString([start_coords, end_coords])

#     # Check for intersection or touching
#     is_intersecting = path.intersects(obstacle_polygon)

#     # Check if either point is inside the polygon
#     is_start_inside = obstacle_polygon.contains(Point(start_coords))
#     is_end_inside = obstacle_polygon.contains(Point(end_coords))
    
#     # the path is clear if there is no intersection and neither point is inside
#     is_clear = not is_intersecting and not is_start_inside and not is_end_inside
    
#     return is_clear, is_intersecting, is_start_inside, is_end_inside
















