from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'tasker'

urlpatterns = [
    path('', views.index, name='index'),
    path('archive/', views.ArchiveTaskDT.as_view(), name='archive'),
    path('add/', views.task_edit, name='task_add'),
    path('mod/<int:task_id>/', views.task_edit, name='task_edit'),
    path('del/<int:task_id>/', views.task_del, name='task_del'),
    path('status/<int:task_id>/', views.task_status, name='task_status'),
    path('summary/<int:task_id>/', views.SummaryList.as_view(), name='summary_list'),
    path('summary/add/<int:task_id>/', views.summary_edit, name='summary_add'), 
    path('summary/mod/<int:task_id>/<int:summary_id>/', views.summary_edit, name='summary_mod'),
    path('summary/del/<int:task_id>/<int:summary_id>/', views.summary_del, name='summary_del'),
    path('detail/<int:summary_id>/', views.summary_detail, name="summary_detail"),
]
