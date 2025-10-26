# main_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('first_page/', views.first_page, name='first_page'),

     # 添加这些新路径
    path('download-template1/', views.download_template1, name='download_template1'),
    path('download-template2/', views.download_template2, name='download_template2'),
    # 处理文件上传和计算
    path('process_files/', views.process_files, name='process_files'),
    # 检查任务状态
    path('check_task_status/<str:task_id>/', views.check_task_status, name='check_task_status'),
    # 下载结果文件
    path('download_result/<str:result_id>/', views.download_result, name='download_result'),

     # 效应分析和风险排序相关
    path('second_page/', views.second_page, name='second_page'),
    path('process_endpoint/', views.process_endpoint, name='process_endpoint'),
    path('check_endpoint_status/<str:task_id>/', views.check_endpoint_status, name='check_endpoint_status'),
    path('download_risk_ranking/', views.download_risk_ranking, name='download_risk_ranking'),
    path('risk_tracing/', views.risk_tracing, name='risk_tracing'),

    # 风险溯源相关
    path('risk_tracing/', views.risk_tracing, name='risk_tracing'),
    path('download_tracing_template/', views.download_tracing_template, name='download_tracing_template'),
    path('process_tracing/', views.process_tracing, name='process_tracing'),
    path('check_tracing_status/<str:task_id>/', views.check_tracing_status, name='check_tracing_status'),
    path('download_tracing_result/<str:result_id>/', views.download_tracing_result, name='download_tracing_result'),
]