import nibabel as nib
import numpy as np
import json

def validate_conversion(nii_path, yolo_format, img_shape):
    """
    將YOLO格式轉回物理座標以驗證
    """
    class_id, x, y, z, w, h, d = map(float, yolo_format.split())
    
    # 轉回voxel座標
    x_voxel = x * img_shape[0]
    y_voxel = y * img_shape[1]
    z_voxel = z * img_shape[2]
    
    w_voxel = w * img_shape[0]
    h_voxel = h * img_shape[1]
    d_voxel = z * img_shape[2]
    
    # 轉回物理座標
    img = nib.load(nii_path)
    voxel_spacing = img.header.get_zooms()
    print(voxel_spacing)
    
    x_physical = x_voxel * voxel_spacing[0]
    y_physical = y_voxel * voxel_spacing[1]
    z_physical = z_voxel * voxel_spacing[2]
    
    return [x_physical, y_physical, z_physical]

def convert_to_yolo_format(roi_center, roi_size, all_center, all_size):
    
    # 將ROI中心點從物理座標轉換為影像座標
    roi_center_voxel = [
        (roi_center[0] - (all_center[0] - all_size[0]/2)) / voxel_spacing[0],
        (roi_center[1] - (all_center[1] - all_size[1]/2)) / voxel_spacing[1],
        (roi_center[2] - (all_center[2] - all_size[2]/2)) / voxel_spacing[2]
    ]
    
    # 將ROI大小從物理單位轉換為體素數
    roi_size_voxel = [
        roi_size[0] / voxel_spacing[0],
        roi_size[1] / voxel_spacing[1],
        roi_size[2] / voxel_spacing[2]
    ]
    
    # 轉換為YOLO格式的相對座標(0-1之間)
    x_center = roi_center_voxel[0] / img_shape[0]
    y_center = roi_center_voxel[1] / img_shape[1]
    z_center = roi_center_voxel[2] / img_shape[2]
    
    width = roi_size_voxel[0] / img_shape[0]
    height = roi_size_voxel[1] / img_shape[1]
    depth = roi_size_voxel[2] / img_shape[2]
    
    # class設為0 (假設只有一個類別)
    class_id = 0
    
    print(validate_conversion(nii_path, f"{class_id} {x_center} {y_center} {z_center} {width} {height} {depth}", img_shape))
    
    return f"{class_id} {z_center} {x_center} {y_center} {depth} {width} {height}"

if __name__ == "__main__":
    # 輸入

    pathdir = ""

    # 讀取 json 檔案
    with open(pathdir + "ROI.json", "r") as f1, open(pathdir + "all_ROI.json", "r") as f2:
        roi_data = json.load(f1)["markups"][0]
        all_roi_data = json.load(f2)["markups"][0]

    # 擷取數據
    roi_center = roi_data["center"]
    roi_size = roi_data["size"]
    all_center = all_roi_data["center"]
    all_size = all_roi_data["size"]

    label = convert_to_yolo_format(roi_center, roi_size, all_center, all_size)

    # 列印結果
    print("Generated Label:", label)

    # 將標籤保存到 txt 檔案
    output_txt_path =  pathdir + "ROI.txt"
    with open(output_txt_path, "w") as f:
        f.write(" ".join(map(str, label)) + "\n")

        
