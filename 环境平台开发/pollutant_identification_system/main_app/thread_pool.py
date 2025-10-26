import os
import uuid
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import logging
import uuid

# 配置极简日志 - 只记录用户访问
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('access.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('access')

# 结果文件存储路径
RESULTS_DIR = r"D:\环境平台开发\pollutant_identification_system\media\results"
EFFECT_RESULTS_DIR = r"D:\环境平台开发\pollutant_identification_system\media\effect_results"
TRACING_RESULTS_DIR = r"D:\环境平台开发\pollutant_identification_system\media\tracing_results"
if not os.path.exists(TRACING_RESULTS_DIR):
    os.makedirs(TRACING_RESULTS_DIR)

if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

if not os.path.exists(EFFECT_RESULTS_DIR):
    os.makedirs(EFFECT_RESULTS_DIR)

# 全局线程池
executor = ThreadPoolExecutor(max_workers=10)

# 任务结果存储
TASK_RESULTS = {}

# 清理过期结果的线程
def cleanup_results():
    """定期清理过期的结果文件"""
    while True:
        try:
            current_time = time.time()
            ids_to_remove = []
            
            for result_id, data in list(TASK_RESULTS.items()):
                # 删除超过15分钟的结果
                if current_time - data['timestamp'] > 15 * 60:
                    try:
                        if 'path' in data and os.path.exists(data['path']):
                            os.remove(data['path'])
                        ids_to_remove.append(result_id)
                    except Exception:
                        pass
            
            
            for result_id in ids_to_remove:
                del TASK_RESULTS[result_id]

            
            # 额外清理可能未跟踪的effect_results目录中的文件
            for directory in [RESULTS_DIR, EFFECT_RESULTS_DIR, TRACING_RESULTS_DIR]:
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    file_modified_time = os.path.getmtime(file_path)
                    if current_time - file_modified_time > 15 * 60:
                        try:
                            os.remove(file_path)
                        except Exception:
                            pass
        
        except Exception:
            pass
        
        # 每5分钟运行一次
        time.sleep(300)

# 启动清理线程
cleanup_thread = threading.Thread(target=cleanup_results, daemon=True)
cleanup_thread.start()

def process_files_task(file1_binary, file2_binary, user_id):
    """处理文件的任务函数"""
    try:
        # 创建唯一结果ID
        result_id = uuid.uuid4().hex
        
        ## 创建临时文件和结果路径
        temp_file1_path = os.path.join(RESULTS_DIR, f"temp_input1_{user_id}_{result_id}.xlsx")
        temp_file2_path = os.path.join(RESULTS_DIR, f"temp_input2_{user_id}_{result_id}.xlsx")
        result_path = os.path.join(RESULTS_DIR, f"result_{user_id}_{result_id}.xlsx")
        
        try:
            # 写入临时文件
            with open(temp_file1_path, 'wb') as f:
                f.write(file1_binary)
                
            with open(temp_file2_path, 'wb') as f:
                f.write(file2_binary)
            
            # 导入计算模块并处理
            from . import calculate
            calculate.process_data(temp_file1_path, temp_file2_path, result_path)
            
            # 保存结果信息
            TASK_RESULTS[result_id] = {
                'status': 'completed',
                'path': result_path,
                'timestamp': time.time(),
                'user_id': user_id
            }
            
            return result_id
            
        finally:
            # 清理临时输入文件
            try:
                if os.path.exists(temp_file1_path):
                    os.remove(temp_file1_path)
                if os.path.exists(temp_file2_path):
                    os.remove(temp_file2_path)
            except Exception:
                pass
                
    except Exception as e:
        # 创建错误结果记录，但不记录日志
        error_id = uuid.uuid4().hex
        TASK_RESULTS[error_id] = {
            'status': 'failed',
            'error': str(e),
            'timestamp': time.time(),
            'user_id': user_id
        }
        
        return error_id

# 提交任务到线程池并返回跟踪ID
def submit_task(file1_binary, file2_binary, user_id):
    """提交任务到线程池并返回可用于跟踪的ID"""
    future = executor.submit(
        process_files_task,
        file1_binary,
        file2_binary,
        user_id
    )
    
    # 生成任务跟踪ID
    task_id = uuid.uuid4().hex
    
    # 存储future对象以便检查状态
    TASK_RESULTS[task_id] = {
        'future': future,
        'timestamp': time.time(),
        'user_id': user_id,
        'status': 'processing'
    }
    
    return task_id

def process_endpoint_task(endpoint, user_id):
    """处理毒性终点分析的任务函数"""
    try:
        # 创建唯一结果ID
        result_id = uuid.uuid4().hex
        
        # 查找同一用户最新的暴露分析结果
        exposure_result_path = None
        latest_timestamp = 0
        
        for temp_id, data in TASK_RESULTS.items():
            if (data.get('user_id') == user_id and 
                data.get('status') == 'completed' and 
                'path' in data and 
                os.path.exists(data['path']) and 
                'timestamp' in data and 
                data['timestamp'] > latest_timestamp and
                'path' in data and 
                data['path'].endswith('.xlsx') and
                'result_' in data['path']):  # 暴露分析的结果文件名格式
                
                latest_timestamp = data['timestamp']
                exposure_result_path = data['path']
        
        # 如果找不到暴露分析的结果，抛出错误
        if not exposure_result_path:
            raise ValueError("未找到暴露分析结果，请先完成暴露分析步骤")
        
        # 创建效应分析结果文件路径
        result_path = os.path.join(EFFECT_RESULTS_DIR, f"effect_analysis_{user_id}_{result_id}.xlsx")
        
        try:
            # 导入计算模块并处理
            from . import calculate_effects
            risk_data = calculate_effects.calculate_risk_ranking(endpoint, exposure_result_path, result_path)           
            # 保存结果信息
            TASK_RESULTS[result_id] = {
                'status': 'completed',
                'path': result_path,
                'timestamp': time.time(),
                'user_id': user_id,
                'endpoint': endpoint,
                'type': 'effects_analysis'
            }

            return result_id, risk_data  
        except Exception as e:
            # 记录错误但不抛出
            logger.error(f"效应分析计算错误: {str(e)}")
            raise
            
    except Exception as e:
        # 创建错误结果记录
        error_id = uuid.uuid4().hex
        TASK_RESULTS[error_id] = {
            'status': 'failed',
            'error': str(e),
            'timestamp': time.time(),
            'user_id': user_id,
            'type': 'effects_analysis'
        }
        
        return error_id, None

# 提交效应分析任务函数
def submit_endpoint_task(endpoint, user_id):
    """提交效应分析任务到线程池并返回可用于跟踪的ID"""
    future = executor.submit(
        process_endpoint_task,
        endpoint,
        user_id
    )
    
    # 生成任务跟踪ID
    task_id = uuid.uuid4().hex
    
    # 存储future对象以便检查状态
    TASK_RESULTS[task_id] = {
        'future': future,
        'timestamp': time.time(),
        'user_id': user_id,
        'status': 'processing',
        'type': 'effects_analysis_task'
    }
    
    return task_id

def process_tracing_task(file_binary, user_id):
    """处理风险溯源的任务函数"""
    try:
        # 创建唯一结果ID
        result_id = uuid.uuid4().hex
        
        # 查找同一用户最新的暴露分析结果
        exposure_result_path = None
        latest_timestamp = 0
        
        for temp_id, data in TASK_RESULTS.items():
            if (data.get('user_id') == user_id and 
                data.get('status') == 'completed' and 
                'path' in data and 
                os.path.exists(data['path']) and 
                'timestamp' in data and 
                data['timestamp'] > latest_timestamp and
                'path' in data and 
                data['path'].endswith('.xlsx') and
                'result_' in data['path']):  # 暴露分析的结果文件名格式
                
                latest_timestamp = data['timestamp']
                exposure_result_path = data['path']
        
        # 如果找不到暴露分析的结果，抛出错误
        if not exposure_result_path:
            raise ValueError("未找到暴露分析结果，请先完成暴露分析步骤")
        # 创建临时文件和结果路径
        temp_file_path = os.path.join(TRACING_RESULTS_DIR, f"temp_input_{user_id}_{result_id}.xlsx")
        result_path = os.path.join(TRACING_RESULTS_DIR, f"tracing_result_{user_id}_{result_id}.xlsx")
        
        try:
            # 写入临时文件
            with open(temp_file_path, 'wb') as f:
                f.write(file_binary)
            
            
            # 导入计算模块并处理

            from . import calculate_tracing
            calculate_tracing.process_tracing(temp_file_path, exposure_result_path,result_path)
            
            
            # 保存结果信息
            TASK_RESULTS[result_id] = {
                'status': 'completed',
                'path': result_path,
                'timestamp': time.time(),
                'user_id': user_id,
                'type': 'tracing_analysis'
            }
            
            return result_id
            
        finally:
            # 清理临时输入文件
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception:
                pass
            
    except Exception as e:
        # 创建错误结果记录
        error_id = uuid.uuid4().hex
        TASK_RESULTS[error_id] = {
            'status': 'failed',
            'error': str(e),
            'timestamp': time.time(),
            'user_id': user_id,
            'type': 'tracing_analysis'
        }
        
        # 记录错误
        logger.error(f"风险溯源分析错误: {str(e)}")
        
        return error_id

# 提交风险溯源任务函数
def submit_tracing_task(file_binary, user_id):
    """提交风险溯源任务到线程池并返回可用于跟踪的ID"""
    future = executor.submit(
        process_tracing_task,
        file_binary,
        user_id
    )
    
    # 生成任务跟踪ID
    task_id = uuid.uuid4().hex
    
    # 存储future对象以便检查状态
    TASK_RESULTS[task_id] = {
        'future': future,
        'timestamp': time.time(),
        'user_id': user_id,
        'status': 'processing',
        'type': 'tracing_analysis_task'
    }
    
    return task_id


