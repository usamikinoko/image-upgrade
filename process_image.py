#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2

def create_directory_if_not_exists(directory_path):
    """创建目录（如果不存在）"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"已创建目录: {directory_path}")

def histogram_equalization(image):
    """对图像进行直方图均衡化（模糊化）"""
    # 转换为OpenCV格式进行处理
    img_array = np.array(image)
    
    # 如果是RGB图像，分别对每个通道进行直方图均衡化
    if len(img_array.shape) == 3:
        # 分离通道
        channels = cv2.split(img_array)
        equalized_channels = []
        
        for channel in channels:
            # 应用高斯模糊
            blurred = cv2.GaussianBlur(channel, (15, 15), 0)
            equalized_channels.append(blurred)
        
        # 合并通道
        equalized_img = cv2.merge(equalized_channels)
        return Image.fromarray(equalized_img)
    else:
        # 灰度图像
        blurred = cv2.GaussianBlur(img_array, (15, 15), 0)
        return Image.fromarray(blurred)

def increase_saturation(image, factor=1.2):
    """增加图像饱和度，默认增加20%"""
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

def sharpen_image(image, factor=1.5):
    """轻度锐化图像"""
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(factor)

def process_image(input_path, output_dir, output_filename=None):
    """处理图像并保存"""
    try:
        # 确保输出目录存在
        create_directory_if_not_exists(output_dir)
        
        # 如果没有指定输出文件名，使用原文件名
        if output_filename is None:
            base_name = os.path.basename(input_path)
            output_filename = f"processed_{base_name}"
        
        output_path = os.path.join(output_dir, output_filename)
        
        # 打开图像
        print(f"正在打开图像: {input_path}")
        image = Image.open(input_path)
        
        # 步骤1: 直方图模糊化
        print("步骤1: 应用直方图模糊化")
        image = histogram_equalization(image)
        
        # 步骤2: 增加饱和度20%
        print("步骤2: 增加饱和度20%")
        image = increase_saturation(image, 1.2)
        
        # 步骤3: 轻度锐化
        print("步骤3: 应用轻度锐化")
        image = sharpen_image(image)
        
        # 保存处理后的图像
        image.save(output_path)
        print(f"处理完成! 图像已保存到: {output_path}")
        
        return True
    except Exception as e:
        print(f"处理图像时出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 输入图像路径
    input_image = os.path.join(project_root, "image.png")
    
    # 输出目录
    output_directory = os.path.join(project_root, "outputs")
    
    # 处理图像
    if os.path.exists(input_image):
        process_image(input_image, output_directory)
    else:
        print(f"错误: 找不到输入图像 {input_image}")
        print("请确保在项目根目录下有名为'image.png'的图像文件")
