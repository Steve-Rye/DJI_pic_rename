import os
import exiftool
from datetime import datetime

def parse_date(date_str):
    """解析日期字符串为指定格式"""
    try:
        if '+' in date_str:
            date_str = date_str.split('+')[0]
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
    except ValueError:
        return None

def get_device_name(metadata):
    """获取设备名称"""
    model_keys = ['EXIF:Model', 'IFD0:Model']
    make_keys = ['EXIF:Make', 'IFD0:Make']
    
    # 尝试获取设备型号
    for key in model_keys:
        if key in metadata and metadata[key]:
            return metadata[key].replace(' ', '_')
    
    # 如果没有型号，尝试获取制造商
    for key in make_keys:
        if key in metadata and metadata[key]:
            return metadata[key].replace(' ', '_')
    
    return 'Unknown'

def get_exif_info(et, image_path):
    """获取图片的拍摄时间和设备信息"""
    try:
        metadata = et.get_metadata(image_path)[0]
        date_keys = ['EXIF:DateTimeOriginal', 'EXIF:CreateDate', 'XMP:CreateDate', 'EXIF:ModifyDate']
        
        date_time = None
        for key in date_keys:
            if key in metadata and (date := parse_date(metadata[key])):
                date_time = date
                break
                
        device = get_device_name(metadata)
        return date_time, device
    except Exception as e:
        print(f"处理 {image_path} 时出错: {str(e)}\n", flush=True)
        return None, None

def rename_images(input_folder):
    """重命名文件夹中的所有图片"""
    image_extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.raw', '.arw', '.cr2')
    
    with exiftool.ExifToolHelper() as et:
        for filename in os.listdir(input_folder):
            if not filename.lower().endswith(image_extensions):
                continue
                
            file_path = os.path.join(input_folder, filename)
            date_time, device = get_exif_info(et, file_path)
            
            if date_time:
                file_ext = os.path.splitext(filename)[1]
                counter = 1
                while True:
                    new_name = f"{device}_{date_time}_{counter}{file_ext}"
                    new_path = os.path.join(input_folder, new_name)
                    if not os.path.exists(new_path):
                        break
                    counter += 1
                
                try:
                    os.rename(file_path, new_path)
                    print(f"已重命名: {filename} -> {new_name}\n", flush=True)
                except Exception as e:
                    print(f"重命名失败: {filename} ({e})\n", flush=True)
            else:
                print(f"未找到日期信息: {filename}\n", flush=True)

if __name__ == "__main__":
    input_folder = "main"
    if not os.path.exists(input_folder):
        print(f"错误: 文件夹 '{input_folder}' 不存在\n", flush=True)
    else:
        rename_images(input_folder)
        print("重命名完成！\n", flush=True)