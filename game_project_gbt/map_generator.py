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

# ==============================
# CONFIGURATION
# ==============================
WIDTH, HEIGHT = 1024, 768
MOUNTAIN_THRESHOLD = 0.23
RIVER_THRESHOLD = -0.2
NOISE_SCALE = 2
SEED = 9423551
NUM_POINTS = 150 
SAVE_PREFIX = "map_model_v8_natural"

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
    يولد مصفوفات التضاريس باستخدام Perlin noise
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
    يحول نوع تضاريس معين من مصفوفة إلى MultiPolygon
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
    يجد أفضل موقع للمدينة - فقط على الأرض الصالحة
    """
    # المنطقة الآمنة = المقاطعة ∩ الأرض - (الجبال ∪ الأنهار)
    safe_area = province_poly.intersection(land_union)
    safe_area = safe_area.difference(mountain_union).difference(river_union)
    
    if safe_area.is_empty or safe_area.area < 10:
        # لا يوجد مكان آمن - لا تضع مدينة
        return None
    
    # إذا كانت MultiPolygon، خذ أكبر جزء
    if isinstance(safe_area, MultiPolygon):
        safe_area = max(safe_area.geoms, key=lambda p: p.area)
    
    # المركز الهندسي
    centroid = safe_area.centroid
    if safe_area.contains(centroid):
        return (int(centroid.x), int(centroid.y))
    
    # نقطة تمثيلية
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

    # 1. توليد خريطة التضاريس
    terrain_map = generate_terrain_maps(seed)

    # 2. تحويل التضاريس إلى مضلعات
    mountain_union = terrain_to_polygons(terrain_map, TERRAIN_TYPE['MOUNTAIN'])
    river_union = terrain_to_polygons(terrain_map, TERRAIN_TYPE['RIVER'])
    land_union = terrain_to_polygons(terrain_map, TERRAIN_TYPE['LAND'])
    
    print(f"   → Mountains: {mountain_union.area:.0f}")
    print(f"   → Rivers: {river_union.area:.0f} px²")
    print(f"   → Land: {land_union.area:.0f} px²")
    
    # 3. إنشاء مخطط Voronoi على كامل الخريطة
    print("Step 3: Generating Voronoi diagram on ENTIRE map...")
    
    # اختيار نقاط عشوائية من كامل الخريطة
    points = np.random.rand(NUM_POINTS, 2)
    points[:, 0] *= WIDTH
    points[:, 1] *= HEIGHT
    
    vor = Voronoi(points)
    
    # تحويل خطوط Voronoi إلى كائنات خطية
    voronoi_lines = []
    for line in vor.ridge_vertices:
        if -1 not in line:
            voronoi_lines.append(geometry.LineString(vor.vertices[line]))
    
    if not voronoi_lines:
        print("ERROR: No valid Voronoi lines generated!")
        return
        
    voronoi_lines_union = unary_union(voronoi_lines)
    
    # 4. دمج خطوط Voronoi مع حدود الخريطة فقط
    print("Step 4: Creating initial provinces...")
    
    map_boundary = box(0, 0, WIDTH, HEIGHT).boundary
    
    # فقط خطوط Voronoi + حدود الخريطة
    all_lines = unary_union([voronoi_lines_union, map_boundary])
    
    # 5. تقسيم الخريطة إلى مقاطعات أولية
    all_polygons = list(polygonize(all_lines))
    print(f"   → Created {len(all_polygons)} initial polygons")
    
    # 6. قص المقاطعات - إزالة ما هو داخل الجبال والأنهار
    print("Step 5: Clipping provinces (removing mountains & rivers)...")
    
    # المناطق الممنوعة = الجبال + الأنهار
    forbidden_area = unary_union([mountain_union, river_union])
    mountain_Areas = unary_union([mountain_union])
    river_Areas = unary_union([river_union])
    province_polygons = []
    removed_count = 0
    clipped_count = 0
    
    for poly in all_polygons:
        if not poly.is_valid or poly.area < 100:
            continue
        
        # قص المقاطعة - إزالة المناطق الممنوعة
        clipped = poly.difference(forbidden_area)
        
        # إذا اختفت المقاطعة تمامًا (كانت داخل جبل/نهر)
        if clipped.is_empty or clipped.area < 500:
            removed_count += 1
            continue
        
        # إذا تم القص (كان هناك جزء داخل الجبال/الأنهار)
        if clipped.area < poly.area * 0.95:  # فقدت أكثر من 5%
            clipped_count += 1
        
        # التعامل مع MultiPolygon (قد ينتج عن القص عدة أجزاء)
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
    
    # 7. معالجة كل مقاطعة ووضع المدن
    print("Step 6: Processing provinces and placing cities...")
    final_provinces = []
    map_data = []
    
    cities_placed = 0
    cities_skipped = 0
    for i, poly in enumerate(province_polygons):
        final_provinces.append(poly)
        
        # تحديد موقع المدينة (قد يكون None إذا لم يكن هناك أرض صالحة)
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
    
    # 8. رسم الخريطة النهائية
    print("Step 7: Drawing the final map...")
    img = Image.new('RGB', (WIDTH, HEIGHT), (70, 130, 180))  # ماء
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
    
    # رسم الأرض
    draw_geometry(land_union, (60, 180, 75))  # أخضر
    
    # رسم الأنهار
    draw_geometry(river_union, (70, 130, 180))  # أزرق
    
    # رسم الجبال
    draw_geometry(mountain_union, (139, 137, 137))  # رمادي
    
    # رسم حدود المقاطعات (الآن بحدود طبيعية!)
    for i, poly in enumerate(final_provinces):
        if poly.exterior:
            coords = list(poly.exterior.coords)
            color = (255, 255, 255) if map_data[i]["has_city"] else (120, 120, 120)
            width = 1
            draw.line(coords, fill=color, width=width)


    
    # رسم المدن (فقط حيث يوجد موقع صالح)
    for province in map_data:
        if province["city_location"]:
            cx, cy = province["city_location"]
            draw.ellipse((cx-4, cy-4, cx+4, cy+4), fill=(255, 215, 0), outline=(0, 0, 0), width=1)
    
    # 9. حفظ المخرجات
    img_path = f"{SAVE_PREFIX}.png"
    img.save(img_path)
    
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
    # حفظ طبقة الجبال
    with open("mountains.geojson", "w") as f:
        json.dump({
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": geometry.mapping(mountain_union),
                "properties": {"terrain": "mountain"}
            }]
        }, f)

    # حفظ طبقة الأنهار
    with open("rivers.geojson", "w") as f:
        json.dump({
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": geometry.mapping(river_union),
                "properties": {"terrain": "river"}
            }]
        }, f)

    geojson_path = f"{SAVE_PREFIX}.geojson"
    with open(geojson_path, 'w') as f:
        json.dump(geojson_data, f, indent=2)
    
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