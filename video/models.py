from __future__ import unicode_literals

from django.db import models

import subprocess

IN_FOLDER = '/hdd/things/captures'
OUT_FOLDER = '/hdd/things/trimmed'



class Player(models.Model):
	url = models.CharField(max_length=120)
	name = models.CharField(max_length=50)
	twitter = models.CharField(max_length=100, blank=True, null=True)
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return self.name

class Ytvideo(models.Model):
	name = models.CharField(max_length=120)
	description = models.TextField(blank=True, null=True)
	tags = models.TextField(blank=True, null=True)
	hero = models.CharField(max_length=120, blank=True, null=True)
	is_trimmed = models.BooleanField(default=False)
	is_uploaded = models.BooleanField(default=False)
	player = models.ForeignKey(Player, blank=True, null=True)
	trimmed_path = models.CharField(max_length=120, blank=True, null=True)
	vid_path = models.CharField(max_length=120)
	vid_link = models.CharField(max_length=100, blank=True, null=True)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.name


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

		

class Vidcue(models.Model):
	video = models.ForeignKey(Ytvideo)
	start = models.CharField(max_length=10)
	end = models.CharField(max_length=10)

	def __unicode__(self):
		return self.video.name
