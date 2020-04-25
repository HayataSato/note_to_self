from django.urls import path, include
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name = 'book_manager'

urlpatterns = [
    path('', views.index, name='index'),
    path('archive/', views.ArchiveBookDT.as_view(), name='archive'),
    path('add/', views.book_edit, name='book_add'),
    path('mod/<int:book_id>/', views.book_edit, name='book_edit'),
    path('del/<int:book_id>/', views.book_del, name='book_del'),
    path('status/<int:book_id>/', views.book_status, name='book_status'),
    path('summary/<int:book_id>/', views.SummaryList.as_view(), name='summary_list'),
    path('summary/add/<int:book_id>/', views.SummaryEdit.as_view(), name='summary_add'),
    path('summary/mod/<int:book_id>/<int:summary_id>/', views.SummaryEdit.as_view(), name='summary_mod'),
    path('summary/del/<int:book_id>/<int:summary_id>/', views.summary_del, name='summary_del'),
    path('detail/<int:summary_id>/', views.summary_detail, name="summary_detail"),
]
