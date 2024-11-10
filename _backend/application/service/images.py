# for sproadic use
import os
import requests
sessionBuilder = SessionBuilder()
sessionBuilder.authenticate()
session = sessionBuilder.session


def requestCarLogos(session):

    # iRacingAPI
    response = session.get('https://members-ng.iracing.com/data/car/assets')

    data = response.json()
    data = requests.get(data["link"]).json()

    relativeImageUrl = "https://images-static.iracing.com/"

    cars = set()
    for car_id in data:
        cars.add(car_id)

    for car_id in cars:
        logoUrl = data[car_id]["logo"]
        print(car_id, logoUrl)
        if (logoUrl):
            downloadAndSaveImage(relativeImageUrl + logoUrl, car_id, "cars")

def requestSeriesLogos(session):

    # iRacingAPI
    response = session.get('https://members-ng.iracing.com/data/series/assets')

    # check if iRacing API is up and subsessionId is valid
    if not responseIsValid(response):
        return {
            "response": response,
            "service": None
        }

    data = response.json()
    data = requests.get(data["link"]).json()

    relativeImageUrl = "https://images-static.iracing.com/"

    series = set()
    for series_id in data:
        series.add(series_id)

    for series_id in series:
        logoUrl = data[series_id]["logo"]
        print(series_id, logoUrl)
        if (logoUrl):
            downloadAndSaveImage(relativeImageUrl + logoUrl, series_id, "series")

def downloadAndSaveImage(url, filename, type):

    folderPath = "images/" + type

    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for error HTTP statuses

    # Create the "images" folder if it doesn't exist
    os.makedirs(folderPath, exist_ok=True)

    # Check if the image is already in PNG format
    if response.headers['Content-Type'] == 'image/png':
        file_path = os.path.join(folderPath, filename + ".png")
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    break
                f.write(chunk)
    else:
        # Convert the image to PNG using Pillow
        from PIL import Image

        image = Image.open(response.raw)
        file_path = os.path.join(folderPath, filename)
        image.save(file_path, 'PNG')

requestCarLogos(session)
# requestSeriesLogos(session)