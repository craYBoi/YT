from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import FormView
from django.shortcuts import redirect
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import subprocess
import os
import string

import core
from .models import Ytvideo, Player, Vidcue, Hero, Video, Videocue, Videosc
from .utils import mass_screenshot

def capture(request):
	context = {
	}

	if request.GET:
		if request.GET.get('capture'):
			screen = int(request.GET.get('capture'))
			# secondary screen
			if screen == 1:
				m = core.Machine(screen=1)
				m.run(screen)
			if screen == 2:
				m = core.Machine(screen=2)
				m.run(screen)


	return render(request, 'capture.html', context)


def cms(request):

	videos = Ytvideo.objects.filter(is_uploaded=False).order_by('-timestamp')
	players = Player.objects.all()
	heros = Hero.objects.order_by('name')


	paginator = Paginator(videos, 3)
	page = request.GET.get('page')

	context = {
		'players': players,
	}

	# upload all
	if request.GET and request.GET.get('upload_all'):

		vids_string = ''

		vids = Ytvideo.objects.filter(is_trimmed=True).filter(is_uploaded=False)
		for vid in vids:
			vid.is_uploaded = True
			vid.save()

			vids_string = vids_string + vid.trimmed_path + ' '
		# for vid in vids:
		# 	vid.upload()

		vids_string = vids_string.strip()
		subprocess.call(['sh', 'video/scripts/mass_upload.sh'])



	# delete vid
	if request.POST and request.POST.get('vid_delete'):

		print '\n\n\n\n START DELETING... \n\n\n\n'
		pk = request.POST.get('vid_id')
		vid = Ytvideo.objects.get(pk=int(pk))

		context['msg'] = 'Video has been successfully updated.\n' + vid.name

		vid.delete_vid()
		print 'Done deleting..'

		context['videos'] = Ytvideo.objects.filter(is_uploaded=False).order_by('-timestamp')[:3]



	if request.POST and request.POST.get('vid_name'):


		name = request.POST.get('vid_name')
		hero = request.POST.get('vid_hero')
		player = request.POST.get('vid_player')
		# desc = request.POST.get('vid_desc')
		tags = request.POST.get('vid_tags')
		pk = request.POST.get('vid_id')

		# print hero
		# print desc

		vid = Ytvideo.objects.get(pk=int(pk))
		vid.name = name
		vid.hero = hero

		# if desc:
		# 	vid.description = desc
		if tags:
			vid.tags = string.replace(tags.strip(), ' ', ',')


		player = Player.objects.get(pk=player)
		vid.player = player
		vid.description = vid.get_desc()
		vid.tags = vid.get_tag()


		vid.save()

		videos = Ytvideo.objects.filter(is_uploaded=False).order_by('-timestamp')
		context['msg'] = 'Video has been successfully updated.\n' + vid.name


	if request.POST and request.POST.get('vid_cue1_start_m'):

		pk = request.POST.get('vid_id')
		vid = Ytvideo.objects.get(pk=pk)

		vid_cue1_start_m = request.POST.get('vid_cue1_start_m')
		vid_cue1_start_s = request.POST.get('vid_cue1_start_s')
		vid_cue1_end_m = request.POST.get('vid_cue1_end_m')
		vid_cue1_end_s = request.POST.get('vid_cue1_end_s')
		vid_cue2_start_m = request.POST.get('vid_cue2_start_m')
		vid_cue2_start_s = request.POST.get('vid_cue2_start_s')
		vid_cue2_end_m = request.POST.get('vid_cue2_end_m')
		vid_cue2_end_s = request.POST.get('vid_cue2_end_s')

		if vid_cue1_start_m and vid_cue1_start_s and vid_cue1_end_m and vid_cue1_end_s:

			# do datetime conversion
			vid_cue1_start = '00:' + str(vid_cue1_start_m) + ':' + str(vid_cue1_start_s)
			vid_cue1_end = '00:' + str(vid_cue1_end_m) + ':' + str(vid_cue1_end_s)

			Vidcue.objects.create(
				video=vid,
				start=vid_cue1_start,
				end=vid_cue1_end,
				)

		if vid_cue2_start_m and vid_cue2_start_s and vid_cue2_end_m and vid_cue2_end_s:

			# do datetime conversion
			vid_cue2_start = '00:' + str(vid_cue2_start_m) + ':' + str(vid_cue2_start_s)
			vid_cue2_end = '00:' + str(vid_cue2_end_m) + ':' + str(vid_cue2_end_s)

			Vidcue.objects.create(
				video=vid,
				start=vid_cue2_start,
				end=vid_cue2_end,
				)

		# trim
		vid.trim()

		# analyze hero, only for 1 vid
		if vid.is_analyzed:
			vid.compute_hero(vid_cue1_start, vid_cue1_end)


		context['msg'] = 'Trimmed successfully. ' + vid.name
		videos = Ytvideo.objects.filter(is_uploaded=False).order_by('-timestamp')

	if request.POST and request.POST.get('vid_upload'):

		pk = request.POST.get('vid_id')
		vid = Ytvideo.objects.get(pk=pk)

		vid.upload()
		context['msg'] = 'Uploaded successfully. ' + vid.name

	if request.POST and request.POST.get('analyze'):
		mass_screenshot()
		context['msg'] = 'Analyzed done!.. '


	try:
		videos = paginator.page(page)
	except PageNotAnInteger:
		videos = paginator.page(1)
	except EmptyPage:
		videos = paginator.page(paginator.num_pages)


	context['videos'] = videos
	return render(request, 'cms.html', context)


