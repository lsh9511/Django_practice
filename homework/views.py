from datetime import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.views.decorators.http import require_http_methods
from pygments.lexers import q

from homework.form import TodoForm, TodoUpdateForm
from homework.models import Todo
from django.urls import reverse


# Create your views here.
def todo_list(request):
    todo_list = Todo.objects.filter(user=request.user).order_by('-created_at')
    q = request.GET.get('q')

    if q:		    # 만약 쿼리파라미터가 존재하면 todo_list에서 해당 쿼리파라미터로 filter를 걸어 조건에 맞는 Todo객체만 가져옵니다.
        todo_list = todo_list.filter(Q(title__icontains=q) | Q(description__icontains=q))

    paginator = Paginator(todo_list, 10) # Paginator 객체를 인스턴스화 합니다.
    page_number = request.GET.get('page') # GET 요청으로부터 page에 담긴 쿼리 파라미터 값을 가져옴
    page_object = paginator.get_page(page_number) # 가져온 페이지 숫자를 이용해서 페이지에 대한 오브젝트를 가져옵니다.
    context = {
        'object_list': page_object.object_list,
        'page_obj': page_object
    }
    return render(request, 'todo_list.html', context)

@login_required()
def todo_info(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    context = {
        'todo' : todo
    }
    return render(request, 'todo_info.html', context)

@login_required()
def todo_create(request):
    form = TodoForm(request.POST or None)
    if form.is_valid():
        todo = form.save(commit=False)
        todo.user = request.user
        todo.save()
        return redirect(reverse('todo_list'),kwargs={'todo_id':todo.pk})
    context = {'form' : form }
    return render(request,'todo_create.html',context)

@login_required()
def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)

    form = TodoUpdateForm(request.POST or None, instance=todo)
    if form.is_valid():
        form.save()
        return redirect(reverse('todo_info',kwargs={'pk':todo.pk}))
    context = {'form' : form,
               'todo' : todo }
    return render(request,'todo_update.html',context)

@login_required()
@require_http_methods(['POST'])
def todo_delete(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    todo.delete()
    return redirect(reverse('todo_list'))
