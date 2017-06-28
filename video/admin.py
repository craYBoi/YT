from django.contrib import admin

from .models import Ytvideo, Player, Vidcue, Hero, Screenshot, Video, Videosc, Videocue, VidImage

class VideoAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'is_trimmed', 'is_uploaded', 'is_analyzed', 'hero', 'player', 'tags', 'trimmed_path', 'vid_path', 'vid_link', 'timestamp']

class PlayerAdmin(admin.ModelAdmin):
	list_display = ['id', 'name', 'url', 'twitter', 'is_k', 'active']

class VidcueAdmin(admin.ModelAdmin):
	list_display = ['id', 'video', 'start', 'end']

class HeroAdmin(admin.ModelAdmin):
	list_display = ['id', 'name']

class ScreenshotAdmin(admin.ModelAdmin):
	list_display = ['id', 'video', 'name', 'path']

class Video2Admin(admin.ModelAdmin):
	list_display = ['id', 'name', 'vid', 'player', 'is_downloaded', 'is_processed', 'vid_path', 'vid_link', 'vid_cues', 'timestamp']

class VideoscAdmin(admin.ModelAdmin):
	list_display = ['id', 'video', 'name', 'elim', 'death', 'path']

class VideocueAdmin(admin.ModelAdmin):
	list_display = ['id', 'video', 'start', 'end', 'hero', 'elim', 'death', 'elim_death_ratio', 'title', 'desc', 'is_deliverable', 'is_updated', 'is_trimmed', 'is_uploaded', 'trimmed_path']

class VideoImageAdmin(admin.ModelAdmin):
	list_display = ['id', 'path', 'hero']

admin.site.register(Ytvideo, VideoAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Vidcue, VidcueAdmin)
admin.site.register(Hero, HeroAdmin)
admin.site.register(Screenshot, ScreenshotAdmin)
admin.site.register(Video, Video2Admin)
admin.site.register(Videosc, VideoscAdmin)
admin.site.register(Videocue, VideocueAdmin)
admin.site.register(VidImage, VideoImageAdmin)
