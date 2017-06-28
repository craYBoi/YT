from __future__ import unicode_literals

from django.db import models

import helpers

from bs4 import BeautifulSoup
from selenium import webdriver

import subprocess
import skvideo.io
import numpy as np
import cv2
import os
import json
from PIL import Image, ImageStat
import datetime
from dateutil.relativedelta import relativedelta
import re
import signal
import random

from collections import defaultdict
import bisect

# from video2.models import Video

IN_FOLDER = '/hdd/things/captures'
OUT_FOLDER = '/hdd/things/trimmed'
CAPTURE_FOLDER2 = '/hdd/things/captures2'
TRIMMED_FOLDER2 = '/hdd/things/trimmed2'
TEMPLATE_PATH = 'ytow/static/template/template2.jpg'
TEMPLATE_PATH2 = 'ytow/static/template/template1.jpg'
HERO_AVATAR_PATH = 'ytow/static/template/heros'



class Player(models.Model):
	url = models.CharField(max_length=120)
	name = models.CharField(max_length=50)
	twitter = models.CharField(max_length=100, blank=True, null=True)
	active = models.BooleanField(default=True)
	recording = models.BooleanField(default=False)
	is_k = models.BooleanField(default=False)

	def __unicode__(self):
		return self.name

	def get_vids_url(self):
		return self.url + '/videos/all'

	def update_vids(self):
		url = self.get_vids_url()

		b = webdriver.PhantomJS()
		b.get(url)
		content = b.page_source

		b.service.process.send_signal(signal.SIGTERM)
		b.quit()

		day = 0
		format = '%b %-d, %Y'

		while(True):
			two_month_ago = datetime.date.today() + relativedelta(months=-2, days=day)
			date_str = two_month_ago.strftime(format)

			ind = content.find(date_str)
			if ind:
				content = content[:ind]
				break
			else:
				day += 1

		soup = BeautifulSoup(content, 'html.parser')
		tmp = soup.find_all('div', class_='tower--bleed')

		if tmp:
			source_str = str(tmp[0])
			loots = re.findall(r'/videos/[0-9]{9}', source_str)

			if loots:
				ids = [l.replace('/videos/', '') for l in loots]

				# clean the duplicates
				ids = list(set(ids))

				# update and create the instances
				# also check to avoid duplicates

				existing_videos = self.video_set.all()
				existing_ids = [v.vid for v in existing_videos]

				for vid in ids:
					name = self.name + ' | ' + vid + '.mp4'

					# do the checkin
					if vid not in existing_ids:
						Video.objects.create(
							name = name,
							vid = vid,
							player = self,
						)

				return ids

			else:
				return False
		else:
			return False



class Hero(models.Model):
	name = models.CharField(max_length=120)

	def __unicode__(self):
		return self.name


