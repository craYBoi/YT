from __future__ import unicode_literals

from django.db import models

import subprocess
import skvideo.io
import numpy as np
import cv2
import os
from PIL import Image

from collections import defaultdict
import bisect

IN_FOLDER = '/hdd/things/captures'
OUT_FOLDER = '/hdd/things/trimmed'
TEMPLATE_PATH = 'ytow/static/template/template2.jpg'
HERO_AVATAR_PATH = 'ytow/static/template/heros'



class Player(models.Model):
	url = models.CharField(max_length=120)
	name = models.CharField(max_length=50)
	twitter = models.CharField(max_length=100, blank=True, null=True)
	active = models.BooleanField(default=True)
	recording = models.BooleanField(default=False)

	def __unicode__(self):
		return self.name


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

			if count % 60 == 0:
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

		# for simplicity, change flag first
		self.is_uploaded = True
		self.save()
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


	def analyze(self):
		pass


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
