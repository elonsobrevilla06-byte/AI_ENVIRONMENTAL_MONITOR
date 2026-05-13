from flask import Flask, render_template, request, jsonify
import torch
import torch.nn as nn
import io 
import base64
import geemap
import ee
from torchvision import transforms,models
from geopy.geocoders import Nominatim
from PIL import Image
import requests
from routes.country_bounds import country_bp

from database_models.country_bounds import get_country_bounds


ee.Initialize(project='golden-system-465607-e5')

app = Flask(__name__)

app.register_blueprint(country_bp)


model = models.resnet18(pretrained=False)

model.fc = nn.Linear(model.fc.in_features,2)

model.load_state_dict(torch.load("forest_model_epoch_14.pth"))

model.eval()

transform = transforms.Compose([
    transforms.Resize((64,64)),
    transforms.ToTensor()
])

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

def analyze_image(image):

    patches = split_image(image)

    tree_count = 0

    for patch in patches:

        x = transform(patch).unsqueeze(0)

        with torch.no_grad():

            output = model(x)

            prediction = torch.argmax(output, 1)

        if prediction.item() == 1:
            tree_count += 1

    total = len(patches)

    forest_percent = (tree_count / total) * 100

    return forest_percent

@app.route("/analyze/before_after_image", methods = ["POST"])
def analyze_before_after_image():
    try:
        data = request.json
        area_size = data["area_km2"]
        after_data = data["after_image"].split(",")[1]
        after_bytes = base64.b64decode(after_data)
        after_img = Image.open(io.BytesIO(after_bytes)).convert("RGB")
        after_percent = analyze_image(after_img)

        before_data = data["before_image"].split(",")[1]
        before_bytes = base64.b64decode(before_data)
        before_img = Image.open(io.BytesIO(before_bytes)).convert("RGB")
        before_percent = analyze_image(before_img)

        before_urbanicity = ""
        before_est_population = 0
        after_urbanicity = ""
        after_est_population = 0


        DENSITY_HIGHLY_URBANIZED = 22561
        DENSITY_URBAN = 5000
        DENSITY_RURAL = 500
        DENSITY_FOREST = 20


        if round(before_percent,2) <= 20:
            before_urbanicity = "Highly Urbanized"
            before_est_population = area_size * DENSITY_HIGHLY_URBANIZED
        elif round(before_percent,2) >= 21 and round(before_percent,2) <= 45:
            before_urbanicity = "Urbanized/Suburb"
            before_est_population = area_size * DENSITY_URBAN           
        elif round(before_percent,2) >= 46 and round(before_percent,2) <= 70:
            before_urbanicity = "Rural Area"
            before_est_population = area_size * DENSITY_RURAL
        else:
            before_urbanicity = "Dense Forest"
            before_est_population = area_size * DENSITY_FOREST

        if round(after_percent,2) <= 20:
            after_urbanicity = "Highly Urbanized"
            after_est_population = area_size * DENSITY_HIGHLY_URBANIZED
        elif round(after_percent,2) >= 21 and round(after_percent,2) <= 45:
            after_urbanicity = "Urbanized/Suburb"
            after_est_population = area_size * DENSITY_URBAN
        elif round(after_percent,2) >= 46 and round(after_percent,2) <= 70:
            after_urbanicity = "Rural Area"
            after_est_population = area_size * DENSITY_RURAL
        else:
            after_urbanicity = "Dense Forest"
            after_est_population = area_size * DENSITY_FOREST

        return jsonify({
            "after_percent": round(after_percent,2),
            "before_percent": round(before_percent,2),
            "before_urbanicity": before_urbanicity,
            "after_urbanicity": after_urbanicity,
            "before_est_population": before_est_population,
            "after_est_population": after_est_population,
            "change": abs(round(after_percent - before_percent, 2)),
        })

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/before_after", methods=["POST"])
def before_after():
    data = request.json
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

@app.route("/")
def home():
    data = get_country_bounds()

    raw = data["data"]

    
    countries = [
        {
            "country_code": row["country_code"],
            "bounds": row["bounds"]
        }
        for row in raw
    ]
    print(data)

    return render_template("index.html", countries=countries)



if __name__ == "__main__":
    app.run(debug=True)