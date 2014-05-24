from django.shortcuts import render

# Create your views here.

from sorl.thumbnail import get_thumbnail, images
from Lushu import settings
from django.core.files.base import File
import os
from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponse

def getImage(request, imageName, width, height):
    filePath = os.path.join(settings.MEDIA_ROOT, "images", imageName + ".jpg").replace("\\", "/")
    imageFile = open(filePath, 'rb')
    im = get_thumbnail(imageFile, width + "x" + height)
    imageFile = open(os.path.join(settings.MEDIA_ROOT, im.name).replace("\\", "/"), "rb")
    imageContent = imageFile.read()
    return HttpResponse(imageContent, mimetype="image/jpeg")