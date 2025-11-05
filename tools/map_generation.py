import random
import json
import numpy as np
from scipy.spatial import Voronoi
from perlin_noise import PerlinNoise
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, MultiPolygon, Point, box
from shapely.ops import unary_union, polygonize
from shapely import geometry
from scipy.ndimage import label, find_objects
import time
import os
os.makedirs("../assets/maps", exist_ok=True)

WIDTH, HEIGHT = 1024, 768
MOUNTAIN_THRESHOLD = 0.23
RIVER_THRESHOLD = -0.2
NOISE_SCALE = 2
SEED = 9423551
NUM_POINTS = 150 
SAVE_PREFIX = "map_model_v8"
img_path = f"./assets/maps/{SAVE_PREFIX}.png"
TERRAIN_TYPE = {
    'MOUNTAIN': 2,
    'LAND': 1,
    'RIVER': 0
}

print(f"[MapGen v8 - Natural Borders] Initializing: {WIDTH}x{HEIGHT}, Seed: {SEED}, Points: {NUM_POINTS}")

# ==============================
# HELPER FUNCTIONS
# ==============================

def generate_terrain_maps(seed):
    """
    Generates terrain maps using Perlin noise and saves them as images.
    """
    print("Step 1: Generating terrain using Perlin noise...")
    noise = PerlinNoise(octaves=6, seed=seed)
    
    x_coords = np.linspace(0, NOISE_SCALE, WIDTH)
    y_coords = np.linspace(0, NOISE_SCALE, HEIGHT)
    world = np.array([[noise([x, y]) for x in x_coords] for y in y_coords])

    terrain_map = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    terrain_map[world > MOUNTAIN_THRESHOLD] = TERRAIN_TYPE['MOUNTAIN']
    terrain_map[(world > RIVER_THRESHOLD) & (world <= MOUNTAIN_THRESHOLD)] = TERRAIN_TYPE['LAND']
    terrain_map[world <= RIVER_THRESHOLD] = TERRAIN_TYPE['RIVER']
    
    return terrain_map

def terrain_to_polygons(terrain_map, terrain_type):
    """
    Converts a specific terrain type from the array to a MultiPolygon
    """
    print(f"Step 2: Converting terrain type '{terrain_type}' to polygons...")
    mask = (terrain_map == terrain_type).astype(np.uint8)
    
    labeled_array, num_features = label(mask)
    if num_features == 0:
        return MultiPolygon()

    polygons = []
    for i in range(1, num_features + 1):
        points = np.argwhere(labeled_array == i)
        points = points[:, [1, 0]]
        if len(points) >= 3:
            poly = Polygon(points).convex_hull
            if poly.is_valid and poly.area > 10:
                polygons.append(poly)

    return unary_union(polygons) if polygons else MultiPolygon()

def find_city_location(province_poly, land_union, mountain_union, river_union):
    """
    Find the best location for a city - only on valid land areas within the province.
    """
    # safe_area = province ∩ land - (mountains ∪ rivers)
    safe_area = province_poly.intersection(land_union)
    safe_area = safe_area.difference(mountain_union).difference(river_union)
    
    if safe_area.is_empty or safe_area.area < 10:
        # No safe location - do not place city
        return None

    # If MultiPolygon, take the largest part
    if isinstance(safe_area, MultiPolygon):
        safe_area = max(safe_area.geoms, key=lambda p: p.area)

    # Find the centroid of the safe area
    centroid = safe_area.centroid
    if safe_area.contains(centroid):
        return (int(centroid.x), int(centroid.y))

    # Find a representative point within the safe area
    rep_point = safe_area.representative_point()
    return (int(rep_point.x), int(rep_point.y))


