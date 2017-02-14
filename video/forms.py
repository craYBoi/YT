from django.forms import ModelForm
from .models import Ytvideo

class VideoForm(ModelForm):
	class Meta:
		model = Ytvideo
		fields = ['player', 'hero', 'name', 'description', 'tags']