def cms2(request):

	# delete video
	if request.method == 'POST' and request.POST.get('video_id'):

		video_pk = request.POST.get('video_id')
		vid = Video.objects.get(pk=video_pk)

		vid.delete_vid()


	videos = Video.objects.filter(is_downloaded=True).filter(is_processed=True)

	paginator = Paginator(videos, 10)
	page = request.GET.get('page')

	try:
		videos = paginator.page(page)
	except PageNotAnInteger:
		videos = paginator.page(1)
	except EmptyPage:
		videos = paginator.page(paginator.num_pages)

	context = {
		'videos': videos,
	}


	return render(request, 'cms2.html', context)

def video(request, vid_id):

	vid = Ytvideo.objects.get(pk=vid_id)
	context = {
		'video': vid,
	}


	return render(request, 'video.html', context)

def video2(request, vid_id):

	vid = Video.objects.get(pk=vid_id)
	cues = vid.videocue_set.all()

	# print cues
	context = {
		'video': vid,
		'cues': cues,
	}

	# open video
	if request.method == 'GET' and request.GET.get('video_id'):
		r = vid.open_vid()

	# update video cues
	if request.method == 'POST' and request.POST.get('videocue_start'):
		videocue_pk = request.POST.get('videocue_id')
		videocue_start = request.POST.get('videocue_start')
		videocue_end = request.POST.get('videocue_end')
		videocue = Videocue.objects.get(pk=videocue_pk)

		# print videocue_pk, videocue_start, videocue_end
		videocue.save_cue(videocue_start, videocue_end)
		videocue.is_updated = True
		videocue.save()


	# trim
	if request.method == 'POST' and request.POST.get('videocue_trim'):
		videocue_pk = request.POST.get('videocue_id')
		videocue = Videocue.objects.get(pk=videocue_pk)
		videocue.trim()

	# title, hero and desc
	if request.method == 'POST' and request.POST.get('videocue_title'):
		videocue_pk = request.POST.get('videocue_id')
		videocue = Videocue.objects.get(pk=videocue_pk)

		videocue_title = request.POST.get('videocue_title')
		videocue_hero = request.POST.get('videocue_hero')

		videocue.title = videocue_title
		videocue.hero = videocue_hero
		videocue.desc = videocue.get_desc()
		videocue.save()

	# upload
	if request.method == 'POST' and request.POST.get('videocue_upload'):
		videocue_pk = request.POST.get('videocue_id')
		videocue = Videocue.objects.get(pk=videocue_pk)

		videocue.is_uploaded = True
		videocue.save()
		videocue.upload()

	return render(request, 'video2.html', context)


def open(request):

	context = {}

	if request.GET:
		pk = request.GET.get('video_id')
		vid = Ytvideo.objects.get(pk=pk)

		context['video'] = vid
		r = vid.open_vlc()


	return render(request, 'video.html', context)


@csrf_exempt
def ajax_open(request):

	print request.POST
	if request.POST:
		# pk = request.POST.get('video_id')
		# vidcue = Videocue.objects.get(pk=int(pk))
		# vid = vidcue.video

		pk = request.POST.get('video_id')
		vid = Video.objects.get(pk=int(pk))

		r = vid.open_vid()

		data = {
			'success': 1,
		}

		return JsonResponse(data)


@csrf_exempt
def ajax_update(request):

	if request.POST:
		pk = request.POST.get('video_id')
		vidcue = Videocue.objects.get(pk=int(pk))

		vidcue_start = request.POST.get('videocue_start')
		vidcue_end = request.POST.get('videocue_end')

		vidcue.save_cue(vidcue_start, vidcue_end)
		vidcue.is_updated = True
		vidcue.save()

		data = {
			'success': 1,
		}

		return JsonResponse(data)


@csrf_exempt
def ajax_trim(request):

	print request.POST

	data = {}

	if request.POST:
		pk = request.POST.get('video_id')
		vidcue = Videocue.objects.get(pk=int(pk))

		r = vidcue.trim()

		if r:
			data['success'] = 1

		return JsonResponse(data)


@csrf_exempt
def ajax_upload(request):

	print request.POST

	data = {}

	if request.POST:
		pk = request.POST.get('video_id')
		vidcue = Videocue.objects.get(pk=int(pk))

		r = vidcue.upload()

		if r:
			data['success'] = 1

		return JsonResponse(data)


@csrf_exempt
def ajax_info(request):

	print request.POST

	data = {}

	if request.POST:
		pk = request.POST.get('video_id')
		vidcue = Videocue.objects.get(pk=int(pk))
		vidcue_hero = request.POST.get('video_hero')
		vidcue_title = request.POST.get('video_title')

		vidcue.title = vidcue_title
		vidcue.hero = vidcue_hero
		vidcue.desc = vidcue.get_desc()
		vidcue.save()

		data['vidcue_title'] = vidcue.title
		data['vidcue_hero'] = vidcue.hero
		data['vidcue_desc'] = vidcue.desc

		return JsonResponse(data)
