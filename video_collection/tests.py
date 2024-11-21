from django.test import TestCase
from django.urls import reverse
from .models import Video
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Exercise Videos')


class TestAddVideos(TestCase):

    def test_add_video(self):

        valid_video = {
            'name': 'bedtime yoga',
            'url': 'https://www.youtube.com/watch?v=6CueZ4zujMk',
            'notes': 'yoga for bedtime'
        }

        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)

        self.assertTemplateNotUsed('video_collection/video_list.html')
        # video list show
        self.assertContains(response, 'bedtime yoga')
        self.assertContains(response,'https://www.youtube.com/watch?v=6CueZ4zujMk' )
        self.assertContains(response, 'yoga for bedtime')

        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        video = Video.objects.first() 
        self.assertEqual('bedtime yoga', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=6CueZ4zujMk', video.url)
        self.assertEqual('yoga for bedtime', video.notes)
        self.assertEqual('6CueZ4zujMk', video.video_id)
    
    def test_add_video_invalid_url_not_added(self):

        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
        
        ]


        for invalid_url in invalid_video_urls:

            new_video = {
                'name': 'example',
                'url': invalid_url,
                'notes': 'example notes'
            }

            url = reverse('add_video')
            response = self.client.post(url, new_video)

         
            self.assertTemplateUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]

            self.assertIn('Invalid YouTube URL', message_texts)
            self.assertIn('Please check the data entered', message_texts)

            # no videos in the database 
            video_count = Video.objects.count()
            self.assertEqual(0, video_count)

class TestVideoList(TestCase):

    def test_all_videos_displayed_in_correct_order(self):

        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=143')
        v3 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=676')
        v4 = Video.objects.create(name='erw', notes='example', url='https://www.youtube.com/watch?v=125')

        expected_video_order = [v2, v1, v4, v3]

        url = reverse('video_list')
        response = self.client.get(url)

        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    def test_no_video_message(self):
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No videos')
        self.assertEqual(0, len( response.context['videos']))

    def test_video_number_message_single_video(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')   

class TestVideoModel(TestCase):
      
      def test_invalid_url_raises_validation_error(self):
          invalid_video_url = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
           
          ]

          for invalid_video_url in invalid_video_url:
              with self.assertRaises(ValidationError):
                  
                  Video.objects.create(name='example', url=invalid_video_url, notes='example note')

          self.assertEqual(0, Video.objects.count())
                
          
      def test_duplicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')

class VideoDetailTest(TestCase):

    def test_video_detail_nonexistent_returns_404(self):
        # Try to access a video with an ID that doesn't exist (e.g., 10000)
        url = reverse('video_detail', kwargs={'video_id': 10000})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)