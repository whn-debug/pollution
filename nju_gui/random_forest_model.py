import pandas as pd
import time



def process_data(input_file1_path, input_file2_path, output_file_path):
    """
    处理两个输入文件并生成输出文件
    
    参数:
    input_file1_path: 参考物质的文件路径
    input_file2_path: 检出物质的文件路径
    output_file_path: 结果输出的文件路径
    """
    
    # 读取输入文件

    reference_data = pd.read_excel(input_file1_path)
    
    detected_data = pd.read_excel(input_file2_path)
    

    
    result_data = pd.DataFrame( {
        'a':1,
        'b':2,
        'c':3
    })
    
    time.sleep(0.5)
        # 保存结果到输出文件
    result_data.to_excel(output_file_path, index=False)
    return result_data