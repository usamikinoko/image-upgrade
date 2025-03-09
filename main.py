#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

def create_directory_if_not_exists(directory_path):
    """创建目录（如果不存在）"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"已创建目录: {directory_path}")

def load_config(config_path):
    """加载YAML配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        print(f"已成功加载配置文件: {config_path}")
        return config
    except Exception as e:
        print(f"加载配置文件时出错: {str(e)}")
        print("将使用默认配置")
        return get_default_config()

def get_default_config():
    """返回默认配置"""
    return {
        'io': {
            'input_image': 'image.png',
            'output_directory': 'outputs',
            'save_intermediate': True,
            'output_format': 'png',
            'output_quality': 95
        },
        'blur': {
            'enabled': True,
            'type': 'gaussian',
            'gaussian': {'radius': 7},
            'box': {'radius': 5},
            'median': {'size': 3}
        },
        'saturation': {
            'enabled': True,
            'factor': 1.2
        },
        'sharpen': {
            'enabled': True,
            'type': 'basic',
            'basic': {'factor': 1.5},
            'unsharp_mask': {'radius': 2, 'percent': 150, 'threshold': 3}
        }
    }

def apply_blur(image, config):
    """根据配置应用模糊效果"""
    if not config.get('enabled', True):
        return image
    
    blur_type = config.get('type', 'gaussian')
    
    if blur_type == 'gaussian':
        radius = config.get('gaussian', {}).get('radius', 7)
        return image.filter(ImageFilter.GaussianBlur(radius=radius))
    elif blur_type == 'box':
        radius = config.get('box', {}).get('radius', 5)
        return image.filter(ImageFilter.BoxBlur(radius=radius))
    elif blur_type == 'median':
        size = config.get('median', {}).get('size', 3)
        return image.filter(ImageFilter.MedianFilter(size=size))
    else:
        print(f"未知的模糊类型: {blur_type}，使用高斯模糊")
        return image.filter(ImageFilter.GaussianBlur(radius=7))

def apply_saturation(image, config):
    """根据配置应用饱和度调整"""
    if not config.get('enabled', True):
        return image
    
    factor = config.get('factor', 1.2)
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

def apply_sharpen(image, config):
    """根据配置应用锐化效果"""
    if not config.get('enabled', True):
        return image
    
    sharpen_type = config.get('type', 'basic')
    
    if sharpen_type == 'basic':
        factor = config.get('basic', {}).get('factor', 1.5)
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
    elif sharpen_type == 'unsharp_mask':
        # 使用PIL的UnsharpMask滤镜
        radius = config.get('unsharp_mask', {}).get('radius', 2)
        percent = config.get('unsharp_mask', {}).get('percent', 150)
        threshold = config.get('unsharp_mask', {}).get('threshold', 3)
        return image.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))
    else:
        print(f"未知的锐化类型: {sharpen_type}，使用基本锐化")
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(1.5)

def apply_additional_processing(image, config):
    """应用其他可选的处理步骤"""
    if not config:
        return image
    
    # 应用亮度调整
    if config.get('brightness', {}).get('enabled', False):
        factor = config.get('brightness', {}).get('factor', 1.0)
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(factor)
    
    # 应用对比度调整
    if config.get('contrast', {}).get('enabled', False):
        factor = config.get('contrast', {}).get('factor', 1.0)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(factor)
    
    # 应用裁剪
    if config.get('crop', {}).get('enabled', False):
        crop_config = config.get('crop', {})
        width, height = image.size
        
        # 处理百分比值
        left = crop_config.get('left', 0)
        top = crop_config.get('top', 0)
        right = crop_config.get('right', '100%')
        bottom = crop_config.get('bottom', '100%')
        
        # 将百分比转换为像素
        if isinstance(left, str) and left.endswith('%'):
            left = int(float(left.strip('%')) * width / 100)
        if isinstance(top, str) and top.endswith('%'):
            top = int(float(top.strip('%')) * height / 100)
        if isinstance(right, str) and right.endswith('%'):
            right = int(float(right.strip('%')) * width / 100)
        if isinstance(bottom, str) and bottom.endswith('%'):
            bottom = int(float(bottom.strip('%')) * height / 100)
        
        # 裁剪图像
        image = image.crop((int(left), int(top), int(right), int(bottom)))
    
    # 应用调整大小
    if config.get('resize', {}).get('enabled', False):
        resize_config = config.get('resize', {})
        width, height = image.size
        
        # 处理百分比值
        new_width = resize_config.get('width', '100%')
        new_height = resize_config.get('height', '100%')
        
        # 将百分比转换为像素
        if isinstance(new_width, str) and new_width.endswith('%'):
            new_width = int(float(new_width.strip('%')) * width / 100)
        if isinstance(new_height, str) and new_height.endswith('%'):
            new_height = int(float(new_height.strip('%')) * height / 100)
        
        # 调整大小
        keep_aspect_ratio = resize_config.get('keep_aspect_ratio', True)
        if keep_aspect_ratio:
            image = image.resize((int(new_width), int(new_height)), Image.LANCZOS)
        else:
            image = image.resize((int(new_width), int(new_height)), Image.LANCZOS)
    
    return image

