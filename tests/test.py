# import pygame
# from shapely.geometry import Point, Polygon
# import networkx as nx
# from shapely.ops import nearest_points
# from math import hypot
# from shapely.geometry import LineString

# # ---------------- Pathfinding Core ----------------

# EPS = 1e-6

# def point_coords(pt):
#     return (pt.x, pt.y)

# def dist(a, b):
#     return hypot(a[0]-b[0], a[1]-b[1])

# def project_outside(pt, polygons, push_eps=1e-6):
#     p = Point(pt) if not isinstance(pt, Point) else pt
#     for poly in polygons:
#         if poly.contains(p):
#             nearest_on_boundary = nearest_points(p, poly.boundary)[1]
#             centroid = poly.centroid
#             dx, dy = nearest_on_boundary.x - centroid.x, nearest_on_boundary.y - centroid.y
#             norm = (dx*dx + dy*dy) ** 0.5 or 1.0
#             ux, uy = dx/norm, dy/norm
#             candidate = Point(nearest_on_boundary.x + ux*push_eps,
#                               nearest_on_boundary.y + uy*push_eps)
#             step = push_eps
#             while any(poly.contains(candidate) for poly in polygons):
#                 step *= 10
#                 candidate = Point(nearest_on_boundary.x + ux*step,
#                                   nearest_on_boundary.y + uy*step)
#             return candidate
#     return p

# def visible(a, b, polygons):
#     seg = LineString([a, b])
#     for poly in polygons:
#         if seg.crosses(poly) or seg.within(poly):
#             return False
#     return True

# def build_visibility_graph(start_pt, goal_pt, polygons):
#     nodes = [('start', point_coords(start_pt)), ('goal', point_coords(goal_pt))]
#     vid = 0
#     for poly in polygons:
#         coords = list(poly.exterior.coords)[:-1]
#         for c in coords:
#             nodes.append((f'v{vid}', (c[0], c[1])))
#             vid += 1

#     G = nx.Graph()
#     for name, coord in nodes:
#         G.add_node(name, coord=coord)

#     for i in range(len(nodes)):
#         for j in range(i+1, len(nodes)):
#             ni, ci = nodes[i]
#             nj, cj = nodes[j]
#             if visible(ci, cj, polygons):
#                 G.add_edge(ni, nj, weight=dist(ci, cj))
#     return G

# def shortest_path_between(start, goal, polygons):
#     spt = project_outside(Point(start), polygons)
#     gpt = project_outside(Point(goal), polygons)
#     G = build_visibility_graph(spt, gpt, polygons)

#     def heuristic(u, v):
#         cu, cv = G.nodes[u]['coord'], G.nodes[v]['coord']
#         return dist(cu, cv)

#     try:
#         path_nodes = nx.astar_path(G, 'start', 'goal', heuristic=heuristic, weight='weight')
#     except nx.NetworkXNoPath:
#         return None, spt, gpt

#     path = [G.nodes[n]['coord'] for n in path_nodes]
#     # smoothing
#     smoothed = [path[0]]
#     i = 0
#     while i < len(path) - 1:
#         j = len(path) - 1
#         while j > i + 1:
#             if visible(path[i], path[j], polygons):
#                 break
#             j -= 1
#         smoothed.append(path[j])
#         i = j
#     return smoothed, spt, gpt





# class Pathfinding:
#     pass




# # ---------------- Pygame UI ----------------

# pygame.init()
# WIDTH, HEIGHT = 800, 600
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Polygon Pathfinding Demo")
# font = pygame.font.SysFont(None, 24)

# clock = pygame.time.Clock()

# polygons = []
# current_poly = []
# start = None
# goal = None
# path = None

# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#         elif event.type == pygame.MOUSEBUTTONDOWN:
#             x, y = event.pos
#             # Left click: start/goal
#             if event.button == 1:
#                 if not start:
#                     start = (x, y)
#                 elif not goal:
#                     goal = (x, y)
#                     if polygons and start and goal:
#                         path, start_p, goal_p = shortest_path_between(start, goal, polygons)
#                         start, goal = (start_p.x, start_p.y), (goal_p.x, goal_p.y)
#                 else:
#                     start = (x, y)
#                     goal = None
#                     path = None

#             # Right click: add polygon point
#             elif event.button == 3:
#                 current_poly.append((x, y))

#             # Middle click: finish polygon
#             elif event.button == 2:
#                 if len(current_poly) > 2:
#                     polygons.append(Polygon(current_poly))
#                 current_poly = []

#         elif event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_RETURN:  # Enter to close polygon
#                 if len(current_poly) > 2:
#                     polygons.append(Polygon(current_poly))
#                 current_poly = []
#             elif event.key == pygame.K_c:  # C to clear
#                 polygons.clear()
#                 current_poly = []
#                 start = goal = path = None

#     # Draw
#     screen.fill((30, 30, 30))

#     # Obstacles
#     for poly in polygons:
#         pygame.draw.polygon(screen, (100, 100, 100), list(poly.exterior.coords), 0)

#     if len(current_poly) > 1:
#         pygame.draw.lines(screen, (150, 150, 150), False, current_poly, 2)

