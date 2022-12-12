from io import BytesIO

from PIL import Image
from flask import Blueprint, Response

from connections import config, DB
from utils.access import *
from utils.utils import *

import base64

app = Blueprint('images', __name__)

MAX_SIZE = config['max_image_size']


@app.route("/<imageId>.<imageExt>")
@app.route("/<imageId>")
def imageGet(imageId, imageExt=None):
    if not imageId.isnumeric():
        return Response("ID изображения должно быть целым числом", HTTP_INVALID_DATA)
    resp = DB.execute(sql.selectImageById, [imageId])
    if (not resp) or ((imageExt is not None) and (resp['type'] != imageExt)):
        return Response("Изображение не найдено", HTTP_NOT_FOUND)
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

    optimized = BytesIO()
    saveFormat = 'JPEG'
    if img.mode == 'RGBA':
        saveFormat = 'PNG'
    img.save(optimized, format=saveFormat, optimize=True, quality=85)
    hex_data = optimized.getvalue()

    resp = DB.execute(sql.insertImage, [userData['id'], saveFormat.lower(), hex_data])
    return jsonResponse(resp)


@app.route("", methods=["DELETE"])
@login_required_return_id
def imageDelete(userId):
    try:
        req = request.json
        imageId = req['imageId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)


    resp = DB.execute(sql.selectImageById, [imageId])
    if not resp:
        return jsonResponse("Изображение не найдено", HTTP_NOT_FOUND)

    DB.execute(sql.deleteImageByIdAuthor, [imageId, userId])
    return jsonResponse("Изображение удалено если вы его автор")
