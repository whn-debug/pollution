# Create your views here.
# main_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from django.http import JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from .thread_pool import submit_task, TASK_RESULTS, logger
import os
import uuid
from .thread_pool import executor, process_files_task, TASK_RESULTS
from django.urls import reverse

def index(request):
    """显示您上传的HTML主页"""
    return render(request, 'main_app/index.html')

def user_login(request):
    """处理用户登录"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'欢迎回来，{username}！')
            
            # 如果用户是从特定页面重定向来的，登录后返回该页面
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('index')
        else:
            messages.error(request, '用户名或密码错误，请重试。')
    
    return render(request, 'main_app/login.html')

def user_logout(request):
    """处理用户退出登录"""
    logout(request)
    messages.info(request, '您已成功退出登录。')
    return redirect('index')

@login_required
def first_page(request):
    """暂时为空的功能页面，需要登录才能访问"""
    return render(request, 'main_app/first_page.html')

@login_required
def download_template1(request):
    """下载园区基础信息模板"""
    # 确保模板文件存在
    template_dir = os.path.join(settings.BASE_DIR, 'media', 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    file_path = os.path.join(template_dir, '参考物质峰面积模板.xlsx')
    
    
    # 返回文件
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename="reference_substance.xlsx"'
    return response

@login_required
def download_template2(request):
    """下载环境参数模板"""
    template_dir = os.path.join(settings.BASE_DIR, 'media', 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    file_path = os.path.join(template_dir, '检出物质峰面积模板.xlsx')
    
    
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename="peaks_of_detected_substance.xlsx"'
    return response

@login_required
def process_files(request):
    """处理上传的文件并等待计算完成"""
    if request.method == 'POST':
        try:
            # 记录用户访问
            logger.info(f"用户 {request.user.username} (ID: {request.user.id}) 请求文件处理")
            
            # 获取上传的文件 - 使用正确的参数名
            file1 = request.FILES.get('reference_submit_excel')  # 匹配前端参数名
            file2 = request.FILES.get('detected_submit_excel')   # 匹配前端参数名
            
            if not file1 or not file2:
                return JsonResponse({'status': 'error', 'message': '请上传两个文件'})
            
            # 读取文件内容到内存
            file1_content = file1.read()
            file2_content = file2.read()
            user_id = request.user.id
            
            # 创建唯一结果ID
            result_id = uuid.uuid4().hex
            
            # 创建Future对象，提交到线程池
            future = executor.submit(
                process_files_task,
                file1_content, 
                file2_content, 
                user_id
            )
            
            # 等待计算完成（阻塞当前请求直到计算完成）
            task_result = future.result()
            
            # 检查计算结果
            if task_result and task_result in TASK_RESULTS:
                result_data = TASK_RESULTS[task_result]
                
                if result_data['status'] == 'completed':
                    return JsonResponse({
                        'status': 'success',
                        'message': '计算完成',
                        'result_url': f"/download_result/{task_result}/"
                    })
                else:
                    error_msg = result_data.get('error', '未知错误')
                    return JsonResponse({
                        'status': 'error',
                        'message': f'计算过程出错: {error_msg}'
                    })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': '处理结果无效'
                })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'处理过程中出错: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'})

@login_required
def check_task_status(request, task_id):
    """检查任务状态"""
    if task_id not in TASK_RESULTS:
        return JsonResponse({'status': 'error', 'message': '任务不存在或已过期'})
    
    task_data = TASK_RESULTS[task_id]
    
    # 确保任务属于当前用户
    if task_data.get('user_id') != request.user.id:
        return JsonResponse({'status': 'error', 'message': '您无权访问此任务'})
    
    # 检查是否处理中的任务
    if 'future' in task_data:
        future = task_data['future']
        
        if future.done():
            try:
                # 获取处理结果
                result_id = future.result()
                
                if result_id and result_id in TASK_RESULTS:
                    result_data = TASK_RESULTS[result_id]
                    
                    # 删除原任务记录，保留结果记录
                    del TASK_RESULTS[task_id]
                    
                    # 根据状态返回结果
                    if result_data['status'] == 'completed':
                        return JsonResponse({
                            'status': 'success',
                            'message': '计算完成',
                            'result_url': f"/download_result/{result_id}/"
                        })
                    else:
                        error_msg = result_data.get('error', '未知错误')
                        return JsonResponse({
                            'status': 'error',
                            'message': f'计算过程出错: {error_msg}'
                        })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': '获取结果失败'
                    })
            
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'处理任务结果时出错: {str(e)}'
                })
        else:
            # 任务仍在处理中
            return JsonResponse({
                'status': 'processing',
                'message': '正在计算中，请稍候...'
            })
    
    # 如果是已完成的任务结果
    elif task_data['status'] == 'completed':
        return JsonResponse({
            'status': 'success',
            'message': '计算完成',
            'result_url': f"/download_result/{task_id}/"
        })
    else:
        error_msg = task_data.get('error', '未知错误')
        return JsonResponse({
            'status': 'error',
            'message': f'计算过程出错: {error_msg}'
        })

@login_required
def download_result(request, result_id):
    """下载计算结果"""
    if result_id not in TASK_RESULTS:
        return JsonResponse({'status': 'error', 'message': '文件不存在或已过期'})
    
    result_data = TASK_RESULTS[result_id]
    
    # 检查文件是否属于当前用户
    if result_data.get('user_id') != request.user.id:
        return JsonResponse({'status': 'error', 'message': '您无权访问此文件'})
    
    # 检查文件是否存在
    if 'path' not in result_data or not os.path.exists(result_data['path']):
        return JsonResponse({'status': 'error', 'message': '结果文件不存在'})
    
    # 记录下载
    logger.info(f"用户 {request.user.username} 下载结果文件")
    
    # 返回文件
    try:
        return FileResponse(
            open(result_data['path'], 'rb'),
            as_attachment=True,
            filename=f"分析结果_{result_id[:8]}.xlsx"
        )
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'下载文件时出错: {str(e)}'})
    
@login_required
def second_page(request):
    """效应分析页面，需要登录才能访问"""
    return render(request, 'main_app/second_page.html')

# 修改views.py中的process_endpoint函数

@login_required
def process_endpoint(request):
    """处理选择的毒性终点并提交异步任务"""
    if request.method == 'POST':
        try:
            # 记录用户访问
            logger.info(f"用户 {request.user.username} (ID: {request.user.id}) 请求效应分析")
            
            # 获取选择的毒性终点
            endpoint = request.POST.get('endpoint')
            
            if not endpoint:
                return JsonResponse({'status': 'error', 'message': '请选择一个毒性终点'})
            
            # 提交任务到线程池
            from .thread_pool import submit_endpoint_task
            task_id = submit_endpoint_task(endpoint, request.user.id)
            
            # 保存任务ID到会话中，以便后续使用
            request.session['effect_task_id'] = task_id
            
            # 立即返回任务ID，不等待计算完成
            return JsonResponse({
                'status': 'processing',
                'message': '任务已提交，正在处理中',
                'task_id': task_id,
                'check_url': reverse('check_endpoint_status', args=[task_id])
            })
            
        except Exception as e:
            # 处理其他异常
            logger.error(f"处理效应分析请求时出错: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'处理过程中出错: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'})

@login_required
def check_endpoint_status(request, task_id):
    """检查效应分析任务状态"""
    from .thread_pool import TASK_RESULTS
    
    if task_id not in TASK_RESULTS:
        return JsonResponse({'status': 'error', 'message': '任务不存在或已过期'})
    
    task_data = TASK_RESULTS[task_id]
    
    # 确保任务属于当前用户
    if task_data.get('user_id') != request.user.id:
        return JsonResponse({'status': 'error', 'message': '您无权访问此任务'})
    
    # 检查是否处理中的任务
    if 'future' in task_data:
        future = task_data['future']
        
        if future.done():
            try:
                # 获取处理结果
                result_id, risk_data = future.result()
                
                if result_id and result_id in TASK_RESULTS:
                    result_data = TASK_RESULTS[result_id]
                    
                    # 删除原任务记录，保留结果记录
                    del TASK_RESULTS[task_id]
                    
                    # 保存结果ID到会话
                    request.session['effect_result_id'] = result_id
                    
                    # 根据状态返回结果
                    if result_data['status'] == 'completed':
                        return JsonResponse({
                            'status': 'success',
                            'message': '计算完成',
                            'result_id': result_id,
                            'risk_data': risk_data,
                            'download_url': f"{reverse('download_risk_ranking')}?result_id={result_id}"
                        })
                    else:
                        error_msg = result_data.get('error', '未知错误')
                        return JsonResponse({
                            'status': 'error',
                            'message': f'计算过程出错: {error_msg}'
                        })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': '获取结果失败'
                    })
            
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'处理任务结果时出错: {str(e)}'
                })
        else:
            # 任务仍在处理中
            return JsonResponse({
                'status': 'processing',
                'message': '正在计算中，请稍候...'
            })
    
    # 如果是已完成的任务结果
    elif task_data['status'] == 'completed':
        return JsonResponse({
            'status': 'success',
            'message': '计算完成',
            'result_id': task_id,
            'download_url': f"{reverse('download_risk_ranking')}?result_id={task_id}"
        })
    else:
        error_msg = task_data.get('error', '未知错误')
        return JsonResponse({
            'status': 'error',
            'message': f'计算过程出错: {error_msg}'
        })

@login_required
def download_risk_ranking(request):
    """下载风险排序结果"""
    result_id = request.GET.get('result_id')
    
    if not result_id or result_id not in TASK_RESULTS:
        return JsonResponse({'status': 'error', 'message': '文件不存在或已过期'})
    
    result_data = TASK_RESULTS[result_id]
    
    # 检查文件是否属于当前用户
    if result_data.get('user_id') != request.user.id:
        return JsonResponse({'status': 'error', 'message': '您无权访问此文件'})
    
    # 检查文件是否存在
    if 'path' not in result_data or not os.path.exists(result_data['path']):
        return JsonResponse({'status': 'error', 'message': '结果文件不存在'})
    
    # 记录下载
    logger.info(f"用户 {request.user.username} 下载风险排序结果文件")
    
    # 返回文件
    try:
        return FileResponse(
            open(result_data['path'], 'rb'),
            as_attachment=True,
            filename=f"风险排序结果_{result_id[:8]}.xlsx"
        )
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'下载文件时出错: {str(e)}'})


@login_required
def risk_tracing(request):
    """风险溯源页面"""
    # 这里后续可以实现风险溯源相关功能
    return render(request, 'main_app/risk_tracing.html')

# 添加到views.py文件

@login_required
def risk_tracing(request):
    """风险溯源页面，需要登录才能访问"""
    return render(request, 'main_app/risk_tracing.html')

@login_required
def download_tracing_template(request):
    """下载风险溯源模板"""
    # 确保模板文件存在
    template_dir = os.path.join(settings.BASE_DIR, 'media', 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    file_path = os.path.join(template_dir, '企业生产使用化学品清单模板.xlsx')
    
    
    # 返回文件
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename="企业生产使用化学品清单模板.xlsx"'
    return response

@login_required
def process_tracing(request):
    """处理风险溯源请求"""
    if request.method == 'POST':
        try:
            # 记录用户访问
            logger.info(f"用户 {request.user.username} (ID: {request.user.id}) 请求风险溯源分析")
            
            # 获取上传的文件
            tracing_file = request.FILES.get('tracing_file')
            
            if not tracing_file:
                return JsonResponse({'status': 'error', 'message': '请上传企业生产使用化学品清单'})
            
            # 读取文件内容到内存
            file_binary = tracing_file.read()
            
            # 提交任务到线程池
            from .thread_pool import submit_tracing_task
            task_id = submit_tracing_task(file_binary, request.user.id)
            
            # 返回任务ID和检查状态的URL
            return JsonResponse({
                'status': 'processing',
                'message': '任务已提交，正在处理中',
                'task_id': task_id,
                'check_url': reverse('check_tracing_status', args=[task_id])
            })
            
        except Exception as e:
            logger.error(f"处理风险溯源请求时出错: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'处理过程中出错: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'})

@login_required
def check_tracing_status(request, task_id):
    """检查风险溯源任务状态"""
    from .thread_pool import TASK_RESULTS
    
    if task_id not in TASK_RESULTS:
        return JsonResponse({'status': 'error', 'message': '任务不存在或已过期'})
    
    task_data = TASK_RESULTS[task_id]
    
    # 确保任务属于当前用户
    if task_data.get('user_id') != request.user.id:
        return JsonResponse({'status': 'error', 'message': '您无权访问此任务'})
    
    # 检查是否处理中的任务
    if 'future' in task_data:
        future = task_data['future']
        
        if future.done():
            try:
                # 获取处理结果
                result_id = future.result()
                
                if result_id and result_id in TASK_RESULTS:
                    result_data = TASK_RESULTS[result_id]
                    
                    # 删除原任务记录，保留结果记录
                    del TASK_RESULTS[task_id]
                    
                    # 保存结果ID到会话
                    request.session['tracing_result_id'] = result_id
                    
                    # 根据状态返回结果
                    if result_data['status'] == 'completed':
                        return JsonResponse({
                            'status': 'success',
                            'message': '计算完成',
                            'result_id': result_id,
                            'download_url': reverse('download_tracing_result', args=[result_id])
                        })
                    else:
                        error_msg = result_data.get('error', '未知错误')
                        return JsonResponse({
                            'status': 'error',
                            'message': f'计算过程出错: {error_msg}'
                        })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': '获取结果失败'
                    })
            
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'处理任务结果时出错: {str(e)}'
                })
        else:
            # 任务仍在处理中
            return JsonResponse({
                'status': 'processing',
                'message': '正在计算中，请稍候...'
            })
    
    # 如果是已完成的任务结果
    elif task_data['status'] == 'completed':
        return JsonResponse({
            'status': 'success',
            'message': '计算完成',
            'result_id': task_id,
            'download_url': reverse('download_tracing_result', args=[task_id])
        })
    else:
        error_msg = task_data.get('error', '未知错误')
        return JsonResponse({
            'status': 'error',
            'message': f'计算过程出错: {error_msg}'
        })

@login_required
def download_tracing_result(request, result_id):
    """下载风险溯源结果"""
    from .thread_pool import TASK_RESULTS
    
    if result_id not in TASK_RESULTS:
        return JsonResponse({'status': 'error', 'message': '文件不存在或已过期'})
    
    result_data = TASK_RESULTS[result_id]
    
    # 检查文件是否属于当前用户
    if result_data.get('user_id') != request.user.id:
        return JsonResponse({'status': 'error', 'message': '您无权访问此文件'})
    
    # 检查文件是否存在
    if 'path' not in result_data or not os.path.exists(result_data['path']):
        return JsonResponse({'status': 'error', 'message': '结果文件不存在'})
    
    # 记录下载
    logger.info(f"用户 {request.user.username} 下载风险溯源结果文件")
    
    # 返回文件
    try:
        return FileResponse(
            open(result_data['path'], 'rb'),
            as_attachment=True,
            filename=f"风险溯源结果_{result_id[:8]}.xlsx"
        )
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'下载文件时出错: {str(e)}'})