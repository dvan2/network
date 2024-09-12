from django.test import TestCase


from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Follow, Post

class ProfileTestCase(TestCase):
    def setUp(self):
        self.User = get_user_model()

        # Create users
        self.user1 = self.User.objects.create_user(username='user1', password="password")
        self.user2 = self.User.objects.create_user(username='user2', password="password")

        # Create some post by user2
        Post.objects.create(author=self.user2, content="Post 1")
        Post.objects.create(author=self.user2, content="Post 2")

        # User1 follows User2
        Follow.objects.create(followed_by=self.user1, being_followed=self.user2)
    
    def test_profile_page_renders(self):
        self.client.login(username="user1", password="password")
        response = self.client.get(reverse('profile', kwargs={'profile_id': self.user2.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'network/profile.html')
    
    def test_posts_displayed(self):
        self.client.login(username="user1", password="password")
        response = self.client.get(reverse('profile', kwargs={'profile_id': self.user2.pk}))

        posts = response.context['posts']
        self.assertEqual(posts[0].content, "Post 2")
        self.assertEqual(posts[1].content, "Post 1")
    
    def test_follow(self):
        self.client.login(username="user1", password="password")
        
        # Visit user2
        response = self.client.get(reverse('profile', kwargs={'profile_id': self.user2.pk}))

        self.assertEqual(response.context['follower_count'], 1)
        self.assertEqual(response.context['following_count'], 0)
        self.assertTrue(response.context['is_following'])

        # Visit self/User1 and check follower/following count
        response = self.client.get(reverse('profile', kwargs={'profile_id': self.user1.pk}))
        self.assertEqual(response.context['follower_count'], 0)
        self.assertEqual(response.context['following_count'], 1)

    def test_unfollow(self):
        self.client.login(username="user1", password="password")
        
        # Unfollow user2
        response = self.client.post(reverse('follow', kwargs={'profile_id': self.user2.pk}))

        self.assertFalse(Follow.objects.filter(followed_by=self.user1, being_followed=self.user2).exists())
        self.assertEqual(response.status_code, 302)

        # Visit user2
        response = self.client.get(reverse('profile', kwargs={'profile_id': self.user2.pk}))

        # Check follower/following count
        self.assertEqual(response.context['follower_count'], 0)
        self.assertEqual(response.context['following_count'], 0)
        self.assertFalse(response.context['is_following'])
    