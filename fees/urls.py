from django.urls import path
from . import views
app_name='fees'
urlpatterns=[
    path('', views.student_list, name='student_list'),
    path('add/', views.student_add, name='student_add'),
    path('edit/<int:pk>/', views.student_edit, name='student_edit'),
    path('delete/<int:pk>/', views.student_delete, name='student_delete'),
    path('toggle_reg_fee/<int:pk>/', views.toggle_reg_fee, name='toggle_reg_fee'),
    path('toggle_due/<int:due_id>/', views.toggle_due, name='toggle_due'),
]
