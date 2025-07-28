from django.shortcuts import render
from django.http import Http404
from homework.models import Todo


# Create your views here.
def todo_list(request):
    todo_list = Todo.objects.all().values_list('id', 'title')
    result = [{'id': todo[0], 'title': todo[1]} for i, todo in enumerate(todo_list)]

    visits = int(request.COOKIES.get('visits',0))+1

    request.session['count'] = request.session.get('count',0) + 1

    context = {
        'data' : result,
        'count' : request.session.get('count',0)
               }

    response = render(request,'todo_list.html',context)

    response.set_cookie('visits',visits)

    return response


def todo_info(request, todo_id):
    try:
        todo = Todo.objects.get(id=todo_id)
        info = {
            'title': todo.title,
            'description': todo.description,
            'start_date': todo.start_date,
            'end_date': todo.end_date,
            'is_completed': todo.is_completed,
        }
        return render(request, 'todo_info.html', {'data': info})
    except Todo.DoesNotExist:
        raise Http404("Todo does not exist")
# def todo_list(request):
#     context = {'homework' : homework}
#     return render(request,'todo_list.html',context)
# def todo_info(request):
#     context = {'homework':homework.title}
#     return render(request,'todo_info.html',context)
