from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from django.views import generic
from django.http import Http404
from django.contrib import messages

from braces.views import SelectRelatedMixin

from . import models
from . import forms
from groups.models import Group

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
class PostList(LoginRequiredMixin, SelectRelatedMixin, generic.ListView):
    model = models.Post
    select_related = ('user', 'group')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(group__members=self.request.user)


        # try:
        #     self.posts_to_show = Group.objects.prefetch_related('posts').get(members=self.request.user)
        # except User.DoesNotExist:
        #     raise Http404
        # else:
        #     return self.posts_to_show.posts.all()


class UserPost(generic.ListView):
    model = models.Post
    template_name = 'posts/user_post_list.html'

    def get_queryset(self):
        try:
            self.post_user = User.objects.prefetch_related('posts').get(username__iexact=self.kwargs.get('username'))
        except User.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_user'] = self.post_user
        return context

class PostDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    select_related = ('user', 'group')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact=self.kwargs.get('username'))


def post_detail(request, username, pk):
    post = get_object_or_404(models.Post, pk=pk)
    new_comment = None

    if request.method == 'POST':
        if request.user.id == None:
            raise Http404
        else:
            comment_form = forms.CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.post = post
                new_comment.author = request.user
                new_comment.save()
                return redirect('posts:single', pk=post.pk, username=post.user.username)
    else:
        comment_form = forms.CommentForm()
    return render(request, 'posts/post_detail.html', {'post': post, 'form':comment_form})


class CreatePost(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    # fields = ('message', 'group')
    model = models.Post
    form_class = forms.PostForm

    def form_valid(self,form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CreatePost, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class DeletePost(LoginRequiredMixin, SelectRelatedMixin, generic.DeleteView):
    model = models.Post
    select_related = ('user', 'group')
    success_url = reverse_lazy('posts:all')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Post Deleted')
        return super().delete(*args, **kwargs)

class EditPost(LoginRequiredMixin, SelectRelatedMixin, generic.UpdateView):
    model = models.Post
    select_related = ('user', 'group')
    fields = ('message',)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404
        return super(EditPost, self).dispatch(request, *args, **kwargs)



class CreateComment(LoginRequiredMixin, generic.CreateView):
    model = models.Comment
    fields = ('text', )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        post_ln = get_object_or_404(models.Post, pk = self.kwargs.get('pk'))
        self.object.post = post_ln
        self.object.save()
        return super().form_valid(form)


class DeleteComment(LoginRequiredMixin, generic.DeleteView):
    model = models.Comment

    def get_success_url(self):
        post = self.object.post
        return reverse_lazy('posts:single', kwargs={'username': post.user.username, 'pk':post.pk})

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)
# END
