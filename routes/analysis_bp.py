
from flask import Blueprint, request, jsonify, request
import requests
from services.model_service import model, transform, device
import torch
import io
import base64
import ee
from PIL import Image
from geopy.geocoders import Nominatim

analysis_bp = Blueprint('analysis_bp', __name__)


def split_image(image, patch_size=64):

    patches = []

    width, height = image.size

    for y in range(0, height, patch_size):

        for x in range(0, width, patch_size):

            patch = image.crop(
                (x, y, x + patch_size, y + patch_size)
            )

            patches.append(patch)

    return patches



def analyze_image(image, area_km2=0):
    patches = split_image(image)
    total = len(patches)

    if total == 0:
        return {
            "agricultural_percentage": 0, "desert_percentage": 0,
            "tree_percentage": 0, "urban_percentage": 0, "water_percentage": 0,
            "estimated_population": 0,
            "agricultural_population": 0, "desert_population": 0,
            "tree_population": 0, "urban_population": 0, "water_population": 0,
        }

    DENSITY_AGRICULTURAL = 500    # rural/farming density
    DENSITY_DESERT       = 20     # very sparse
    DENSITY_TREE         = 20     # dense forest, sparse population
    DENSITY_URBAN        = 5000   # urban/suburban
    DENSITY_WATER        = 0      # no population on water

    DENSITY_MAP = {
        0: DENSITY_AGRICULTURAL,
        1: DENSITY_DESERT,
        2: DENSITY_TREE,
        3: DENSITY_URBAN,
        4: DENSITY_WATER,
    }

    # Area each 64x64 patch represents in km²
    patch_area_km2 = area_km2 / total

    agricultural_count = 0
    desert_count       = 0
    tree_count         = 0
    urban_count        = 0
    water_count        = 0

    agricultural_population = 0
    desert_population       = 0
    tree_population         = 0
    urban_population        = 0
    water_population        = 0  # always 0

    for patch in patches:
        x = transform(patch).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(x)
            prediction = torch.argmax(output, 1).item()

        patch_population = patch_area_km2 * DENSITY_MAP.get(prediction, 0)

        if prediction == 0:
            agricultural_count += 1
            agricultural_population += patch_population
        elif prediction == 1:
            desert_count += 1
            desert_population += patch_population
        elif prediction == 2:
            tree_count += 1
            tree_population += patch_population
        elif prediction == 3:
            urban_count += 1
            urban_population += patch_population
        elif prediction == 4:
            water_count += 1
            # water_population stays 0

    agricultural_percentage = (agricultural_count / total) * 100
    desert_percentage       = (desert_count       / total) * 100
    tree_percentage         = (tree_count         / total) * 100
    urban_percentage        = (urban_count        / total) * 100
    water_percentage        = (water_count        / total) * 100

    estimated_population = (
        agricultural_population + desert_population +
        tree_population + urban_population
        # water intentionally excluded
    )

    return {
        "agricultural_percentage": round(agricultural_percentage, 2),
        "desert_percentage":       round(desert_percentage,       2),
        "tree_percentage":         round(tree_percentage,         2),
        "urban_percentage":        round(urban_percentage,        2),
        "water_percentage":        round(water_percentage,        2),
        "estimated_population":    round(estimated_population),
        "agricultural_population": round(agricultural_population),
        "desert_population":       round(desert_population),
        "tree_population":         round(tree_population),
        "urban_population":        round(urban_population),
        "water_population":        0,
    }

