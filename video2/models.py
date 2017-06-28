# from __future__ import unicode_literals
#
# from django.db import models
#
# from video.models import Player
#
# # Create your models here.
# import subprocess
# import os
#
# IN_FOLDER = '/hdd/things/captures2'
# OUT_FOLDER = '/hdd/things/trimmed2'
#
# class Video(models.Model):
#     name = models.CharField(max_length=50)
#     vid = models.CharField(max_length=9)
#     timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
#     player = models.ForeignKey(Player, blank=True, null=True)
#     is_downloaded = models.BooleanField(default=False)
#
#     def get_vid_url(self):
#         return self.player.url + '/v/' + self.vid
