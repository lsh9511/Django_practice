from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from homework.forms import CommentForm
from homework.models import Todo, Comment


class TodoListView(ListView):
    model = Todo
    template_name = 'todo_list.html'
    paginate_by = 10
    ordering = '-created_at'

    def get_queryset(self):
        queryset = super().get_queryset()

        q= self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q)
            )
        return queryset
class TodoDetailView(LoginRequiredMixin,DetailView):
    model = Todo
    template_name = 'todo_info.html'

    def get_object(self):
        object = super().get_object()
        if not self.request.user.is_superuser and not self.request.user :
            raise Http404("접근 권한이 없습니다.")
        return object

    def get_context_data(self, **kwargs):
        comments = self.object.comments.order_by("-created_at")
        paginator = Paginator(comments, 5)
        context = {
            "todo": self.object,
            "comment_form": CommentForm(),
            "page_obj": paginator.get_page(self.request.GET.get("page")),
        }
        return context


class TodoCreateView(LoginRequiredMixin,CreateView):
    model = Todo
    template_name = 'todo_create.html'
    fields = ('title','description','start_date','end_date')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('todo_info', kwargs={'pk':self.object.pk})

class TodoUpdateView(LoginRequiredMixin,UpdateView):
    model = Todo
    template_name = 'todo_update.html'
    fields = ('title','description','start_date','end_date', 'is_completed')

    def get_object(self,queryset=None):
        self.object = super().get_object(queryset)

        if self.object.user != self.request.user and not self.request.user.is_superuser:
            raise Http404("해당 To do를 수정할 권한이 없습니다.")
        return self.object

    def get_success_url(self):
        return reverse_lazy('todo_info', kwargs={'pk':self.object.pk})

class TodoDeleteView(LoginRequiredMixin,DeleteView):
    model = Todo

    def get_object(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('todo_list')

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['message']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.todo = Todo.objects.get(pk=self.kwargs['pk'])
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('todo_info', kwargs={'pk': self.object.todo.pk})

class CommentUpdateView(LoginRequiredMixin,UpdateView):
    model = Comment
    fields = ['message']

    def get_object(self,queryset=None):
        obj = super().get_object(queryset) # 조건식이 붙을때 항상 넣어줘야함 () 안에 queryset

        if obj.user != self.request.user and not self.request.user.is_superuser:
            raise Http404("해당 댓글을 수정할 권한이 없습니다.")
        return obj

    def get_success_url(self):
        return reverse_lazy('todo_info', kwargs={'pk':self.object.pk})

class CommentDeleteView(LoginRequiredMixin,DeleteView):
    model = Comment

    def get_object(self,queryset=None):
        obj = super().get_object(queryset)

        if obj.user != self.request.user and not self.request.user.is_superuser:
            raise Http404("해당 댓글을 삭제할 권한이 없습니다.")
        return obj
    def get_success_url(self):
        return reverse_lazy('todo_list')



