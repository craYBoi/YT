from django.contrib import admin

from .models import Ytvideo, Player, Vidcue

class VideoAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'is_trimmed', 'is_uploaded', 'hero', 'player', 'tags', 'trimmed_path', 'vid_path', 'vid_link', 'timestamp']

class PlayerAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'url', 'twitter', 'active']

class VidcueAdmin(admin.ModelAdmin):
	list_display = ['id', 'video', 'start', 'end']

admin.site.register(Ytvideo, VideoAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Vidcue, VidcueAdmin)
