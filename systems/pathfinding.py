# systems/pathfinding.py - EMERGENCY FIX
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import nearest_points
from shapely.prepared import prep
from math import hypot, sqrt
import networkx as nx
from typing import List, Tuple, Optional, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PathfindingResult:
    """Result of a pathfinding query."""
    path: Optional[List[Tuple[float, float]]]
    start_projected: Point
    goal_projected: Point
    distance: float
    nodes_explored: int
    debug_info: dict = None
    
    @property
    def success(self) -> bool:
        return self.path is not None


class PathfindingSystem:
    """High-performance pathfinding system using visibility graphs with A*."""

    EPS = 1e-6
    BUFFER_DISTANCE = 3.0  # NEW: Buffer around obstacles for visibility checks

    def __init__(
        self,
        game,
        obstacles: List[Polygon],
        *,
        max_vertices_per_poly: int = 60,
        simplify_tolerance: float = 0.0,
        max_edge_length: Optional[float] = None,
        cache_graph: bool = True,
        smoothing_iterations: int = 2,
        debug_mode: bool = False,
        use_buffer: bool = True  # NEW: Use buffered obstacles for collision
    ):
        """Initialize pathfinding system."""
        self.game = game
        self.max_vertices_per_poly = max_vertices_per_poly
        self.simplify_tolerance = simplify_tolerance
        self.max_edge_length = max_edge_length
        self.cache_graph = cache_graph
        self.smoothing_iterations = smoothing_iterations
        self.debug_mode = debug_mode
        self.use_buffer = use_buffer
        
        self.raw_obstacles = obstacles or []
        self._preprocess_obstacles()
        
        self._base_graph = None
        self._vertex_list = None
        
        if self.cache_graph and self.raw_obstacles:
            print(f"Building visibility graph with {sum(len(v) for v in self.vertices_by_poly)} vertices...")
            self._build_cached_graph()
            
            # DIAGNOSTIC: Check if graph is actually connected
            if self._base_graph and self._base_graph.number_of_edges() == 0:
                self._diagnose_visibility_problem()

    def _diagnose_visibility_problem(self):
        """Diagnose why no edges are being created."""
        print("\n=== VISIBILITY DIAGNOSTIC ===")
        
        # Test a few random vertex pairs
        if len(self._vertex_list) < 2:
            print("Not enough vertices to test!")
            return
        
        # Test first 5 pairs
        test_count = 0
        visible_count = 0
        
        for i in range(min(5, len(self._vertex_list))):
            for j in range(i+1, min(i+6, len(self._vertex_list))):
                ni, ci, _ = self._vertex_list[i]
                nj, cj, _ = self._vertex_list[j]
                
                dist = self._dist(ci, cj)
                seg = LineString([ci, cj])
                
                # Detailed check
                blocking_obstacles = []
                for idx, (poly_prep, poly_bounds) in enumerate(zip(self.prepared, self.bounds)):
                    if not self._segment_bbox_intersects(seg, poly_bounds):
                        continue
                    if poly_prep.intersects(seg):
                        blocking_obstacles.append(idx)
                
                test_count += 1
                if len(blocking_obstacles) == 0:
                    visible_count += 1
                
                if test_count <= 3:  # Print first 3
                    print(f"Pair {i}-{j}: dist={dist:.1f}, blocked by {len(blocking_obstacles)} obstacles")
        
        print(f"Tested {test_count} pairs: {visible_count} visible, {test_count - visible_count} blocked")
        print(f"Obstacle coverage is {((test_count - visible_count) / test_count * 100):.1f}% blocking")
        
        # Check if obstacles overlap
        overlapping = 0
        for i in range(len(self.polygons)):
            for j in range(i+1, min(i+10, len(self.polygons))):
                if self.polygons[i].intersects(self.polygons[j]):
                    overlapping += 1
        print(f"Found {overlapping} overlapping obstacle pairs (in first 10 checked)")
        print("=== END DIAGNOSTIC ===\n")

    def _preprocess_obstacles(self):
        """Preprocess obstacles for fast collision detection."""
        if self.simplify_tolerance and self.simplify_tolerance > 0.0:
            self.polygons = [
                p.simplify(self.simplify_tolerance, preserve_topology=True)
                for p in self.raw_obstacles
            ]
        else:
            self.polygons = list(self.raw_obstacles)

        # CRITICAL FIX: Use buffered obstacles for collision detection
        # This treats obstacles as slightly smaller, allowing paths closer to edges
        if self.use_buffer:
            self.collision_polygons = [p.buffer(-self.BUFFER_DISTANCE) for p in self.polygons]
            # Remove invalid geometries (buffers can create empty polygons)
            self.collision_polygons = [p for p in self.collision_polygons if not p.is_empty and p.is_valid]
            print(f"Using buffered obstacles: {len(self.polygons)} -> {len(self.collision_polygons)} valid")
        else:
            self.collision_polygons = self.polygons

        self.prepared = [prep(p) for p in self.collision_polygons]
        self.bounds = [p.bounds for p in self.collision_polygons]

        # Build vertex cache - use ORIGINAL polygons for waypoints, not buffered
        self.vertices_by_poly = []
        for p in self.polygons:
            coords = list(p.exterior.coords)[:-1]
            sampled = self._sample_vertices(coords)
            self.vertices_by_poly.append(sampled)

    def _sample_vertices(self, coords: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Intelligently sample vertices from polygon coordinates."""
        n = len(coords)
        if n <= self.max_vertices_per_poly or self.max_vertices_per_poly <= 0:
            return coords

        step = max(1, n // self.max_vertices_per_poly)
        sampled = coords[::step]

        if sampled[0] != coords[0]:
            sampled.insert(0, coords[0])

        return sampled

    def _build_cached_graph(self):
        """Build base visibility graph from obstacle vertices only."""
        self._vertex_list = []
        vid = 0
        for poly_idx, poly_vertices in enumerate(self.vertices_by_poly):
            for coord in poly_vertices:
                self._vertex_list.append((f"v{vid}", coord, poly_idx))
                vid += 1

        self._base_graph = nx.Graph()
        for name, coord, _ in self._vertex_list:
            self._base_graph.add_node(name, coord=coord)

        edges_checked = 0
        edges_added = 0
        n_vertices = len(self._vertex_list)

        print(f"Checking visibility for {n_vertices} vertices...")
        
        for i in range(n_vertices):
            ni, ci, poly_i = self._vertex_list[i]
            
            for j in range(i + 1, n_vertices):
                nj, cj, poly_j = self._vertex_list[j]
                edges_checked += 1

                # Skip same polygon vertices
                if poly_i == poly_j:
                    continue

                # Check max distance
                if self.max_edge_length:
                    dist = self._dist(ci, cj)
                    if dist > self.max_edge_length:
                        continue

                # Visibility check
                if self._visible(ci, cj):
                    self._base_graph.add_edge(ni, nj, weight=self._dist(ci, cj))
                    edges_added += 1
            
            # Progress indicator
            if i % 50 == 0 and i > 0:
                progress = self.loading_percent(x=i, max_val=n_vertices) / 100
                self.game.loading_screen.update(progress, "Building pathfinding system...")
                self.game.loading_screen.render()
                print(f"  Progress: {i}/{n_vertices} vertices processed, {edges_added} edges found\nprogress = {progress}")



        print(f"Visibility check complete: {edges_checked} checks, {edges_added} edges")

    def loading_percent(self, x, max_val=358, start=60, per=30):
        end = start + per
        return start + (end - start) * (x / max_val)
    @staticmethod
    def _dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
        """Fast Euclidean distance calculation."""
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return sqrt(dx * dx + dy * dy)

    @staticmethod
    def _point_coords(pt: Union[Point, Tuple[float, float]]) -> Tuple[float, float]:
        """Extract coordinates from Point or tuple."""
        if isinstance(pt, Point):
            return (pt.x, pt.y)
        return pt

    def _project_outside(self, pt: Union[Point, Tuple[float, float]], push_eps: float = 10.0) -> Point:
        """Project point outside obstacles if it's inside one."""
        p = Point(pt) if not isinstance(pt, Point) else pt

        # Check against ORIGINAL polygons, not buffered
        for poly_idx, poly in enumerate(self.polygons):
            if not poly.contains(p):
                continue

            nearest_on_boundary = nearest_points(p, poly.boundary)[1]
            centroid = poly.centroid
            dx = nearest_on_boundary.x - centroid.x
            dy = nearest_on_boundary.y - centroid.y
            norm = sqrt(dx * dx + dy * dy) or 1.0
            ux, uy = dx / norm, dy / norm

            # Push further out (increased from 1e-6)
            step = push_eps
            candidate = Point(
                nearest_on_boundary.x + ux * step,
                nearest_on_boundary.y + uy * step,
            )

            max_iterations = 10
            iteration = 0
            while iteration < max_iterations and any(poly.contains(candidate) for poly in self.polygons):
                step *= 2.0
                candidate = Point(
                    nearest_on_boundary.x + ux * step,
                    nearest_on_boundary.y + uy * step,
                )
                iteration += 1

            return candidate

        return p

    def _segment_bbox_intersects(self, seg: LineString, poly_bounds: Tuple[float, float, float, float]) -> bool:
        """Fast AABB intersection test."""
        minx, miny, maxx, maxy = poly_bounds
        sx_min, sy_min, sx_max, sy_max = seg.bounds
        
        if sx_max < minx or sx_min > maxx or sy_max < miny or sy_min > maxy:
            return False
        return True

    def _visible(self, a: Tuple[float, float], b: Tuple[float, float]) -> bool:
        """Check if line segment from a to b is collision-free."""
        seg = LineString([a, b])

        # Check against collision polygons (buffered)
        for poly_prep, poly_bounds in zip(self.prepared, self.bounds):
            if not self._segment_bbox_intersects(seg, poly_bounds):
                continue

            if poly_prep.intersects(seg):
                return False

        return True

    def _build_query_graph(self, start_pt: Point, goal_pt: Point) -> nx.Graph:
        """Build visibility graph for specific query."""
        start_coord = self._point_coords(start_pt)
        goal_coord = self._point_coords(goal_pt)

        if self._base_graph is not None:
            G = self._base_graph.copy()
            
            G.add_node("start", coord=start_coord)
            G.add_node("goal", coord=goal_coord)

            # Connect start
            for name, coord, _ in self._vertex_list:
                if self.max_edge_length and self._dist(start_coord, coord) > self.max_edge_length:
                    continue
                if self._visible(start_coord, coord):
                    G.add_edge("start", name, weight=self._dist(start_coord, coord))

            # Connect goal
            for name, coord, _ in self._vertex_list:
                if self.max_edge_length and self._dist(goal_coord, coord) > self.max_edge_length:
                    continue
                if self._visible(goal_coord, coord):
                    G.add_edge("goal", name, weight=self._dist(goal_coord, coord))

            # Direct connection
            if self._visible(start_coord, goal_coord):
                G.add_edge("start", "goal", weight=self._dist(start_coord, goal_coord))

        else:
            G = self._build_complete_graph(start_pt, goal_pt)

        return G

    def _build_complete_graph(self, start_pt: Point, goal_pt: Point) -> nx.Graph:
        """Build complete visibility graph."""
        start_coord = self._point_coords(start_pt)
        goal_coord = self._point_coords(goal_pt)

        nodes = [("start", start_coord), ("goal", goal_coord)]

        vid = 0
        for poly_vertices in self.vertices_by_poly:
            for coord in poly_vertices:
                nodes.append((f"v{vid}", coord))
                vid += 1

        G = nx.Graph()
        for name, coord in nodes:
            G.add_node(name, coord=coord)

        for i in range(len(nodes)):
            ni, ci = nodes[i]
            for j in range(i + 1, len(nodes)):
                nj, cj = nodes[j]

                if self.max_edge_length and self._dist(ci, cj) > self.max_edge_length:
                    continue

                if self._visible(ci, cj):
                    G.add_edge(ni, nj, weight=self._dist(ci, cj))

        return G

    def _smooth_path(self, path: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Smooth path by removing unnecessary waypoints."""
        if len(path) <= 2:
            return path

        for iteration in range(self.smoothing_iterations):
            smoothed = [path[0]]
            i = 0

            while i < len(path) - 1:
                best_j = i + 1
                max_lookahead = min(i + 20, len(path) - 1)
                for j in range(max_lookahead, i + 1, -1):
                    if self._visible(path[i], path[j]):
                        best_j = j
                        break

                smoothed.append(path[best_j])
                i = best_j

            if len(smoothed) == len(path):
                break

            path = smoothed

        return path

    def find_path(
        self,
        start: Union[Point, Tuple[float, float]],
        goal: Union[Point, Tuple[float, float]]
    ) -> PathfindingResult:
        """Find shortest collision-free path from start to goal."""
        start_pt = self._project_outside(Point(start))
        goal_pt = self._project_outside(Point(goal))
        
        start_coord = self._point_coords(start_pt)
        goal_coord = self._point_coords(goal_pt)

        # Quick check for direct path
        if self._visible(start_coord, goal_coord):
            path = [start_coord, goal_coord]
            distance = self._dist(start_coord, goal_coord)
            return PathfindingResult(
                path=path,
                start_projected=start_pt,
                goal_projected=goal_pt,
                distance=distance,
                nodes_explored=2
            )

        # Build visibility graph
        G = self._build_query_graph(start_pt, goal_pt)

        # A* heuristic
        def heuristic(u: str, v: str) -> float:
            cu = G.nodes[u]["coord"]
            cv = G.nodes[v]["coord"]
            return self._dist(cu, cv)

        # Find path
        try:
            path_nodes = nx.astar_path(G, "start", "goal", heuristic=heuristic, weight="weight")
        except nx.NetworkXNoPath:
            return PathfindingResult(
                path=None,
                start_projected=start_pt,
                goal_projected=goal_pt,
                distance=float('inf'),
                nodes_explored=G.number_of_nodes()
            )

        # Extract and smooth path
        path = [G.nodes[n]["coord"] for n in path_nodes]

        if self.smoothing_iterations > 0:
            path = self._smooth_path(path)

        distance = sum(self._dist(path[i], path[i + 1]) for i in range(len(path) - 1))

        return PathfindingResult(
            path=path,
            start_projected=start_pt,
            goal_projected=goal_pt,
            distance=distance,
            nodes_explored=len(path_nodes)
        )

    def invalidate_cache(self):
        """Invalidate cached visibility graph."""
        self._base_graph = None
        self._vertex_list = None

    def update_obstacles(self, obstacles: List[Polygon]):
        """Update obstacles and rebuild cache."""
        self.raw_obstacles = obstacles or []
        self._preprocess_obstacles()
        
        if self.cache_graph and self.raw_obstacles:
            self._build_cached_graph()
        else:
            self.invalidate_cache()

    def get_stats(self) -> dict:
        """Get statistics about the pathfinding system."""
        stats = {
            "num_obstacles": len(self.polygons),
            "total_vertices": sum(len(v) for v in self.vertices_by_poly),
            "cache_enabled": self.cache_graph,
            "max_edge_length": self.max_edge_length,
            "smoothing_iterations": self.smoothing_iterations,
        }
        
        if self._base_graph is not None:
            stats.update({
                "cached_nodes": self._base_graph.number_of_nodes(),
                "cached_edges": self._base_graph.number_of_edges(),
            })
        
        return stats