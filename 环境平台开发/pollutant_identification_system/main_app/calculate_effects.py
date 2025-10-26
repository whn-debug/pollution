import pandas as pd
import time
import numpy as np



def calculate_risk_ranking(endpoint, exposure_result_path, result_path):
    """
    处理两个输入文件并生成输出文件
    
    参数:
    input_file1_path: 参考物质的文件路径
    input_file2_path: 检出物质的文件路径
    output_file_path: 结果输出的文件路径
    """
    
    try:
        # 生成符合前端需要的标准化数据
        risk_data = pd.read_excel('./main_app/rank-inchikey-HQ.xlsx')

        # 处理所有的NaN值，转换为None(将被JSON序列化为null)
        risk_data = risk_data.replace({np.nan: None})
        
        # 保存结果文件
        risk_data.to_excel(result_path, index=False)
        
        # 转换为字典列表并返回
        return risk_data.to_dict(orient='records')
        
    except Exception as e:
        raise