#     # Path
#     if path:
#         pygame.draw.lines(screen, (0, 150, 255), False, path, 4)
#         print("Path:", path)

#     # Start / Goal
#     if start:
#         pygame.draw.circle(screen, (0, 255, 0), (int(start[0]), int(start[1])), 6)
#         print("Start" , start)
#     if goal:
#         pygame.draw.circle(screen, (255, 0, 0), (int(goal[0]), int(goal[1])), 6)
#         print("Goal" , goal)

#     # Info text
#     txt = font.render("Left click: start/goal | Right: draw obstacle | Middle/Enter: finish | C: clear", True, (200,200,200))
#     screen.blit(txt, (10, 10))

#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()




from shapely.geometry import Point, Polygon, LineString
from shapely.ops import nearest_points
from math import hypot
import networkx as nx


class Pathfinding:
    EPS = 1e-6

    def __init__(self, obstacles):
        """
        Initialize the pathfinding system.

        Args:
            obstacles (list[Polygon]): List of shapely Polygon obstacles.
        """
        self.obstacles = obstacles

    # ---------------- Internal utilities ----------------
    @staticmethod
    def _dist(a, b):
        return hypot(a[0] - b[0], a[1] - b[1])

    @staticmethod
    def _point_coords(pt):
        return (pt.x, pt.y)

    def _project_outside(self, pt, push_eps=1e-6):
        """
        If the given point is inside an obstacle, move it to the nearest
        point outside the obstacle boundary.
        """
        p = Point(pt) if not isinstance(pt, Point) else pt
        for poly in self.obstacles:
            if poly.contains(p):
                nearest_on_boundary = nearest_points(p, poly.boundary)[1]
                centroid = poly.centroid
                dx = nearest_on_boundary.x - centroid.x
                dy = nearest_on_boundary.y - centroid.y
                norm = (dx * dx + dy * dy) ** 0.5 or 1.0
                ux, uy = dx / norm, dy / norm

                candidate = Point(
                    nearest_on_boundary.x + ux * push_eps,
                    nearest_on_boundary.y + uy * push_eps,
                )

                step = push_eps
                while any(poly.contains(candidate) for poly in self.obstacles):
                    step *= 10
                    candidate = Point(
                        nearest_on_boundary.x + ux * step,
                        nearest_on_boundary.y + uy * step,
                    )
                return candidate
        return p

    def _visible(self, a, b):
        """
        Check if segment (a,b) doesn't cross any obstacle.
        """
        seg = LineString([a, b])
        for poly in self.obstacles:
            if seg.crosses(poly) or seg.within(poly):
                return False
        return True

    def _build_visibility_graph(self, start_pt, goal_pt):
        """
        Build a visibility graph including the start, goal, and obstacle vertices.
        """
        nodes = [
            ("start", self._point_coords(start_pt)),
            ("goal", self._point_coords(goal_pt)),
        ]

        vid = 0
        for poly in self.obstacles:
            coords = list(poly.exterior.coords)[:-1]  # skip closing point
            for c in coords:
                nodes.append((f"v{vid}", (c[0], c[1])))
                vid += 1

        G = nx.Graph()
        for name, coord in nodes:
            G.add_node(name, coord=coord)

        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                ni, ci = nodes[i]
                nj, cj = nodes[j]
                if self._visible(ci, cj):
                    G.add_edge(ni, nj, weight=self._dist(ci, cj))
        return G

    # ---------------- Public API ----------------
    def find_path(self, start, goal):
        """
        Compute the shortest path between start and goal considering obstacles.

        Args:
            start (tuple[float,float] | Point)
            goal (tuple[float,float] | Point)

        Returns:
            path (list[(x,y)]) or None,
            start_projected (Point),
            goal_projected (Point)
        """
        spt = self._project_outside(Point(start))
        gpt = self._project_outside(Point(goal))

        G = self._build_visibility_graph(spt, gpt)

        def heuristic(u, v):
            cu, cv = G.nodes[u]["coord"], G.nodes[v]["coord"]
            return self._dist(cu, cv)

        try:
            path_nodes = nx.astar_path(
                G, "start", "goal", heuristic=heuristic, weight="weight"
            )
        except nx.NetworkXNoPath:
            return None, spt, gpt

        path = [G.nodes[n]["coord"] for n in path_nodes]

        # --- simple smoothing ---
        smoothed = [path[0]]
        i = 0
        while i < len(path) - 1:
            j = len(path) - 1
            while j > i + 1:
                if self._visible(path[i], path[j]):
                    break
                j -= 1
            smoothed.append(path[j])
            i = j

        return smoothed, spt, gpt



from shapely.geometry import Polygon

# Create obstacles
obstacles = [
    Polygon([(1, 1), (4, 1), (4, 4), (1, 4)]),
    Polygon([(6, 2), (8, 3), (7.5, 5), (6, 4)]),
]

pf = Pathfinding(obstacles)

start = (0, 0)
goal = (7, 3)  # even if inside an obstacle

path, s_proj, g_proj = pf.find_path(start, goal)
print("Path:", path)
