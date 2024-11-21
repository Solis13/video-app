from urllib import parse 
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=40, unique=True)

    def save(self, *args, **kwargs):
        # checks for a valid YouTube URL in the form
        # https://www.youtube.com/watch?v=12345678
        # where 12345678 is the video ID
        url_components = parse.urlparse(self.url)

        if url_components.scheme != 'https':
            raise ValidationError(f'Not a YouTube URL {self.url}')

        if url_components.netloc != 'www.youtube.com':
            raise ValidationError(f'Not a YouTube URL {self.url}')
                
        if url_components.path != '/watch':
            raise ValidationError(f'Not a YouTube URL {self.url}')
            
        query_string = url_components.query # 'v=123432'
        if not query_string:
            raise ValidationError(f'Invalid YouTube URL {self.url}')
        parameters = parse.parse_qs(query_string, strict_parsing=True) #dictionary
        v_parameters_list = parameters.get('v')
        if not v_parameters_list:   # empty string, empty list... 
            raise ValidationError(f'Invalid YouTube URL parameters {self.url}')
        self.video_id = v_parameters_list[0]   # set the video ID for this Video object 

        super().save(*args, **kwargs)  # don't forget!

    def __str__(self):
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url}, Notes: {self.notes[:200]}'