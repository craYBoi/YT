from .models import Ytvideo

a = Ytvideo.objects.get(pk=409)

a.analyze()