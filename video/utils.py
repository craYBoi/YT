from .models import Ytvideo, Screenshot
from math import ceil

def mass_screenshot():
    vids = Ytvideo.objects.filter(is_analyzed=False)

    # first update all the flags
    for vid in vids:
        vid.is_analyzed = True
        vid.save()

    print 'Starting mass screenshot..'

    for vid in vids:
        vid.generate_screenshots()

    print 'Done -- ' + str(vid.pk)


def update_screenshot_name():
	screenshots = Screenshot.objects.all()

	for s in screenshots:
		path = s.path
		name = path.split('/')[-1]
		name = name.replace('.jpg', '')
		s.name = name
		s.save()