class Ytvideo(models.Model):
	name = models.CharField(max_length=120)
	description = models.TextField(blank=True, null=True)
	tags = models.TextField(blank=True, null=True)
	hero = models.CharField(max_length=120, blank=True, null=True)
	is_trimmed = models.BooleanField(default=False)
	is_uploaded = models.BooleanField(default=False)
	is_analyzed = models.BooleanField(default=False)
	player = models.ForeignKey(Player, blank=True, null=True)
	trimmed_path = models.CharField(max_length=120, blank=True, null=True)
	vid_path = models.CharField(max_length=120)
	vid_link = models.CharField(max_length=100, blank=True, null=True)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return str(self.pk) + ' -- ' + self.name


	def get_desc(self):
		# create desc
		twitter = ''
		if self.player.twitter:
			twitter = '\ntwitter: ' + self.player.twitter

		print self.name
		print self.player.name.upper()
		print self.player.url
		print twitter

		m = 'Overwatch Season 3 Daily Dose\nSubscribe for daily dose: https://www.youtube.com/channel/UCaZrokkXp1jnG1ObCcTc6hA?sub_confirmation=1\n\n' + self.name + '\n\n' + 'Overwatch Pro gameplays & highlights. This video aims to help players learn from pro gamers.\n\n' + 'Support ' + self.player.name.upper() + ' here:\n\ntwitch: ' + self.player.url + twitter + '\n\nTwitch videos copyright belongs to the streamers.  If you want one of the videos removed, contact me at my email address below.\n\nSubscribe to receive notifications of future uploads :p'

		return m

	def get_tag(self):
		tags = 'Overwatch,' + self.player.name + ',' + self.hero + ',' + self.player.name + ' ' + self.hero + ',best ' + self.hero + ',pro ' + self.hero
		return tags


	def num_of_cues(self):
		return len(self.vidcue_set.all())


	def delete_vid(self):
		# delete links and vids
		subprocess.call(['sh', 'video/scripts/delete_vid.sh', self.vid_link, self.vid_path])

		self.delete()


	def generate_screenshots(self):

		vid_link = str('ytow' + self.vid_link)
		template_path = str(TEMPLATE_PATH)

		template = Image.open(template_path)
		template_data = np.asarray(template)

		vid = skvideo.io.vreader(vid_link)


		count = 0
		for frame in vid:
			count += 1

			if count % 30 == 0:
				res = cv2.matchTemplate(frame, template_data, cv2.TM_CCOEFF_NORMED)

				print str(count) + ' --- ' + str(res) + ' --- ' + self.name

				if res > 0.3:
					print 'HIT!'

					length = count / 60
					mins = length / 60
					secs = length % 60

					out_folder = str(self.pk) + '/'
					out_time = str(mins).zfill(2) + ':' + str(secs).zfill(2)
					out_name = out_time + '.jpg'
					im = Image.fromarray(frame)

					out_folder_path = str('ytow/static/screenshots/') + out_folder
					if not os.path.exists(out_folder_path):
						os.makedirs(out_folder_path)

					# also need to create screenshot instance
					save_out_name = str('ytow/static/screenshots/') + out_folder + out_name
					db_out_name = str('/static/screenshots/') + out_folder + out_name

					# create database instance
					Screenshot.objects.create(
						video=self,
						path=db_out_name,
						name=out_time,
					)

					# save the screenshot
					im.save(save_out_name)


		print 'Done'



	def trim(self):

		# get all the cues and trim the vid
		cues = self.vidcue_set.all()
		if cues:
			for i, cue in enumerate(cues):

				start = cue.start
				end = cue.end

				# calculate duration for ffmpeg to work
				start_m = int(start.split(':')[1])
				end_m = int(end.split(':')[1])
				start_s = int(start.split(':')[2])
				end_s = int(end.split(':')[2])

				print start_m, end_m, start_s, end_s
				diff = end_m * 60 + end_s - start_m * 60 - start_s

				print diff
				m = str(diff/60)
				s = str(diff%60)
				m = m.zfill(2)
				s = s.zfill(2)

				print m, s

				duration = '00:' + m + ':' + s

				print duration


				vid_name = self.name
				out_name = vid_name.split('.')[0] + str(cue.pk) + str(i) + '.mkv'

				try:
					subprocess.call(['sh', 'video/scripts/trim.sh', vid_name, start, duration, IN_FOLDER, OUT_FOLDER, out_name])
				except Exception, e:
					raise e
				else:

					# update the datebase
					self.is_trimmed = True

					trimmed_path = '/hdd/things/trimmed/' + out_name
					self.trimmed_path = trimmed_path

					self.save()





					return True

		# no cues for this vid
		return False

	def upload(self):
		vid_name = self.name
		title = vid_name
		tags = self.tags
		desc = self.get_desc()

		try:
			subprocess.call(['sh', 'video/scripts/upload.sh', title, desc, tags, self.trimmed_path])
		except Exception, e:
			raise e


	def open_vlc(self):
		name = 'ytow/' + self.vid_link
		try:
			subprocess.call(['sh', 'video/scripts/open.sh', name])
		except Exception, e:
			raise e


	def load_hero_avatars(self):
		hero_avatars = os.listdir(HERO_AVATAR_PATH)
		hs = []
		for h in hero_avatars:
			path = os.path.join(HERO_AVATAR_PATH, h)
			im = Image.open(path)

			hs.append((h.replace('.jpg', ''), im))

		return hs


	# get the hero of the video given a clip of gameplay, didn't consider 2 heros or more.
	def compute_hero(self, start='', end=''):
		# different filter needed from start to end

		if not start:
			print 'No cues given.. pass'
			pass

		# 00:11:22 -> 11:22

		start_min = int(start[3:5])
		end_min = int(end[3:5])

		screenshots = self.screenshot_set.all()

		# filter screenshots
		names = [s.name for s in screenshots]
		mins = [int(s.split(':')[0]) for s in names]

		start_ind = bisect.bisect(mins, start_min)
		end_ind = bisect.bisect(mins, end_min)

		# print len(screenshots)
		# print start_ind
		# print end_ind

		screenshots = screenshots[start_ind:end_ind+1]

		ims = []

		for s in screenshots:
			path = 'ytow/' + s.path
			im = Image.open(path)
			ims.append(im)


		# analyze hero
		hero_count = defaultdict(int)
		hs = self.load_hero_avatars()

		for im in ims:
			hero_avatar = im.crop((430, 557, 533, 633))
			hero_avatar_data = np.asarray(hero_avatar)

			# prob
			hero_prob = -1
			hero_name = ''

			for h in hs:
				h_name = h[0]
				h_data = np.asarray(h[1])
				res = cv2.matchTemplate(hero_avatar_data, h_data, cv2.TM_CCOEFF_NORMED)

				if res > hero_prob:
					hero_prob = res
					hero_name = h_name


			# update the count
			hero_count[hero_name] += 1


		hero = max(hero_count, key=hero_count.get)
		self.hero = hero
		super(Ytvideo, self).save()



