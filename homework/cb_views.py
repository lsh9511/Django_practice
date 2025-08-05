from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import signing
from django.core.paginator import Paginator
from django.core.signing import TimestampSigner, SignatureExpired
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView

from homework.forms import CommentForm, TodoForm, TodoUpdateForm
from homework.models import Todo, Comment
from users.forms import SignupForm, LoginForm
from utils.email import send_email

User = get_user_model()

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
    form_class = TodoForm

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
    form_class =TodoUpdateForm

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

class SignupView(CreateView):
    template_name = 'registration/signup.html'
    form_class = SignupForm

    def form_valid(self,form):
        user = form.save()
        signer = TimestampSigner()
        signed_user_email = signer.sign(user.email)
        signer_dump = signing.dumps(signed_user_email)

        url = f"{self.request.scheme}://{self.request.META['HTTP_HOST']}/verify/?code={signer_dump}"
        subject = f"[Todo]{user.name}님의 이메일 인증 링크입니다."
        message = f"""
            아래의 링크를 클릭하여 이메일 인증을 완료해주세요. \n\n
            {url} 
            """
        send_email(subject=subject,message=message,from_email=None, to_email = user.email)

        return render(
            request=self.request,
            template_name='registration/signup_done.html',
            context={
                'user' : user,
                     }
        )

def verify_email(request):
    code = request.GET.get('code', '')

    signer = TimestampSigner()
    try:
        decoded_user_email = signing.loads(code)
        user_email = signer.unsign(decoded_user_email, max_age=60 * 5)
    except (TypeError, SignatureExpired):
        return render(request, 'registration/verify_failed.html')

    user = get_object_or_404(User, email=user_email)
    user.is_active = True
    user.save()
    return render(request, 'registration/verify_success.html')


class LoginView(FormView):
    template_name = "registration/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("todo_list")

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user=user)
        return HttpResponseRedirect(self.get_success_url())



