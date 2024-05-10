import pandas as pd
import os

# ที่อยู่โฟลเดอร์ที่มีไฟล์ที่แยกออกมาแล้ว
folder = '/Users/pingpongges/Desktop/โปรเจคจบ/Code-new/Data_copy(100)'

# รายชื่อไฟล์ CSV ในโฟลเดอร์
data_files_path = sorted([os.path.join(folder, file) for file in os.listdir(folder) if file.endswith('.csv')])

# โหลดแต่ละไฟล์ CSV เข้าสู่ DataFrame และเก็บไว้ใน dictionary
dataframes = {file.split('/')[-1]: pd.read_csv(file) for file in data_files_path}

# สร้างสถิติเบื้องต้นสำหรับแต่ละ DataFrame และเก็บไว้ใน dictionary
data_info = {name: df.describe().round(2) for name, df in dataframes.items()}

# แสดงสถิติเบื้องต้น
for name, info in data_info.items():
    print(f"สถิติของ {name}:")
    print(info)
    print("\n")
