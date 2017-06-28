from .models import VidImage
from PIL import Image
import os

def open_vidimage():
    a = VidImage.objects.first()

    print('Current Dir: %s') % (os.getcwd())
    print('Image Path: %s') % (a.path)

    im = Image.open(a.path)
    im.show()
