from re import search
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from .models import Post, Like
from profiles.models import Profile
from .forms import PostModelForm, CommentModelForm
from django.views.generic import UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.urls import reverse, resolve
# Create your views here.
@login_required
def newest_posts(request):
    qs = Post.objects.all().order_by('-created')
    profile = Profile.objects.get(user=request.user)
    paginator = Paginator(qs, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    p_form = PostModelForm()
    c_form = CommentModelForm()
    post_added = False

    if 'submit_p_form' in request.POST:
        p_form = PostModelForm(request.POST, request.FILES)
        if p_form.is_valid():
            instance = p_form.save(commit=False)
            instance.author = profile
            instance.save()
            p_form = PostModelForm()
            post_added = True

    if 'submit_c_form' in request.POST:
        c_form = CommentModelForm(request.POST)
        if c_form.is_valid():
            instance = c_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id=request.POST.get('post_id'))
            instance.save()
            c_form = CommentModelForm()
    context = {
        'qs': qs,
        'profile': profile,
        'p_form': p_form,
        'c_form': c_form,
        'post_added': post_added,
        'posts': posts
    }
    return render(request, 'posts/main2.html', context)
@login_required
def post_comment_create_and_list_view(request):
    me = Profile.objects.get(user=request.user)
    list_of_ids = me.friends.all().values_list('id', flat=True)
    lst = [i for i in list_of_ids]
    lst.append(me.id)
    qs = Post.objects.all().filter(author__id__in=lst)
    profile = Profile.objects.get(user=request.user)
    paginator = Paginator(qs, 3)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    p_form = PostModelForm()
    c_form = CommentModelForm()
    post_added = False

    if 'submit_p_form' in request.POST:
        p_form = PostModelForm(request.POST, request.FILES)
        if p_form.is_valid():
            instance = p_form.save(commit=False)
            instance.author = profile
            instance.save()
            p_form = PostModelForm()
            post_added = True

    if 'submit_c_form' in request.POST:
        c_form = CommentModelForm(request.POST)
        if c_form.is_valid():
            instance = c_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id=request.POST.get('post_id'))
            instance.save()
            c_form = CommentModelForm()
    context = {
        'qs': qs,
        'profile': profile,
        'p_form': p_form,
        'c_form': c_form,
        'post_added': post_added,
        'posts': posts
    }
    return render(request, 'posts/main2.html', context)
@login_required
def favourites_list(request):
    user = request.user
    posts = user.favourite.all()
    return render(request, 'posts/favourites.html', {'posts': posts})
@login_required
def favourite_add(request, id):
    post = get_object_or_404(Post, id=id)

    if post.favourite.filter(id=request.user.id).exists():
        post.favourite.remove(request.user)
    else:
        post.favourite.add(request.user)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def like_unlike_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        profile = Profile.objects.get(user=user)

        if profile in post_obj.liked.all():
            post_obj.liked.remove(profile)
        else:
            post_obj.liked.add(profile)

        like, created = Like.objects.get_or_create(user=profile, post_id=post_id)

        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
        else:
            like.value='Like'
            post_obj.save()
            like.save()

    return redirect(request.META.get('HTTP_REFERER'))

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    template_name = 'posts/confirm_del.html'
    success_url = reverse_lazy('main-post-view')

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Post.objects.get(pk=pk)
        if not obj.author.user == self.request.user:
            messages.warning(self.request, 'You need to be the author of the post in order to delete')
        return obj

class PostUpdateView(LoginRequiredMixin,UpdateView):
    form_class = PostModelForm
    model = Post
    template_name = 'posts/update.html'
    success_url = reverse_lazy('main-post-view')

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        if form.instance.author == profile:
            return super().form_valid(form)
        else:
            form.add_error(None, 'You need to be the author of the post in order to delete')
            return super().form_valid(form)

def searchbar(request):
    if request.method=='GET':
        print('hello')
        search = request.GET.get('q')
        # profiles = Profile.objects.all().filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(user__username__icontains=search))
        profiles = Profile.objects.filter(user__username__icontains=search)    
        return render(request)