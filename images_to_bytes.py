import base64
from PIL import Image
from io import BytesIO

from connections import DB

MAX_SIZE = 512

if __name__ == '__main__':
    images = DB.execute("SELECT * FROM images", [], manyResults=True)
    #print(images)
    for image in images:
        base64Data = image['base64']
        imageBytes = base64.b64decode(base64Data)

        img = Image.open(BytesIO(imageBytes))  # open image

        (wOrig, hOrig) = img.size
        maxSize = max(wOrig, hOrig)

        if maxSize > MAX_SIZE:  # image lower than MAX_SIZE
            multiplier = maxSize / MAX_SIZE
            w = int(wOrig / multiplier)
            h = int(hOrig / multiplier)

            img = img.resize((w, h), Image.Resampling.LANCZOS)  # resize to MAX_SIZE

        optimized = BytesIO()
        saveFormat = 'JPEG'
        if img.mode == 'RGBA':
            saveFormat = 'PNG'
        img.save(optimized, format=saveFormat, optimize=True, quality=85)
        hex_data = optimized.getvalue()

        res = DB.execute("UPDATE images SET bytes = %s WHERE id = %s RETURNING *", [hex_data, image['id']])
        print("UPDATED")

    print("-----OK------")
    images = DB.execute("SELECT * FROM images;", [], manyResults=True)
    #print(images)
