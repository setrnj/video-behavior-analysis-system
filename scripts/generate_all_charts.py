#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
毕业论文图表生成主控制脚本
生成所有11类核心图表
"""

import os
import sys
import importlib.util

def import_module_from_file(file_path):
    """从文件路径导入模块"""
    module_name = os.path.basename(file_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    print("=" * 70)
    print("开始生成毕业论文所需11类核心图表")
    print("=" * 70)
    
    # 创建输出目录结构
    output_dirs = [
        'docs/system',           # 系统架构图表
        'docs/exploration',      # 数据探索图表  
        'docs/rfm',              # RFM分析图表
        'docs/clustering',       # 聚类分析图表
        'docs/validation',       # 验证结果图表
        'docs/summary'           # 总结展望图表
    ]
    
    for dir_path in output_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # 图表生成模块列表
    chart_modules = [
        ("系统架构与设计类图表", "scripts/system_architecture.py", 
         ["generate_system_architecture", "generate_er_diagram"]),
        
        ("数据预处理与探索类图表", "scripts/data_exploration.py", 
         ["generate_data_cleaning_flow", "generate_basic_features"]),
        
        ("RFM分析核心图表", "scripts/rfm_analysis.py", 
         ["generate_rfm_distributions", "generate_rfm_matrix"]),
        
        ("用户分群与聚类结果图表", "scripts/user_clustering.py", 
         ["generate_kmeans_clustering", "generate_radar_chart"]),
        
        ("效果验证与趋势分析图表", "scripts/validation_results.py", 
         ["generate_retention_curves", "generate_strategy_comparison"]),
        
        ("总结与展望类图表", "scripts/summary_diagrams.py", 
         ["generate_system_workflow"])
    ]
    
    success_count = 0
    total_count = len(chart_modules)
    
    print(f"\n📊 总共需要生成 {total_count} 类图表")
    print("-" * 50)
    
    for chart_type, file_path, functions in chart_modules:
        print(f"\n🎯 正在生成: {chart_type}")
        print(f"   脚本路径: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"   ❌ 脚本文件不存在: {file_path}")
            continue
            
        try:
            # 导入模块
            module = import_module_from_file(file_path)
            
            # 执行模块中的函数
            for func_name in functions:
                if hasattr(module, func_name):
                    func = getattr(module, func_name)
                    func()
                    print(f"   ✅ {func_name} 执行成功")
                else:
                    print(f"   ⚠ 函数不存在: {func_name}")
            
            success_count += 1
            print(f"   🎉 {chart_type} 生成完成")
            
        except Exception as e:
            print(f"   ❌ {chart_type} 生成失败: {str(e)}")
    
    print("\n" + "=" * 70)
    print(f"图表生成统计: 成功 {success_count}/{total_count} 类图表")
    print("=" * 70)
    
    # 列出所有生成的图表文件
    print("\n📁 生成的图表文件结构:")
    print("-" * 50)
    
    for root, dirs, files in os.walk('docs'):
        level = root.replace('docs', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}📂 {os.path.basename(root)}/")
        sub_indent = ' ' * 2 * (level + 1)
        
        # 只显示PNG文件
        png_files = [f for f in files if f.endswith('.png')]
        for file in png_files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            print(f"{sub_indent}📄 {file} ({file_size/1024:.1f} KB)")
    
    print("\n✅ 所有图表生成完成！图表已保存到 docs/ 目录")
    print("💡 提示: 这些图表可以直接用于毕业论文撰写")

if __name__ == "__main__":
    main()
