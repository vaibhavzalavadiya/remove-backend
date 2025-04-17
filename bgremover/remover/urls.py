from django.urls import path
from . import views

urlpatterns = [
    path('api/remove-background/', views.remove_background, name='remove_background'),
    path('api/task-result/<str:task_id>/', views.get_task_result),
]
