from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import signal
import sched
import requests
import datetime
import json
import time
import os
import subprocess
import csv

from .models import Ytvideo, Player

class Machine():
	def __init__(self, screen=1):
		self.s = sched.scheduler(time.time, time.sleep)
		# screen 1 is secondary ASUS, 2 is primary Acer
		self.screen = screen

	def get_html_content(self, url):
		b = webdriver.PhantomJS()
		b.get(url)
		content = b.page_source

		b.service.process.send_signal(signal.SIGTERM)
		b.quit()

		return content

	def channel_status(self, url):
		content = self.get_html_content(url)
		soup = BeautifulSoup(content, 'html.parser')
		tmp = soup.find_all('div', class_='balloon--tooltip')
		r_set = [k.string.replace('\n', '').strip(' ').lower() for k in tmp]

		return u'live now' in r_set

	def get_next_index(self, curr, max_c):
		next = curr+1
		if next == max_c:
			return 0
		return next

	def process_name(self, n):
		return n + str(datetime.datetime.now().strftime('-%m-%d-%y-%H:%M')) + '.mkv'

	# little function to parse time, and calculate duration
	def time_to_sec(self, input_t):
		pieces = input_t.split(':')
		h = int(pieces[0])
		m = int(pieces[1])
		s = int(pieces[2])
		return h*3600 + m*60 + s

	def sec_to_time(self, input_t):
		h = input_t / 3600
		input_t = input_t % 3600
		m = input_t / 60
		s = input_t % 60
		return str(h).zfill(2) + ':' + str(m).zfill(2) + ':' + str(s).zfill(2)


	def time_to_duration(self, start_time, end_time):
		diff = self.time_to_sec(end_time) - self.time_to_sec(start_time)
		duration = self.sec_to_time(diff)
		return duration


	def loop_check(self, urls, curr_c=0):
		# check channel_status
		print 'Starting the script...'

		# loop through all the accounts, if offline, jump to the next, jump back to the first when depleted
		max_c = len(urls)


		# MAJOR EDIT
		# url = urls[curr_c]
		# print 'Working on ' + str(url) + '...'

		player = urls[curr_c]


		print 'Working on ' + player.name + '...'
		url = player.url


		# in case Phantom JS crashes
		try:
			flag = self.channel_status(url)
		except:
			next_c = self.get_next_index(curr_c, max_c)

			player = urls[next_c]
			url = player.url
			self.s.enter(5, 1, self.loop_check, (urls, next_c,))

		# start the script
		if flag:
			# call webdriver with Chrome and record
			print 'The Channel is Live!!'

			# open the browser and make it fullscreen


			if self.screen == 1:

				b = webdriver.Chrome(os.path.join(os.path.dirname(__file__), 'chromedriver'))
				b.set_window_position(1920, 0)

			else:
				b = webdriver.Firefox()
				b.set_window_position(0, 0)
				b.set_window_size(960, 1080)


			delay = 10
			# b.implicitly_wait(15)

			# [DEBUG]
			print 'BEFORE GET'
			b.maximize_window()
			b.get(url)



			# b.refresh()

			# b.implicitly_wait(10)
			print 'FINDING ELEMENT'
			# make sure to change the quality to source

			if self.screen == 2:
				b.set_window_size(960, 1080)

			# TEMP
			# try:

			flag = True
			count = 0
			while flag:
				try:
			# do this twice to refresh
					try:
						WebDriverWait(b, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'js-control-playpause-button')))

						count += 1
						# escape if count exceed 10

						if count > 10:
							next_c = self.get_next_index(curr_c, max_c)
							player = urls[next_c]
							url = player.url
							b.close()
							b.quit()
							self.s.enter(5, 1, self.loop_check, (urls, next_c,))

						print 'Finding js control playpause button...'



					except TimeoutException, e:
						raise e
					else:
						time.sleep(5)
						b.find_element_by_class_name('js-control-playpause-button').send_keys(Keys.ENTER)
			 			b.find_element_by_class_name('js-control-playpause-button').send_keys(Keys.ENTER)

						# hit mature button
						try:
							b.find_element_by_class_name('js-player-mature-accept').send_keys(Keys.ENTER)
						except:
							pass

					try:
						WebDriverWait(b, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'player-button--settings')))
					except TimeoutException, e:
						raise e
					else:
						b.find_element_by_class_name('player-button--settings').send_keys(Keys.ENTER)


						el = b.find_element_by_class_name('player-menu__item-control')
						el.send_keys(Keys.ENTER)
						sel = Select(b.find_element_by_class_name('player-menu__item-control'))


					# for situations when other is hosting
						sel.select_by_visible_text('Source')

						# full screen
						b.find_element_by_class_name('player-button--fullscreen').send_keys(Keys.ENTER)

						# hit mature button
						try:
							b.find_element_by_class_name('js-player-mature-accept').send_keys(Keys.ENTER)
						except:
							pass
				except:
					try:
						b.refresh()
					except:
						next_c = self.get_next_index(curr_c, max_c)

						player = urls[next_c]
						url = player.url
						self.s.enter(5, 1, self.loop_check, (urls, next_c,))

					time.sleep(5)

					# pass
				else:
					flag = False

			# TEMP
			# except Exception, e:
			#
			# 	raise e
			#
			# 	# close and recall this method in 5 secs
			# 	next_c = self.get_next_index(curr_c, max_c)
			#
			# 	# MAJOR EDIT
			# 	# url = urls[next_c]
			# 	player = urls[next_c]
			# 	url = player.url
			#
			#
 		# 		print 'Other Host Hosting.. Try  ' + str(url) + ' in 5 secs'
			# 	self.s.enter(5, 1, self.loop_check, (urls, next_c,))

			# hit the player button for some certain situations when the video don't play automatically
			print 'hit play button now'
			try:
				b.find_element_by_class_name('player-button-play').send_keys(Keys.ENTER)
			except:
				pass

			# hit mature button
			try:
				b.find_element_by_class_name('js-player-mature-accept').send_keys(Keys.ENTER)
			except:
				pass


			# record the video
			captured_name = self.process_name(url.split('/')[-1])

			# first create the vid instance, since recording can be disrupted
			player = Player.objects.get(url=url)
			vid_path = '/hdd/things/captures/' + captured_name
			link_path = '/static/links/' + captured_name

			Ytvideo.objects.create(
				name = captured_name,
				player = player,
				vid_path = vid_path,
				vid_link = link_path,
			)

			# create the sym link to that video
			r = subprocess.call(['sh', 'video/scripts/create_link.sh', vid_path, link_path])



			if not r:
				print 'Problem generating the vid link'

			# TODO add timestamp on the record name, make it unique and easy to track

			# screen ASUS is 1
			if self.screen == 1:
				vid_input_mod = "+1920,0"
			else:
				vid_input_mod = ''

			# update the player recording flag
			player.recording = True
			player.save()

			# record
			subprocess.call(['sh', 'video/scripts/record.sh', captured_name, vid_input_mod])

			player.recording = False
			player.save()

			# 20 second buffer time at the end
			time.sleep(10)
			print '\nDone!\n'

			# now work on the next one
			next_c = self.get_next_index(curr_c, max_c)

			# MAJOR EDIT
			# url = urls[next_c]
			player = urls[next_c]
			url = player.url



			# close the driver
			b.close()
			b.quit()

			self.s.enter(5, 1, self.loop_check, (urls, next_c,))

		else:
			# close and recall this method in 5 secs
			next_c = self.get_next_index(curr_c, max_c)

			# MAJOR EDIT
			# url = urls[next_c]
			player = urls[next_c]
			url = player.url

 			print 'Offline.. Try again on ' + str(url) + ' in 5 secs'
			self.s.enter(5, 1, self.loop_check, (urls, next_c,))


	def run(self, screen):

		# get the urls

		# ASUS for active players

		players = Player.objects.filter(active=True).exclude(recording=True)
		# if screen == 1:
		# 	players = Player.objects.filter(active=True)
		# else:
		# 	players = Player.objects.filter(active=False)
		# urls = [p.url for p in players]

		# self.loop_check(urls)
		self.loop_check(players)
		self.s.run()
