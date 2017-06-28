from .models import Ytvideo, Screenshot, Player, Video
from math import ceil
import random

def mass_update():
    players = Player.objects.filter(active=True)
    for player in players:
        print 'Working on ' + player.name + '...'
        r = player.update_vids()

        if r:
            print '[SUCCESS] + ' + player.name + ' updated!'
        else:
            print '[FAIL] + ' + player.name


def smart_download(num=10):
    # get the total num of vids
    last_vid = Video.objects.last()
    first_vid = Video.objects.first()
    last_ind = last_vid.pk
    first_ind = first_vid.pk

    downloaded_vids = []

    while num > 0:

        print 'Working on ' + str(num) + 'th video..'
        # get the random index
        # random.seed(random.randint(1, 100))
        random_ind = random.randint(first_ind, last_ind)
        try:
            vid = Video.objects.get(pk=random_ind)
        except:
            print 'Vid not found'
            continue
        else:
            print 'video is ' + str(vid) + ' ' + vid.name
            # also check if the vid flag is downloaded
            if vid.is_downloaded:
                print '[SKIP] Already downloaded'
                continue

            try:
                vid.download_vid()
            except:
                # revert back
                raise
                print '[SKIP] Download error ' + str(vid) + ' ' + vid.name
                vid.is_downloaded = False
                vid.save()
            else:
                downloaded_vids.append(str(vid.pk) + ' ' + vid.name)

                # decrement the count
                num -= 1
                print str(num) + '[DONE] th video completes..'

    for downloaded_vid in downloaded_vids:
        print downloaded_vid

    print '[DONE] downloading'




def mass_download():
    players = Player.objects.filter(active=True)

    vid_set = []

    for player in players:
        vids = player.video_set.filter(is_downloaded=False)
        vids = [v for v in vids]
        random.shuffle(vids)
        print player.name
        if vids:
            last_vid = vids[0]
            vid_set.append(last_vid)

    if vid_set:
        for vid in vid_set:

            # double check is_downloaded to be atomic
            if not vid.is_downloaded:
                print 'Downloading ' + vid.name + '...'
                try:
                    vid.download_vid()
                except:
                    # revert back
                    vid.is_downloaded = False
                    vid.save()
            else:
                print 'Already Downloaded ' + vid.name + '...'


def mass_process():
    vids = Video.objects.filter(is_processed=False).filter(is_downloaded=True)
    vids = [v for v in vids]

    random.shuffle(vids)

    vids = vids[:6]
    # print vids

    for vid in vids:
        print 'Working on ' + str(vid.pk)
        try:
            # atomic
            if not vid.is_processed:
                vid.generate_sc()
        except:
            # revert back the flag
            vid.is_processed = False
            vid.save()
            # ignore the bug and move on
            continue


def smart_process(num=10):
    last_vid = Video.objects.last()
    last_ind = last_vid.pk
    first_vid = Video.objects.first()
    first_ind = first_vid.pk

    processed_vids = []

    while num > 0:

        print 'Working on ' + str(num) + 'th video..'

        # get the random index
        random_ind = random.randint(first_ind, last_ind)
        try:
            vid = Video.objects.get(pk=random_ind)
        except:
            print 'Video not found..'
            continue
        else:
            print 'video is ' + str(vid) + ' ' + vid.name
            # check if the vid flag is good
            if vid.is_processed:
                print '[SKIP] already processed'
                continue

            if not vid.is_downloaded:
                print '[SKIP] Not yet downloaded'
                continue

            try:
                vid.generate_sc()
            except:
                print '[SKIP] Process error ' + str(vid) + ' ' + vid.name
                # raise


                # revert back
                # vid.is_processed = False
                # vid.save()

                # delete and pass
                vid.delete_vid()
                num -= 1
            else:
                processed_vids.append(str(vid.pk) + ' ' + vid.name)

                # decrement the count
                num -= 1
                print str(num) + '[DONE] th video completes..'

    for processed_vid in processed_vids:
        print processed_vid

    print '[DONE] processing..'




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


def mass_split():
    vids = Video.objects.filter(is_downloaded=True).filter(is_processed=True).filter(is_splitted=False)

    for vid in vids:
        vid.split_video()


def update_screenshot_name():
	screenshots = Screenshot.objects.all()

	for s in screenshots:
		path = s.path
		name = path.split('/')[-1]
		name = name.replace('.jpg', '')
		s.name = name
		s.save()
