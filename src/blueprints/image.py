import random
import string
from io import BytesIO

from PIL import Image
from flask import Blueprint, Response

from src.connections import config
from src.utils.access import *
from src.utils.utils import *

import base64

app = Blueprint('images', __name__)

MAX_SIZE = config['max_image_size']
IMAGE_ID_GENERATE_LEN = 30


@app.route("/<imageId>.<imageExt>")
@app.route("/<imageId>")
def imageGet(imageId, imageExt=None):
    if not config['save_images_to_db']:
        return jsonResponse("Конфигурацией сервера задано, что он не должен отдавать картинки. Настройте их как раздачу статики через сторонний сервер для статики", HTTP_INTERNAL_ERROR)

    if not imageId.isnumeric():
        return jsonResponse("ID изображения должно быть целым числом", HTTP_INVALID_DATA)
    resp = DB.execute(sql.selectImageById, [imageId])
    if (not resp) or ((imageExt is not None) and (resp['type'] != imageExt)):
        return jsonResponse("Изображение не найдено", HTTP_NOT_FOUND)
    # base64Data = resp['base64']
    # imageBytes = base64.b64decode(base64Data)
    imageBytes = resp['bytes']
    imageLen = len(imageBytes)

    res = Response(imageBytes, mimetype=f'image/{resp["type"]}')
    res.headers['Content-Length'] = imageLen
    return res


_leftLen = len('data:image/')
_rightLen = len(';base64')
@app.route("", methods=["POST"])
@login_and_email_confirmation_required
def imageUpload(userData):
    try:
        req = request.json
        dataUrl = req['dataUrl']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    [dataUrl, base64Data] = dataUrl.split(',')
    imageType = dataUrl[_leftLen: -_rightLen]

    imageBytes = base64.b64decode(base64Data)
    img = Image.open(BytesIO(imageBytes))  # open image

    (wOrig, hOrig) = img.size
    maxSize = max(wOrig, hOrig)

    if maxSize > MAX_SIZE:  # image bigger than MAX_SIZE. Need to resize
        multiplier = maxSize / MAX_SIZE
        w = int(wOrig / multiplier)
        h = int(hOrig / multiplier)

        img = img.resize((w, h), Image.Resampling.LANCZOS)  # resize to MAX_SIZE

    saveFormat = 'JPEG'
    if img.mode == 'RGBA':
        saveFormat = 'PNG'

    if config['save_images_to_db']:
        optimized = BytesIO()
        img.save(optimized, format=saveFormat, optimize=True, quality=85)
        hex_data = optimized.getvalue()

        resp = DB.execute(sql.insertImage, [userData['id'], saveFormat.lower(), hex_data])
        return jsonResponse({'id': resp['id']})

    chars = string.ascii_letters + string.digits
    randomId = ''.join(random.choice(chars) for _ in range(IMAGE_ID_GENERATE_LEN))
    fileName = f"{userData['id']}_{randomId}.{saveFormat.lower()}"
    saveFullPath = os.path.join(config['save_images_folder'], fileName)
    img.save(saveFullPath, format=saveFormat, optimize=True, quality=85)
    return jsonResponse({'id': fileName})


@app.route("", methods=["DELETE"])
@login_required_return_id
def imageDelete(userId):
    try:
        req = request.json
        imageId = req['imageId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if config['save_images_to_db']:
        resp = DB.execute(sql.selectImageById, [imageId])
        if not resp:
            return jsonResponse("Изображение не найдено", HTTP_NOT_FOUND)

        DB.execute(sql.deleteImageByIdAuthor, [imageId, userId])
        return jsonResponse("Изображение удалено если вы его автор")

    fileName = f"{imageId}"
    fullPath = os.path.join(config['save_images_folder'], fileName)
    if not os.path.isfile(fullPath):
        return jsonResponse("Изображение не найдено", HTTP_NOT_FOUND)

    os.remove(fullPath)
    return jsonResponse("Изображение удалено")
