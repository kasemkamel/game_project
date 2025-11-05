# core/map_loader.py
import json
import os
from entities.terrain import terrain
from entities.province import Province
from entities.city import City
from entities.castle import Castle
from entities.checkpoint import Checkpoint
from shapely.geometry import shape, Point

class MapLoader:
    """Loads and parses GeoJSON map files into game entities."""
    
    def __init__(self, map_path="assets/maps/map_model_v8.geojson", mountains_path = "assets/maps/mountains.geojson", rivers_path = "assets/maps/rivers.geojson"):
        self.map_path = map_path
        self.mountains_path = mountains_path
        self.rivers_path = rivers_path
        self.provinces = []
        self.cities = []
        self.castles = []
        self.checkpoints = []
        self.mountains = []
        self.rivers = []
    
    def load_map(self):
        """Load the main map file and create game entities."""
        if not os.path.exists(self.map_path) or not os.path.exists(self.mountains_path) or not os.path.exists(self.rivers_path):
            print(f"ERROR: Map file not found at {self.map_path} or terrain files missing at {self.mountains_path} or {self.rivers_path}.")
            print("Please run tools/map_generator.py first!")
            return False
        
        print(f"Loading map from {self.map_path}...")
        print(f"Loading terrain from {self.mountains_path} \nand {self.rivers_path}...")
        
        with open(self.map_path, 'r') as f:
            geojson_data = json.load(f)
        

        with open(self.mountains_path, 'r') as f:
            _mountains = json.load(f)
        

        with open(self.rivers_path, 'r') as f:
            _rivers = json.load(f)



        # Load each province
        for feature in geojson_data['features']:
            self._create_province_from_feature(feature)
        
        # Load terrain layers
        for feature in _mountains['features']:
            self._create_terrain_layers(feature)

        for feature in _rivers['features']:
            self._create_terrain_layers(feature)

        print(f"✓ Loaded {len(self.provinces)} provinces")
        print(f"✓ Loaded {len(self.cities)} cities")
        print(f"✓ Loaded {len(self.castles)} castles")
        print(f"✓ Loaded {len(self.checkpoints)} checkpoints")
        
        return True
    
    def _create_province_from_feature(self, feature):
        """Convert a GeoJSON feature into game entities."""
        geometry = feature['geometry']
        props = feature['properties']
        
        # Extract polygon coordinates
        if geometry['type'] == 'Polygon':
            coords = geometry['coordinates'][0]
        else:
            print(f"Warning: Unsupported geometry type {geometry['type']}")
            return
        
        # Convert coordinates to pygame format [(x, y), ...]
        points = [(x, y) for x, y in coords]
        color = (60, 180, 75)    # Green for land
        
        # Create province entity
        province = Province(points, color, props)
        self.provinces.append(province)
        
        # Create city if present
        if props.get('has_city', False) and props.get('city_location'):
            city_loc = props['city_location']
            city_name = props.get('city_name', f"City {props['province_id']}")
            city = City(city_loc[0], city_loc[1], city_name)
            city.province_id = props['province_id']
            self.cities.append(city)
        else:
            # No city for this province
            pass


    def _create_terrain_layers(self, feature):
        """Create terrain layers like mountains or rivers."""
        geometry = feature['geometry']
        props = feature['properties']
        # Extract polygon coordinates
        if geometry['type'] == 'Polygon':
            coords = geometry['coordinates'][0]
        elif geometry['type'] == 'MultiPolygon':
            for poly in geometry['coordinates']:
                coords = poly[0]
                        # Convert coordinates to pygame format [(x, y), ...]
                points = [(x, y) for x, y in coords]
        
                if props.get("terrain") == "mountain":
                    color = (139, 69, 19)  # Brown for mountains
                    print(f"Creating mountain terrain with {len(points)} points")
                    
                elif props.get("terrain") == "river":
                    color = (30, 144, 255) # Blue for rivers
                    print(f"Creating river terrain with {len(points)} points")
                    
                else:
                    color = (128, 128, 128) # Default gray
                    print(f"Creating unknown terrain type with {len(points)} points")
                
                terrain_entity = terrain(points, color)

                if props.get("terrain") == "mountain":
                    self.mountains.append(terrain_entity)
                elif props.get("terrain") == "river":
                    self.rivers.append(terrain_entity)
        else:
            print(f"Warning: Unsupported geometry type {geometry['type']}")
            return
        print(f"✓ Created terrain layer: {len(self.mountains)} mountains, {len(self.rivers)} rivers")



    def get_all_entities(self):
        """Return all loaded entities as a tuple."""
        return (
            self.provinces,
            self.cities,
            self.castles,
            self.checkpoints,
            self.mountains,
            self.rivers
        )