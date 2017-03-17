from django.contrib import admin

from .models import Ytvideo, Player, Vidcue, Hero, Screenshot

class VideoAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'is_trimmed', 'is_uploaded', 'is_analyzed', 'hero', 'player', 'tags', 'trimmed_path', 'vid_path', 'vid_link', 'timestamp']

class PlayerAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'url', 'twitter', 'active']

class VidcueAdmin(admin.ModelAdmin):
	list_display = ['id', 'video', 'start', 'end']

class HeroAdmin(admin.ModelAdmin):
	list_display = ['id', 'name']

class ScreenshotAdmin(admin.ModelAdmin):
	list_display = ['id', 'video', 'name', 'path']

admin.site.register(Ytvideo, VideoAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Vidcue, VidcueAdmin)
admin.site.register(Hero, HeroAdmin)
admin.site.register(Screenshot, ScreenshotAdmin)
