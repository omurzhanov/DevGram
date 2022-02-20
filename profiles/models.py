from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.shortcuts import reverse

from .utils import get_random_code
# Create your models here.
class ProfileManager(models.Manager):
    def get_all_profiles_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender)
        profile = Profile.objects.get(user=sender)
        qs = Relationship.objects.filter(Q(sender=profile) | Q(receiver=profile))

        accepted = []
        for rel in qs:
            if rel.status == 'accepted':
                accepted.append(rel.receiver)
                accepted.append(rel.sender)

        available = [profile for profile in profiles if profile not in accepted]

        return available

    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles
    def get_all_friends(self, me):
        profile = Profile.objects.get(user=me)
        list_of_ids = me.friends.all().values_list('id', flat=True)
        qs = Profile.objects.filter(id__in=[list_of_ids])
        return qs
        

class Profile(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="no bio", max_length=300)
    email = models.EmailField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    avatar = models.FileField(default='avatar.jpg', upload_to='avatars/')

    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    slug = models.SlugField(unique=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ProfileManager()
    def get_absolute_url(self):
        return reverse('profiles:profile-detail-view', kwargs={'slug': self.slug})

    def get_friends(self):
        return self.friends.all()

    def get_image_url(self):
        return self.image.url

    def get_friends_no(self):
        return self.friends.all().count()

    def get_posts_no(self):
        return self.posts.all().count()

    def get_friends_no(self):
        return self.friends.all().count()

    def get_all_authors_posts(self):
        return self.posts.all()

    def get_likes_given_no(self):
        likes = self.like_set.all()
        total_liked = 0
        for item in likes:
            if item.value == 'Like':
                total_liked += 1
        return total_liked

    def get_likes_received_no(self):
        posts = self.posts.all()
        total_liked = 0
        for item in posts:
            total_liked += item.liked.all().count()
        return total_liked

    def __str__(self):
        return f'{self.user.username} -- {self.created.strftime("%d-%m-%Y")}'

    def save(self, *args, **kwargs):
        ex = False
        if self.first_name and self.last_name:
            to_slug = slugify(str(self.first_name) + " " + str(self.last_name))
            ex = Profile.objects.filter(slug=to_slug).exists()
            while ex:
                to_slug = slugify(to_slug + " " + str(get_random_code()))
                ex = Profile.objects.filter(slug=to_slug).exists()
        else:
            to_slug = str(self.user)
        self.slug = to_slug
        super().save(*args, **kwargs)
STATUS_CHOICES = (
    ('send', 'send'),
    ('accepted', 'accepted')
)
class RelationShipManager(models.Manager):
    def invitation_received(self, receiver):
        qs = Relationship.objects.filter(receiver=receiver, status='send')
        return qs



class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = RelationShipManager()
    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"