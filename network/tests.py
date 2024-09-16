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
        self.assertTrue(Follow.objects.filter(followed_by=self.user1, being_followed=self.user2).exists())
        
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
    
class PostingTestCase(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username='testuser', password='pass')
    
    def test_create_post(self):
        self.client.login(username='testuser', password='pass')

        response = self.client.post(reverse('post'), {'post-input': 'Post 1'})

        self.assertRedirects(response, reverse('index'))
        post = Post.objects.get(content="Post 1")

        self.assertEqual(post.author.username, 'testuser')


class MultipleFollowing(TestCase):
    def setUp(self):
        self.User = get_user_model()

        # Create 3 users
        self.user1 = self.User.objects.create_user(username='user1', password='pass')
        self.user2 = self.User.objects.create_user(username='user2', password='pass')
        self.user3 = self.User.objects.create_user(username='user3', password='pass')

        self.post1 = Post.objects.create(author=self.user1, content="I'm User 1")
        Post.objects.create(author=self.user2, content="I'm User 2")
        Post.objects.create(author=self.user3, content="I'm User 3")

        # User1 follows User2
        Follow.objects.create(followed_by=self.user1, being_followed=self.user2)
        Follow.objects.create(followed_by=self.user1, being_followed=self.user3)
    
    def test_following_page(self):
        self.client.login(username='user1', password='pass')
        self.assertTrue(Follow.objects.filter(followed_by=self.user1, being_followed=self.user2).exists())
        self.assertTrue(Follow.objects.filter(followed_by=self.user1, being_followed=self.user3).exists())

        #Check following count for user1
        response = self.client.get(reverse('profile', kwargs={'profile_id': self.user1.pk}))
        self.assertEqual(response.context['follower_count'], 0)
        self.assertEqual(response.context['following_count'], 2)

        response = self.client.post(reverse('following'))
        posts = response.context['posts']

        self.assertTrue(any(post.content == "I'm User 2" for post in posts))
        self.assertTrue(any(post.content == "I'm User 3" for post in posts))
        self.assertFalse(any(post.content == "I'm User 1" for post in posts))
    
    def test_like_post(self):
        self.client.login(username='user2', password='pass')



