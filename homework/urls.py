from django.urls import path

from homework import cb_views
from homework.cb_views import CommentCreateView, CommentDeleteView, CommentUpdateView

urlpatterns = [
    path('',cb_views.TodoListView.as_view(), name='todo_list'),
    path('create/',cb_views.TodoCreateView.as_view(), name='todo_create'),
    path('<int:pk>/',cb_views.TodoDetailView.as_view(), name='todo_info'),
    path('<int:pk>/update/',cb_views.TodoUpdateView.as_view(), name='todo_update'),
    path('<int:pk>/delete/',cb_views.TodoDeleteView.as_view(), name='todo_delete'),
    path('comment/<int:pk>/create/', CommentCreateView.as_view(), name='comment_create'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    path('comment/<int:pk>/update/', CommentUpdateView.as_view(), name='comment_update')
]