# ==============================
# MAIN GENERATION LOGIC
# ==============================
def generate_map_model(seed=SEED):
    start_time = time.time()
    
    if seed is None: 
        seed = random.randint(0, 999999)
    random.seed(seed)
    np.random.seed(seed)

    # 1. generate terrain map
    terrain_map = generate_terrain_maps(seed)

        # 2. convert terrain types to polygons
    mountain_union = terrain_to_polygons(terrain_map, TERRAIN_TYPE['MOUNTAIN'])
    river_union = terrain_to_polygons(terrain_map, TERRAIN_TYPE['RIVER'])
    land_union = terrain_to_polygons(terrain_map, TERRAIN_TYPE['LAND'])
    
    print(f"   → Mountains: {mountain_union.area:.0f}")
    print(f"   → Rivers: {river_union.area:.0f} px²")
    print(f"   → Land: {land_union.area:.0f} px²")
    
    # 3. generate voronoi diagram over entire map
    print("Step 3: Generating Voronoi diagram on ENTIRE map...")
    
    # generate random points
    points = np.random.rand(NUM_POINTS, 2)
    points[:, 0] *= WIDTH
    points[:, 1] *= HEIGHT
    
    vor = Voronoi(points)
    
    # extract voronoi lines
    voronoi_lines = []
    for line in vor.ridge_vertices:
        if -1 not in line:
            voronoi_lines.append(geometry.LineString(vor.vertices[line]))
    
    if not voronoi_lines:
        print("ERROR: No valid Voronoi lines generated!")
        return
        
    voronoi_lines_union = unary_union(voronoi_lines)

    # 4. generate initial provinces
    print("Step 4: Creating initial provinces...")
    
    map_boundary = box(0, 0, WIDTH, HEIGHT).boundary
    
    # include map boundary to close polygons
    all_lines = unary_union([voronoi_lines_union, map_boundary])
    
    # 5. generate all polygons from voronoi lines
    all_polygons = list(polygonize(all_lines))
    print(f"   → Created {len(all_polygons)} initial polygons")
    
    # 6. clipping provinces (removing mountains & rivers)
    print("Step 5: Clipping provinces (removing mountains & rivers)...")
    
    # generate forbidden area (mountains + rivers)
    forbidden_area = unary_union([mountain_union, river_union])
    mountain_Areas = unary_union([mountain_union])
    river_Areas = unary_union([river_union])
    province_polygons = []
    removed_count = 0
    clipped_count = 0
    
    for poly in all_polygons:
        if not poly.is_valid or poly.area < 100:
            continue
        
        # clip polygon with forbidden area
        clipped = poly.difference(forbidden_area)
        
        # if completely inside mountains/rivers
        if clipped.is_empty or clipped.area < 500:
            removed_count += 1
            continue
        
        # check if clipped polygon is valid and has enough area
        if clipped.area < poly.area * 0.95:  # less than 95% area remains
            clipped_count += 1
        
        # add valid clipped polygon(s) to list
        if isinstance(clipped, MultiPolygon):
            for geom in clipped.geoms:
                if geom.is_valid and geom.area > 500:
                    province_polygons.append(geom)
        elif isinstance(clipped, Polygon):
            if clipped.is_valid and clipped.area > 500:
                province_polygons.append(clipped)
    
    print(f"   → Removed {removed_count} provinces (fully inside mountains/rivers)")
    print(f"   → Clipped {clipped_count} provinces (partially inside)")
    print(f"   → Final provinces: {len(province_polygons)}")
    
    if not province_polygons:
        print("ERROR: No valid provinces after clipping!")
        return
    
    # 7. process provinces and place cities
    print("Step 6: Processing provinces and placing cities...")
    final_provinces = []
    map_data = []
    
    cities_placed = 0
    cities_skipped = 0
    for i, poly in enumerate(province_polygons):
        final_provinces.append(poly)
        
        # Find city location
        city_loc = find_city_location(poly, land_union, mountain_union, river_union)
        
        if city_loc:
            cities_placed += 1
        else:
            cities_skipped += 1
        
        map_data.append({
            "province_id": i,
            "city_name": f"City {i}" if city_loc else None,
            "city_location": city_loc,
            "area": poly.area,
            "is_coastal": poly.intersects(river_union),
            "is_mountainous": poly.intersects(mountain_union),
            "has_city": city_loc is not None
        })
    
    print(f"   → Cities placed: {cities_placed}")
    print(f"   → Cities skipped (no safe land): {cities_skipped}")
    
    # 8. draw final map
    print("Step 7: Drawing the final map...")
    img = Image.new('RGB', (WIDTH, HEIGHT), (70, 130, 180))  # water background
    draw = ImageDraw.Draw(img)
    
    def draw_geometry(geom, fill_color):
        if isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                if poly.exterior:
                    draw.polygon(list(poly.exterior.coords), fill=fill_color)
                    for interior in poly.interiors:
                        draw.polygon(list(interior.coords), fill=(70, 130, 180))
        elif isinstance(geom, Polygon):
            if geom.exterior:
                draw.polygon(list(geom.exterior.coords), fill=fill_color)
                for interior in geom.interiors:
                    draw.polygon(list(interior.coords), fill=(70, 130, 180))
    
    #draw land
    draw_geometry(land_union, (60, 180, 75))  # green
    
    # draw rivers
    draw_geometry(river_union, (70, 130, 180))  # blue

    # draw mountains
    draw_geometry(mountain_union, (139, 137, 137))  # gray

    # draw province borders (now with natural borders!)
    for i, poly in enumerate(final_provinces):
        if poly.exterior:
            coords = list(poly.exterior.coords)
            color = (255, 255, 255) if map_data[i]["has_city"] else (120, 120, 120)
            width = 1
            draw.line(coords, fill=color, width=width)

    # 9. save outputs

    
    # GeoJSON
    geojson_features = []
    for i, poly in enumerate(final_provinces):
        feature = {
            "type": "Feature",
            "geometry": geometry.mapping(poly),
            "properties": map_data[i]
        }
        geojson_features.append(feature)
    
    geojson_data = {"type": "FeatureCollection", "features": geojson_features}
    # save mountain layer
    with open("./assets/maps/mountains.geojson", "w") as f:
        json.dump({
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": geometry.mapping(mountain_union),
                "properties": {"terrain": "mountain", "blocks_position": True}
            }]
        }, f)

    # save river layer
    with open("./assets/maps/rivers.geojson", "w") as f:
        json.dump({
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": geometry.mapping(river_union),
                "properties": {"terrain": "river", "blocks_position": True}
            }]
        }, f)

    geojson_path = f"./assets/maps/{SAVE_PREFIX}.geojson"
    with open(geojson_path, 'w') as f:
        json.dump(geojson_data, f, indent=2)

    # save map image
    img.save(img_path)

    # 10. done
    end_time = time.time()
    print("=" * 60)
    print(f"✓ Map generation complete in {end_time - start_time:.2f} seconds!")
    print(f"✓ Total provinces: {len(final_provinces)}")
    print(f"✓ Provinces with cities: {cities_placed}")
    print(f"✓ Empty provinces (mountains/coastal): {cities_skipped}")
    print(f"✓ Saved map image → {img_path}")
    print(f"✓ Saved GeoJSON data → {geojson_path}")
    print("=" * 60)

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    generate_map_model()