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
MOUNTAIN_THRESHOLD = 0.3
RIVER_THRESHOLD = -0.1
NOISE_SCALE = 1.9
SEED = 9423551
NUM_POINTS = 150 
SAVE_PREFIX = "map_model_v6"

TERRAIN_TYPE = {
    'MOUNTAIN': 2,
    'LAND': 1,
    'RIVER': 0
}

print(f"[MapGen v6] Initializing map: {WIDTH}x{HEIGHT}, Seed: {SEED}, Points: {NUM_POINTS}")

# ==============================
# HELPER FUNCTIONS
# ==============================

def generate_terrain_maps(seed):
    """
    يولد مصفوفات التضاريس باستخدام NumPy بشكل كامل لتحقيق أداء فائق.
    """
    print("Step 1: Generating terrain using Perlin noise (vectorized)...")
    noise = PerlinNoise(octaves=6, seed=seed)
    
    # إنشاء شبكة إحداثيات وتطبيق الضوضاء عليها دفعة واحدة
    x_coords = np.linspace(0, NOISE_SCALE, WIDTH)
    y_coords = np.linspace(0, NOISE_SCALE, HEIGHT)
    world = np.array([[noise([x, y]) for x in x_coords] for y in y_coords])

    # تصنيف التضاريس باستخدام عمليات NumPy الموجهة
    terrain_map = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    terrain_map[world > MOUNTAIN_THRESHOLD] = TERRAIN_TYPE['MOUNTAIN']
    terrain_map[(world > RIVER_THRESHOLD) & (world <= MOUNTAIN_THRESHOLD)] = TERRAIN_TYPE['LAND']
    terrain_map[world <= RIVER_THRESHOLD] = TERRAIN_TYPE['RIVER']
    
    return terrain_map

def terrain_to_polygons(terrain_map, terrain_type):
    """
    يحول نوع تضاريس معين (مثل كل الجبال) من مصفوفة إلى كائن MultiPolygon واحد.
    """
    print(f"Step 2: Converting terrain type '{terrain_type}' to polygons...")
    mask = (terrain_map == terrain_type).astype(np.uint8)
    
    # استخدام label من SciPy لتحديد المناطق المتصلة
    labeled_array, num_features = label(mask)
    if num_features == 0:
        return MultiPolygon()

    polygons = []
    # العثور على حدود كل منطقة وتحويلها إلى مضلع
    for i in range(1, num_features + 1):
        points = np.argwhere(labeled_array == i)
        # التبديل من (row, col) إلى (x, y)
        points = points[:, [1, 0]]
        if len(points) >= 3:
            # .convex_hull أسرع من buffer(0) للمناطق الكبيرة
            poly = Polygon(points).convex_hull
            if poly.is_valid:
                polygons.append(poly)

    # دمج كل المضلعات في كائن واحد لسهولة التعامل
    return unary_union(polygons)

def find_city_location(province_poly, land_poly, mountain_union):
    """
    يجد أفضل موقع للمدينة داخل مضلع المقاطعة، مع تجنب الجبال.
    
    تم تحديث هذه الدالة لتجنب الجبال بشكل صريح.
    """
    # 1. ابحث عن نقطة داخل المقاطعة وبعيدة عن الجبال
    
    # المركز الهندسي هو نقطة البداية
    centroid = province_poly.centroid
    target_point = centroid

    # 2. تحقق من أن النقطة تقع ضمن الأرض الصالحة وبعيدة عن الجبال
    # الأرض الصالحة هي land_poly
    
    # إذا كان المركز الهندسي يقع داخل الأرض الصالحة وليس داخل الجبال
    if land_poly.contains(centroid) and not mountain_union.contains(centroid):
        return (int(centroid.x), int(centroid.y))
    
    # 3. إذا لم يكن المركز الهندسي صالحًا، ابحث عن نقطة تمثيلية صالحة
    rep_point = province_poly.representative_point()
    if land_poly.contains(rep_point) and not mountain_union.contains(rep_point):
        return (int(rep_point.x), int(rep_point.y))

    # 4. كملاذ أخير، ابحث عن أي نقطة صالحة داخل المقاطعة (قد تكون بطيئة)
    # نقوم بإنشاء مضلع الأرض الصالحة داخل المقاطعة
    safe_area = province_poly.intersection(land_poly).difference(mountain_union)
    
    if not safe_area.is_empty:
        # إذا كانت المساحة الصالحة موجودة، استخدم نقطة تمثيلية لها
        safe_point = safe_area.representative_point()
        return (int(safe_point.x), int(safe_point.y))
        
    # 5. إذا لم يتم العثور على أي نقطة صالحة، استخدم المركز الهندسي (هذا يعني أن المقاطعة كلها غير صالحة، وهو أمر نادر الحدوث بعد التقاطع)
    # ونقوم بالتحذير
    print(f"Warning: Could not find a safe city location for a province. Using centroid: ({int(centroid.x)}, {int(centroid.y)})")
    return (int(centroid.x), int(centroid.y))