def process_image(config):
    """根据配置处理图像"""
    try:
        # 获取IO配置
        io_config = config.get('io', {})
        project_root = os.path.dirname(os.path.abspath(__file__))
        input_image_path = os.path.join(project_root, io_config.get('input_image', 'image.png'))
        output_directory = os.path.join(project_root, io_config.get('output_directory', 'outputs'))
        save_intermediate = io_config.get('save_intermediate', True)
        output_format = io_config.get('output_format', 'png')
        output_quality = io_config.get('output_quality', 95)
        
        # 确保输出目录存在
        create_directory_if_not_exists(output_directory)
        
        # 获取原始文件名（不含扩展名）
        base_name = os.path.splitext(os.path.basename(input_image_path))[0]
        
        # 检查输入图像是否存在
        if not os.path.exists(input_image_path):
            print(f"错误: 找不到输入图像 {input_image_path}")
            print("请确保在项目根目录下有指定的图像文件")
            return False
        
        # 打开图像
        print(f"正在打开图像: {input_image_path}")
        original_image = Image.open(input_image_path)
        current_image = original_image.copy()
        
        # 步骤1: 直方图模糊化
        print("步骤1: 应用直方图模糊化")
        blurred_image = apply_blur(current_image, config.get('blur', {}))
        
        # 保存步骤1的结果
        if save_intermediate:
            step1_output = os.path.join(output_directory, f"{base_name}_step1_blurred.{output_format}")
            blurred_image.save(step1_output, quality=output_quality)
            print(f"步骤1完成! 图像已保存到: {step1_output}")
        
        current_image = blurred_image
        
        # 步骤2: 增加饱和度
        print("步骤2: 调整饱和度")
        saturated_image = apply_saturation(current_image, config.get('saturation', {}))
        
        # 保存步骤2的结果
        if save_intermediate:
            step2_output = os.path.join(output_directory, f"{base_name}_step2_saturated.{output_format}")
            saturated_image.save(step2_output, quality=output_quality)
            print(f"步骤2完成! 图像已保存到: {step2_output}")
        
        current_image = saturated_image
        
        # 步骤3: 锐化
        print("步骤3: 应用锐化")
        sharpened_image = apply_sharpen(current_image, config.get('sharpen', {}))
        
        # 保存步骤3的结果
        if save_intermediate:
            step3_output = os.path.join(output_directory, f"{base_name}_step3_sharpened.{output_format}")
            sharpened_image.save(step3_output, quality=output_quality)
            print(f"步骤3完成! 图像已保存到: {step3_output}")
        
        current_image = sharpened_image
        
        # 应用其他处理步骤
        if 'additional' in config:
            print("应用其他处理步骤")
            current_image = apply_additional_processing(current_image, config.get('additional', {}))
        
        # 保存最终处理后的图像
        final_output = os.path.join(output_directory, f"{base_name}_final.{output_format}")
        current_image.save(final_output, quality=output_quality)
        print(f"全部处理完成! 最终图像已保存到: {final_output}")
        
        return True
    except Exception as e:
        print(f"处理图像时出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 加载配置文件
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    config = load_config(config_path)
    
    # 处理图像
    process_image(config)
