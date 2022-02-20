from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404, reverse

from posts.models import Post
from .models import Profile, Relationship
from .forms import ProfileModelForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from posts.forms import CommentModelForm
# Create your views here.

@login_required
def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileModelForm(request.POST or None, request.FILES or None, instance=profile)
    posts = Post.objects.filter(author=profile)
    confirm = False
    c_form = CommentModelForm()

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            confirm = True
    if 'submit_c_form' in request.POST:
        c_form = CommentModelForm(request.POST)
        if c_form.is_valid():
            instance = c_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id=request.POST.get('post_id'))
            instance.save()
            c_form = CommentModelForm()
    context = {
        'profile': profile,
        'form': form,
        'confirm': confirm,
        'posts': posts,
        'c_form': c_form,
    }

    return render(request, 'profiles/myprofile.html', context)

@login_required
def invites_received_view(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invitation_received(profile)
    results = list(map(lambda x: x.sender, qs))
    is_empty = False

    if len(results) == 0:
        is_empty = True

    context = {
        'qs': results,
        'is_empty': is_empty,
    }

    return render(request, 'profiles/my_invites.html', context)
@login_required
def accept_invitation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()
    return redirect('profiles:my-invites-view')

@login_required
def reject_invitation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()

    return redirect('profiles:my-invites-view')


class ProfileDetailView(LoginRequiredMixin,DetailView, FormMixin):
    model = Profile
    template_name = 'profiles/detail.html'
    form_class = CommentModelForm

    def get_success_url(self):
        profile = self.get_object()
        return '{}'.format(reverse('profiles:profile-detail-view', kwargs={'slug': profile.slug}))
    
    def get_object(self, slug=None):
        slug = self.kwargs.get('slug')
        profile = Profile.objects.get(slug=slug)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)
        friends = Profile.objects.get_all_friends(self.get_object().user)
        context['rel_receiver'] = rel_receiver
        context['rel_sender'] = rel_sender
        context['posts'] = self.get_object().get_all_authors_posts()
        context['len_posts'] = True if len(self.get_object().get_all_authors_posts()) > 0 else False
        context['c_form'] = CommentModelForm()
        context['profiles'] = friends
        context['is_empty'] = False
        if len(friends) == 0:
            context['is_empty'] = True
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = Profile.objects.get(id=self.request.user.id)
        instance.post = Post.objects.get(id=self.request.POST.get('post_id'))
        instance.save()
        return super().form_valid(form)

class FriendsListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        qs = Profile.objects.get_all_friends(self.request.user)
        return qs

class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    context_object_name = 'profiles'

    def get_template_names(self):
        template_name = super(ProfileListView, self).get_template_names()
        search = self.request.GET.get('q')
        if search:
            template_name = 'search.html'
        return template_name

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs

    def get_context_data(self, word=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get('q')
        if word:
            search = word
        if search:
            context['profiles'] = Profile.objects.all().filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(user__username__icontains=search))
            return context
        else:
            profile = Profile.objects.get(user=self.request.user)
            rel_r = Relationship.objects.filter(sender=profile)
            rel_s = Relationship.objects.filter(receiver=profile)
            rel_receiver = []
            rel_sender = []
            for item in rel_r:
                rel_receiver.append(item.receiver.user)
            for item in rel_s:
                rel_sender.append(item.sender.user)
            context['rel_receiver'] = rel_receiver
            context['rel_sender'] = rel_sender
            context['is_empty'] = False
            if len(self.get_queryset()) == 0:
                context['is_empty'] = True

            return context

@login_required
def send_invitation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')

@login_required
def remove_from_friends(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get((Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender)))
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')