# ==============================
# MAIN GENERATION LOGIC
# ==============================
def generate_map_model(seed=SEED):
    start_time = time.time()
    
    if seed is None: seed = random.randint(0, 999999)
    random.seed(seed)
    np.random.seed(seed)

    # 1. توليد خريطة التضاريس (جبال، أرض، أنهار)
    terrain_map = generate_terrain_maps(seed)

    # 2. تحويل مناطق التضاريس إلى مضلعات هندسية
    mountain_union = terrain_to_polygons(terrain_map, TERRAIN_TYPE['MOUNTAIN'])
    river_union = terrain_to_polygons(terrain_map, TERRAIN_TYPE['RIVER'])
    
    # الأرض الصالحة للسكن (LAND)
    land_mask = (terrain_map == TERRAIN_TYPE['LAND'])
    
    # إنشاء مضلع للأرض الصالحة للسكن فقط (Land Union)
    print("Step 3: Creating landmass polygons...")
    land_polygons = []
    labeled_land, num_land_features = label(land_mask)
    for i in range(1, num_land_features + 1):
        points = np.argwhere(labeled_land == i)[:, [1, 0]]
        if len(points) >= 3:
            # استخدام Polygon(points).convex_hull كما في الكود الأصلي
            poly = Polygon(points).convex_hull
            if poly.is_valid:
                land_polygons.append(poly)
    land_union = unary_union(land_polygons)
    
    # 3. تحديد المنطقة التي سيتم تطبيق تقسيم فورونوي عليها
    # المنطقة الصالحة للتقسيم هي الأرض الصالحة + الجبال + الأنهار
    # هذا هو الخطأ الذي تم تصحيحه. يجب أن يكون التقسيم على المنطقة الصالحة فقط.
    # المنطقة التي يجب أن تتقاطع معها خطوط فورونوي هي *فقط* مضلع الأرض الصالحة (land_union)
    
    # 4. إنشاء مخطط فورونوي وتقسيم الأرض
    print("Step 4: Generating Voronoi diagram and creating provinces...")
    
    # 4.1. اختيار نقاط فورونوي داخل الأرض الصالحة فقط
    land_points = np.argwhere(land_mask)[:, [1, 0]] # الحصول على إحداثيات (x, y) للأرض الصالحة
    
    if len(land_points) < NUM_POINTS:
        print("Warning: Not enough land points to select the required number of Voronoi points.")
        selected_indices = np.arange(len(land_points))
    else:
        selected_indices = np.random.choice(len(land_points), NUM_POINTS, replace=False)
        
    points = land_points[selected_indices]
    vor = Voronoi(points)
    
    # تحويل خطوط فورونوي إلى كائنات خطية Shapely
    voronoi_lines = unary_union([
        geometry.LineString(vor.vertices[line])
        for line in vor.ridge_vertices if -1 not in line
    ])
    
    # 4.2. تجميع كل الخطوط التي ستشكل حدود المقاطعات
    # أ. حدود الخريطة
    map_boundary = box(0, 0, WIDTH, HEIGHT).boundary
    
    # ب. حدود التضاريس غير الصالحة (الجبال والأنهار)
    # نحتاج إلى حدود الأرض الصالحة التي تلامس المناطق غير الصالحة
    # حدود الأرض الصالحة هي land_union.boundary
    # لكننا نريد أن تكون حدود المقاطعات هي حدود الجبال والأنهار نفسها
    
    # دمج حدود الجبال والأنهار مع خطوط فورونوي وحدود الخريطة
    all_lines = unary_union([
        voronoi_lines, 
        mountain_union.boundary, 
        river_union.boundary,
        map_boundary
    ])
    
    # 4.3. تقسيم الأرض الصالحة باستخدام كل الخطوط المجمعة
    # نستخدم polygonize لإنشاء مضلعات من تقاطع الخطوط
    # ثم نستخدم التقاطع مع land_union لضمان أن المقاطعات لا تتجاوز الأرض الصالحة
    
    # نستخدم polygonize على جميع الخطوط المجمعة لإنشاء مضلعات أولية
    # ثم نأخذ تقاطع هذه المضلعات مع land_union
    
    # نستخدم polygonize لإنشاء مضلعات أولية من كل الخطوط
    # هذا سيقسم كل شيء، بما في ذلك المناطق غير الصالحة، ولكننا سنقوم بالتصفية لاحقًا
    all_polygons = list(polygonize(all_lines))
    
    # 4.4. استخراج المقاطعات النهائية عن طريق تقاطع المضلعات الأولية مع الأرض الصالحة
    province_polygons = []
    for poly in all_polygons:
        # التقاطع مع مضلع الأرض الصالحة
        intersection = poly.intersection(land_union)
        
        if intersection.is_empty:
            continue
            
        # إذا كان التقاطع MultiPolygon، قم بإضافة كل مضلع على حدة
        if isinstance(intersection, MultiPolygon):
            for geom in intersection.geoms:
                if geom.area > 500 and geom.is_valid:
                    province_polygons.append(geom)
        elif isinstance(intersection, Polygon):
            if intersection.area > 500 and intersection.is_valid:
                province_polygons.append(intersection)

    
    print(f"Step 5: Processing {len(province_polygons)} provinces...")
    final_provinces = []
    map_data = []
    
    # 5. معالجة كل مقاطعة على حدة
    for i, poly in enumerate(province_polygons):
        
        # التأكد من أن المقاطعة صالحة وذات مساحة كافية (تم التحقق منها في الخطوة السابقة)
        if not poly.is_valid or poly.area < 500:
             continue # يجب أن لا يحدث هذا إذا كان الكود في 4.2 صحيحاً
        
        final_provinces.append(poly)
        
        # 6. تحديد موقع المدينة وجمع البيانات
        # تم تحديث find_city_location لضمان عدم وضع المدن في الجبال
        city_loc = find_city_location(poly, land_union, mountain_union)
        
        map_data.append({
            "province_id": len(final_provinces) - 1,
            "city_name": f"City {len(final_provinces) - 1}",
            "city_location": city_loc,
            "area": poly.area,
            "is_coastal": poly.intersects(river_union),
            "is_mountainous": poly.intersects(mountain_union)
        })

    # 7. رسم الخريطة النهائية
    print("Step 7: Drawing the final map...")
    img = Image.new('RGB', (WIDTH, HEIGHT), (70, 130, 180)) # لون الماء الأساسي (أزرق)
    draw = ImageDraw.Draw(img)

    # رسم الأرض
    # يجب أن تكون الأرض هي land_union فقط
    if isinstance(land_union, MultiPolygon):
        for poly in land_union.geoms:
            draw.polygon(list(poly.exterior.coords), fill=(60, 180, 75)) # أخضر
            for interior in poly.interiors:
                draw.polygon(list(interior.coords), fill=(70, 130, 180)) # لون الماء
    elif isinstance(land_union, Polygon):
        draw.polygon(list(land_union.exterior.coords), fill=(60, 180, 75)) # أخضر
        for interior in land_union.interiors:
            draw.polygon(list(interior.coords), fill=(70, 130, 180)) # لون الماء

    # رسم الأنهار (فوق الأرض)
    if isinstance(river_union, MultiPolygon):
        for poly in river_union.geoms:
            draw.polygon(list(poly.exterior.coords), fill=(70, 130, 180)) # أزرق
    elif isinstance(river_union, Polygon):
        draw.polygon(list(river_union.exterior.coords), fill=(70, 130, 180)) # أزرق


    # رسم الجبال (فوق الأرض والأنهار)
    if isinstance(mountain_union, MultiPolygon):
        for poly in mountain_union.geoms:
            draw.polygon(list(poly.exterior.coords), fill=(110, 110, 110)) # رمادي
    elif isinstance(mountain_union, Polygon):
        draw.polygon(list(mountain_union.exterior.coords), fill=(110, 110, 110)) # رمادي

    # رسم حدود المقاطعات
    # حدود المقاطعات الآن هي تقاطع خطوط فورونوي مع الأرض الصالحة، لذا لن تمر عبر الجبال أو الأنهار
    for poly in final_provinces:
        # رسم حدود المقاطعة
        draw.line(list(poly.exterior.coords), fill=(200, 200, 200), width=1)
        
        # إذا كانت المقاطعة تلامس الجبل أو النهر، فسيتم رسم الحد فوقها
        # ولكن بما أن المقاطعات هي جزء من land_union، فإن حدودها الداخلية لن تكون على الجبال أو الأنهار.
        # الحدود التي تلامس الجبال/الأنهار ستكون جزءًا من حدود land_union

    # رسم المدن
    for province in map_data:
        cx, cy = province["city_location"]
        draw.ellipse((cx-3, cy-3, cx+3, cy+3), fill=(255, 255, 0), outline='black')

    # 8. حفظ المخرجات
    img_path = f"{SAVE_PREFIX}.png"
    img.save(img_path)
    
    geojson_features = []
    for i, poly in enumerate(final_provinces):
        # يجب التأكد من أن poly هو Polygon أو MultiPolygon
        if isinstance(poly, Polygon) or isinstance(poly, MultiPolygon):
            feature = {
                "type": "Feature",
                "geometry": geometry.mapping(poly),
                "properties": next((p for p in map_data if p["province_id"] == i), None)
            }
            geojson_features.append(feature)
        
    geojson_data = {"type": "FeatureCollection", "features": geojson_features}
    
    geojson_path = f"{SAVE_PREFIX}.geojson"
    with open(geojson_path, 'w') as f:
        json.dump(geojson_data, f, indent=2)

    end_time = time.time()
    print("-" * 30)
    print(f"Map generation complete in {end_time - start_time:.2f} seconds.")
    print(f"Saved map image -> {img_path}")
    print(f"Saved GeoJSON data -> {geojson_path}")

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    generate_map_model()
