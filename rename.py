import os
import exiftool
from datetime import datetime

def parse_date(date_str):
    """解析日期字符串为指定格式"""
    try:
        if '+' in date_str:
            date_str = date_str.split('+')[0]
        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').strftime('%y%m%d%H%M%S')
    except ValueError:
        return None

def get_exif_date(et, image_path):
    """获取图片的拍摄时间"""
    try:
        metadata = et.get_metadata(image_path)[0]
        date_keys = ['EXIF:DateTimeOriginal', 'EXIF:CreateDate', 'XMP:CreateDate', 'EXIF:ModifyDate']
        
        for key in date_keys:
            if key in metadata and (date := parse_date(metadata[key])):
                return date
        return None
    except Exception as e:
        print(f"处理 {image_path} 时出错: {str(e)}")
        return None

def rename_images(input_folder):
    """重命名文件夹中的所有图片"""
    image_extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.raw', '.arw', '.cr2')
    
    with exiftool.ExifToolHelper() as et:
        for filename in os.listdir(input_folder):
            if not filename.lower().endswith(image_extensions):
                continue
                
            file_path = os.path.join(input_folder, filename)
            if date_time := get_exif_date(et, file_path):
                file_ext = os.path.splitext(filename)[1]
                new_name = f"{date_time}{file_ext}"
                new_path = os.path.join(input_folder, new_name)
                
                counter = 1
                while os.path.exists(new_path):
                    new_name = f"{date_time}_{counter}{file_ext}"
                    new_path = os.path.join(input_folder, new_name)
                    counter += 1
                
                try:
                    os.rename(file_path, new_path)
                    print(f"已重命名: {filename} -> {new_name}")
                except Exception as e:
                    print(f"重命名失败: {filename} ({e})")
            else:
                print(f"未找到日期信息: {filename}")

if __name__ == "__main__":
    input_folder = "main"
    if not os.path.exists(input_folder):
        print(f"错误: 文件夹 '{input_folder}' 不存在")
    else:
        rename_images(input_folder)
        print("重命名完成！")