class Vidcue(models.Model):
	video = models.ForeignKey(Ytvideo)
	start = models.CharField(max_length=10)
	end = models.CharField(max_length=10)

	def __unicode__(self):
		return self.video.name


class Screenshot(models.Model):
	video = models.ForeignKey(Ytvideo)
	path = models.CharField(max_length=120)
	name = models.CharField(max_length=100, default='')


class Video(models.Model):
	name = models.CharField(max_length=50)
	vid = models.CharField(max_length=9)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
	player = models.ForeignKey(Player)
	is_downloaded = models.BooleanField(default=False)
	is_processed = models.BooleanField(default=False)
	is_splitted = models.BooleanField(default=False)
	vid_path = models.CharField(max_length=120, blank=True, null=True)
	vid_link = models.CharField(max_length=100, blank=True, null=True)

	# textfield to store json text of all the cues in a video
	vid_cues = models.TextField(blank=True, null=True)

	def __unicode__(self):
		return str(self.pk) + ' | ' + self.name


	def vid_cue_list(self):
		return json.loads(self.vid_cues)


	def save_vid_cues(self, vid_cue_list):
		formatted_vid_cue = json.dumps(vid_cue_list)
		self.vid_cues = formatted_vid_cue
		try:
			self.save()
		except:
			raise
		else:
			return True


	def get_vid_url(self):
		return self.player.url + '/v/' + self.vid


	def delete_vid(self):
		subprocess.call(['sh', 'video/scripts/delete_vid.sh', self.vid_link, self.vid_path])

		self.delete()

	# open vid
	def open_vid(self):
		name = 'ytow/' + self.vid_link
		try:
			subprocess.call(['sh', 'video/scripts/open.sh', name])
		except Exception, e:
			raise e


	# download vids to specific places
	def download_vid(self):
		vid_path = CAPTURE_FOLDER2 + '/' + self.name
		link_path = '/static/links2/' + self.name

		# update the flags first, if r failed, restore the flags
		self.vid_path = vid_path
		self.vid_link = link_path
		self.is_downloaded = True
		self.save()

		# download the video
		token = 'pket84tnqh29si9tpuxdmi6848s81u'
		download_link = self.get_vid_url()

		r1 = subprocess.call(['sh', 'video/scripts/download.sh', token, vid_path, download_link])

		r = subprocess.call(['sh', 'video/scripts/create_link2.sh', vid_path, link_path])
		return True

		# if not r:
		# 	# update vid_path and vid_link
		# 	self.vid_path = ''
		# 	self.vid_link = ''
		# 	self.is_downloaded = False
		# 	self.save()
		# 	print 'Problem generating vid paths and links!'

	# do template matching to generate screenshots
	def generate_sc(self):

		# atomic
		self.is_processed = True
		self.save()


		print 'Working on ' + str(self.pk) + ' ' + self.name + '...'


		# add is_k
		is_k = self.player.is_k
		if is_k:
			print 'It is in Korean'
		else:
			print 'It is in English'


		vid_link = str('ytow' + self.vid_link)

		template_data = np.asarray(Image.open(TEMPLATE_PATH2).resize((640, 360)).convert('L'))
		template_data_1080 = np.asarray(Image.open(TEMPLATE_PATH).resize((640, 360)).convert('L'))

		# either 1080P or 720P
		probe = skvideo.io.ffprobe(vid_link)
		vid_width = int(probe['video']['@width'])
		vid_height = probe['video']['@height']

		print 'Video is ' + vid_height + 'P!'

		if vid_width == 1920:
			template_data = template_data_1080

		vid = skvideo.io.vreader(vid_link)

		count = 0
		for frame in vid:
			count += 1

			alpha = 90

			if count % alpha == 0:

				# resize frame to 640, 360 to make it much quicker
				resized_frame = Image.fromarray(frame).convert('L').resize((640, 360))



				res = cv2.matchTemplate(np.asarray(resized_frame), template_data, cv2.TM_CCOEFF_NORMED)


				print str(self.pk) + ' ' + str(count) + ' --- ' + str(res) + ' --- ' + self.name

				# brightness = ImageStat.Stat(resized_frame)
				# print 'Mean ' + str(brightness.mean[0])

				if res > 0.35:
					print '[HIT]'

					length = count / 60

					hours = length / 3600
					mins = (length % 3600) / 60
					secs = length  % 3600 % 60

					out_time = str(hours).zfill(2) + ':' + str(mins).zfill(2) + ':' + str(secs).zfill(2)


					out_folder = str(self.pk) + '/'
					out_name = out_time + '.jpg'
					im = Image.fromarray(frame)

					im = im.resize((1280, 720))

					out_folder_path = str('ytow/static/screenshots2/') + out_folder

					if not os.path.exists(out_folder_path):
						os.makedirs(out_folder_path)

					save_out_name = str('ytow/static/screenshots2/') + out_folder + out_name

					db_out_name = str('/static/screenshots2/') + out_folder + out_name

					# do the elim and death extraction
					to_analyze_frame = Image.fromarray(frame)
					try:
						elim_death_tuple = helpers.get_stats2(to_analyze_frame, is_k)
					except:
						# raise
						print 'Skip frame..'
						continue


					Videosc.objects.create(
						video = self,
						path = db_out_name,
						name = out_time,
						elim = elim_death_tuple[0],
						death = elim_death_tuple[1],
					)

					print save_out_name
					im.save(save_out_name)


		print 'Correcting...'
		try:
			self.correct_video_stat()
			self.split_video()
		except:
			print 'No Screenshots Generated'
			pass



	# correct death elim base on the context
	# do this after video is being screenshotted
	def correct_video_stat(self):
		vid_scs = self.videosc_set.all()
		# vid_ids = [v.pk for v in vid_scs]

		for i, vid_sc in enumerate(vid_scs):
			if i == 0 or i == len(vid_scs) - 1:
				continue


			prev_sc = vid_scs[i-1]
			next_sc = vid_scs[i+1]

			self.correct_single_sc(vid_sc, prev_sc, next_sc)

		for vid_sc in vid_scs:
			print vid_sc.video.name, vid_sc.elim, vid_sc.death



	def correct_single_sc(self, curr_sc, prev_sc, next_sc):
		'''
		see if elim,death makes sense in a sc based on prev and next scs
		'''
		curr_elim = curr_sc.elim
		curr_death = curr_sc.death
		next_elim = next_sc.elim
		next_death = next_sc.death
		prev_elim = prev_sc.elim
		prev_death = prev_sc.death

		# Case (1,2) (30,2) (1,2)
		# prev, next same, but not the curr, set the curr to prev
		if prev_elim == next_elim or prev_death == next_death:
			curr_sc.elim = prev_elim
			curr_sc.death = prev_death

		# Case prev, curr (4 19) (4 10) (4 10)
		if prev_elim == curr_elim and prev_death > curr_death and prev_death > next_death:
			prev_sc.death = curr_death
			prev_sc.save()

		# Case (19 4) (10 4) (10 4)
		if prev_death == curr_death and prev_elim > curr_elim and prev_elim > next_elim:
			prev_sc.elim = curr_elim
			prev_sc.save()

		# Case (6,0) (9,0) (8,1)
		# set curr to prev
		if curr_elim > prev_elim and curr_elim > next_elim:
			if curr_death < next_death:
				curr_sc.elim = prev_elim
				curr_sc.death = prev_death

		# Case (0,1) (0,16) (1,3)
		if curr_death > prev_death and curr_death > next_death:
			if curr_elim < next_elim:
				curr_sc.elim = prev_elim
				curr_sc.death = prev_death

		# Case (3,0) (0,0) (5,1)
		if curr_elim < prev_elim and prev_elim < next_elim:
			curr_sc.elim = prev_elim

		# Case (3,1) (3,0) (3,2)
		if curr_death < prev_death and prev_death < next_death:
			curr_sc.death = prev_death

		# suddle different is very big
		if curr_elim - prev_elim > 20:
			curr_sc.elim = prev_elim

		if curr_death - prev_death > 20:
			curr_sc.death = prev_sc.death

		curr_sc.save()



	# split video
	def split_video(self):
		screenshots = self.videosc_set.all()

		first_sc = screenshots[0]
		start = first_sc.name

		for i, screenshot in enumerate(screenshots):

			curr_sc = screenshot
			curr_sc_elim = curr_sc.elim
			curr_sc_death = curr_sc.death

			# don't forget to add the last gameplay
			if i == len(screenshots) - 1:
				end = curr_sc.name

				v = Videocue.objects.create(
					video = self,
					end_sc = curr_sc,
					is_updated = False,
					elim = curr_sc_elim,
					death = curr_sc_death,
				)

				v.analyze()

				v.save_cue(start, end)

				break


			next_sc = screenshots[i+1]
			next_sc_elim = next_sc.elim
			next_sc_death = next_sc.death

			print screenshot.__unicode__(), curr_sc_elim, curr_sc_death

			# meaning a new match has started
			if next_sc_elim < curr_sc_elim:

				# store start and end cue, and update start
				end = curr_sc.name

				v = Videocue.objects.create(
					video = self,
					end_sc = curr_sc,
					is_updated = False,
					elim = curr_sc_elim,
					death = curr_sc_death,
				)

				v.analyze()

				v.save_cue(start, end)

				start = end


		self.is_splitted = True
		self.save()


	def mass_analyze(self):
		vidcues = self.videocue_set.all()
		for vidcue in vidcues:
			try:
				vidcue.analyze()
			except:
				pass