@analysis_bp.route("/analyze/before_after_image", methods=["POST"])
def analyze_before_after_image():
    try:
        data = request.json
        area_size = data["area_km2"]

        after_data  = data["after_image"].split(",")[1]
        after_bytes = base64.b64decode(after_data)
        after_img   = Image.open(io.BytesIO(after_bytes)).convert("RGB")
        after_result = analyze_image(after_img, area_km2=area_size)

        before_data  = data["before_image"].split(",")[1]
        before_bytes = base64.b64decode(before_data)
        before_img   = Image.open(io.BytesIO(before_bytes)).convert("RGB")
        before_result = analyze_image(before_img, area_km2=area_size)

        # Determine urbanicity label from urban patch percentage
        def urbanicity_label(result):
            urban_pct = result["urban_percentage"]
            if urban_pct >= 70:
                return "Highly Urbanized"
            elif urban_pct >= 45:
                return "Urbanized/Suburb"
            elif urban_pct >= 20:
                return "Rural Area"
            else:
                return "Dense Forest / Natural"

        before_urbanicity = urbanicity_label(before_result)
        after_urbanicity  = urbanicity_label(after_result)

        # Overall urban-percent change (for backward compatibility)
        before_urban_pct = before_result["urban_percentage"]
        after_urban_pct  = after_result["urban_percentage"]

        return jsonify({
            # --- backward-compatible fields ---
            "before_percent":       before_urban_pct,
            "after_percent":        after_urban_pct,
            "change":               abs(round(after_urban_pct - before_urban_pct, 2)),
            "before_urbanicity":    before_urbanicity,
            "after_urbanicity":     after_urbanicity,
            "before_est_population": before_result["estimated_population"],
            "after_est_population":  after_result["estimated_population"],

            # --- full breakdown for pie charts ---
            "before_breakdown": {
                "agricultural_percentage": before_result["agricultural_percentage"],
                "desert_percentage":       before_result["desert_percentage"],
                "tree_percentage":         before_result["tree_percentage"],
                "urban_percentage":        before_result["urban_percentage"],
                "water_percentage":        before_result["water_percentage"],
                "agricultural_population": before_result["agricultural_population"],
                "desert_population":       before_result["desert_population"],
                "tree_population":         before_result["tree_population"],
                "urban_population":        before_result["urban_population"],
                "water_population":        0,
                "estimated_population":    before_result["estimated_population"],
            },
            "after_breakdown": {
                "agricultural_percentage": after_result["agricultural_percentage"],
                "desert_percentage":       after_result["desert_percentage"],
                "tree_percentage":         after_result["tree_percentage"],
                "urban_percentage":        after_result["urban_percentage"],
                "water_percentage":        after_result["water_percentage"],
                "agricultural_population": after_result["agricultural_population"],
                "desert_population":       after_result["desert_population"],
                "tree_population":         after_result["tree_population"],
                "urban_population":        after_result["urban_population"],
                "water_population":        0,
                "estimated_population":    after_result["estimated_population"],
            },
        })

    except Exception as e:
        return jsonify({"error": str(e)})
    
@analysis_bp.route("/before_after", methods=["POST"])
def before_after():
    data = request.json
    # babalikan
    # image_data = data["image"]
    # image_data = image_data.split(",")[1]
    # image_bytes = base64.b64decode(image_data)

    # image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    # forest_percent = analyze_image(image)
    
    before_base64 = "" 

    if "coords" in data:
            try:
                geometry = ee.Geometry.Polygon(data["coords"])
                lat = data["lat"]
                lng = data["lng"]

                geolocator = Nominatim(user_agent = "geo_app")

                location = geolocator.reverse(
                    f"{lat}, {lng}",
                    language = 'en'
                )

                city = "Unknown City"
                region = "Unknown Region"
                country = "Unknown Country"
                if location and location.raw.get("address"):
                    address = location.raw["address"]
                    
                    country = (
                        address.get("country") or 
                        "Unknown Country"
                    )

                    city = (
                        address.get("city") or
                        address.get("town") or
                        address.get("municipality") or
                        address.get("village") or
                        "Unknown City"
                    )
                    region = (
                        address.get("region") or
                        address.get("state") or
                        address.get("state_district") or
                        "Unknown Region"
                    )

                area_meters = geometry.area().getInfo()
                area_km2 = area_meters / 1000000

                before_year = data.get("before_year", "2014")
                start_date = f"{before_year}-01-01"
                end_date = f"{before_year}-12-31"

                before_collection = (
                    ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
                    .filterBounds(geometry)
                    .filterDate(start_date, end_date )
                    .filter(ee.Filter.lt('CLOUD_COVER', 30))
                )

                before_image = before_collection.median().clip(geometry)

        
                scaled = before_image.select(['SR_B4', 'SR_B3', 'SR_B2']) \
                    .multiply(0.0000275).add(-0.2)

                before_rgb = scaled.visualize(
                    min=0.03,
                    max=0.5,
                    gamma=1.4
                )

                thumbnail_url = before_rgb.getThumbURL({
                    'dimensions': 1024,
                    'region': geometry,
                    'format': 'png'
                })

                
                response = requests.get(thumbnail_url)
                if response.status_code == 200:
                    before_base64 = base64.b64encode(response.content).decode('utf-8')
                print(region)
            except Exception as e:
                print(f"Error: {e}")
                before_base64 = ""

    return jsonify({
            # "forest_percent": round(forest_percent, 2),
            "before_image": "data:image/png;base64," + before_base64 if before_base64 else None,
            "area_km2": round(area_km2, 2),
            "city": city,
            "region": region,
            "country": country,
            "latitude": lat,
            "longitude": lng
            
        })