class Videosc(models.Model):
	video = models.ForeignKey(Video)
	path = models.CharField(max_length=120)
	name = models.CharField(max_length=100, default='')
	elim = models.SmallIntegerField(blank=True, null=True)
	death = models.SmallIntegerField(blank=True, null=True)


	def __unicode__(self):
		return str(self.video.pk) + self.name

	def get_stats(self):
		im = Image.open('ytow' + self.path)
		# resized_img = im.resize((1280, 720))

		elim_death_tuple = helpers.get_stats2(im)

		return elim_death_tuple

	def get_hour(self):
		return int(self.name.split(':')[0])

	def get_min(self):
		return int(self.name.split(':')[1])

	def get_sec(self):
		return int(self.name.split(':')[2])

	def get_old_min(self):
		return int(self.name.split(':')[0])

	def get_old_sec(self):
		return int(self.name.split(':')[1])


class Videocue(models.Model):
	video = models.ForeignKey(Video)
	start = models.CharField(max_length=20, blank=True, null=True)
	end = models.CharField(max_length=20, blank=True, null=True)
	hero = models.CharField(max_length=120, blank=True, null=True)
	elim = models.SmallIntegerField(blank=True, null=True)
	death = models.SmallIntegerField(blank=True, null=True)
	elim_death_ratio = models.FloatField(blank=True, null=True)
	is_deliverable = models.BooleanField(default=False)
	end_sc = models.ForeignKey(Videosc)
	title = models.CharField(max_length=200, blank=True, null=True)
	desc = models.TextField(blank=True, null=True)
	is_updated = models.BooleanField(default=False)
	is_trimmed = models.BooleanField(default=False)
	is_uploaded = models.BooleanField(default=False)
	trimmed_path = models.CharField(max_length=200, blank=True, null=True)


	# cue_str should be of format: hh:mm:ss
	def save_cue(self, start_cue_str, end_cue_str):

		# preprocess cue_str to include hours because the stupid mistake
		# start_mins = int(start_cue_str.split(':')[0])
		# start_secs = int(start_cue_str.split(':')[1])
		# hours = start_mins / 60
		# mins = start_mins % 60
		# start_cue_str = str(hours).zfill(2) + ':' + str(mins).zfill(2) + ':' + str(start_secs).zfill(2)
		#
		# end_mins = int(end_cue_str.split(':')[0])
		# end_secs = int(end_cue_str.split(':')[1])
		# hours = end_mins / 60
		# mins = end_mins % 60
		# end_cue_str = str(hours).zfill(2) + ':' + str(mins).zfill(2) + ':' + str(end_secs).zfill(2)

		start_cue_str = start_cue_str.zfill(2)
		end_cue_str = end_cue_str.zfill(2)


		self.start = start_cue_str
		self.end = end_cue_str
		self.save()

	# use end screenshot as the metric, rating algorithm goes here
	def analyze(self):
		# elims = self.end_sc.get_stats()[0]
		# deaths = self.end_sc.get_stats()[1]
		#
		# self.elim = elims
		# self.death = deaths

		# print self.elim, self.death

		# algorithm
		# add map relevant things later
		# add hero relevant things later
		if self.death == 0:
			self.elim_death_ratio = 100
		else:
			self.elim_death_ratio = float(self.elim)/self.death

		if self.elim >= 15 and self.death <= 6 and self.elim_death_ratio >= 8:
			self.is_deliverable = True

		self.save()


	def trim(self):

		start_hour = int(self.start.split(':')[0])
		start_min = int(self.start.split(':')[1])
		start_sec = int(self.start.split(':')[2])

		end_hour = int(self.end.split(':')[0])
		end_min = int(self.end.split(':')[1])
		end_sec = int(self.end.split(':')[2])

		diff = end_hour * 3600 + end_min * 60 + end_sec - start_hour * 3600 - start_min * 60 - start_sec

		hours = str(diff/3600).zfill(2)
		mins = str((diff%3600)/60).zfill(2)
		secs = str(diff%3600%60).zfill(2)

		duration = hours + ':' + mins + ':' + secs
		vid_name = self.video.name
		out_name = str(self.pk) + ' | ' + self.start + ' | ' + vid_name

		print self.start, duration, vid_name, out_name
		try:
			subprocess.call(['sh', 'video/scripts/trim2.sh', vid_name, self.start, duration, CAPTURE_FOLDER2, TRIMMED_FOLDER2, out_name])
		except Exception, e:
			raise
		else:
			self.is_trimmed = True
			self.trimmed_path = os.path.join(TRIMMED_FOLDER2, out_name)

			self.save()
			return True
		return False


	def get_tag(self):
		tags = 'Overwatch,' + self.video.player.name + ',' + self.hero + ',' + self.video.player.name + ' ' + self.hero + ',best ' + self.hero + ',pro ' + self.hero
		return tags


	def upload(self):
		tags = self.get_tag()

		self.is_upload = True
		self.save()

		# retrieve a thumbnail image in random order
		hero = Hero.objects.get(name = self.hero)
		images = hero.vidimage_set.all()
		image_paths = [i.path for i in images]

		if image_paths:
			ind = random.randint(0, len(image_paths) - 1)
			image_path = image_paths[ind]
		else:
			image_path = ''

		try:
			subprocess.call(['sh', 'video/scripts/upload.sh', self.title, self.desc, tags, self.trimmed_path, image_path])
		except Exception, e:
			raise e


	def get_desc(self):
		# create desc
		twitter = ''
		if self.video.player.twitter:
			twitter = '\ntwitter: ' + self.video.player.twitter


		m = 'Overwatch Season 3 Daily Dose\nSubscribe for daily dose: https://www.youtube.com/channel/UCaZrokkXp1jnG1ObCcTc6hA?sub_confirmation=1\n\n' + self.title + '\n\n' + 'Overwatch Pro gameplays & highlights. This video aims to help players learn from pro gamers.\n\n' + 'Support ' + self.video.player.name.upper() + ' here:\n\ntwitch: ' + self.video.player.url + twitter + '\n\nTwitch videos copyright belongs to the streamers.  If you want one of the videos removed, contact me at my email address below.\n\nSubscribe to receive notifications of future uploads :p'

		return m

class VidImage(models.Model):
	path = models.CharField(max_length=50)
	hero = models.ForeignKey(Hero)

	def __unicode__(self):
		return str(self.pk) + ' ' + self.path + self.hero.name
