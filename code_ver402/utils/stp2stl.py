
# code_ver4.0.0/paper_testcase/hw2 폴더 경로의
# hw2_s1에서 hw2_s13까지의 stp 파일도 읽어와서
# stl 파일로 변환하여 code_ver4.0.0/paper_testcase/hw2 폴더에 저장한다.

# stp -> stl
from OCC.Extend.DataExchange import read_step_file
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.StlAPI import StlAPI_Writer
import os

# code_ver4.0.0/paper_testcase/hw1 폴더 경로의
# hw1_s1에서 hw1_s15까지의 stp 파일을 읽어와서
# stl 파일로 변환하여 code_ver4.0.0/paper_testcase/hw1 폴더에 저장하고

stl_writer = StlAPI_Writer()
stl_writer.SetASCIIMode(True)  # Set to False if you want a binary STL

stp_path = os.path.join(os.getcwd(), "code_ver4.0.0/paper_testcase/hw1/stp/a")
stl_path = os.path.join(os.getcwd(), "code_ver4.0.0/paper_testcase/hw1/stp/a")
stp_file_list = []

for file in os.listdir(stp_path):
    if file.endswith(".stp"):
        stp_file_list.append(file)

for stp_file in stp_file_list:
    file_name = stp_file.split(".")[0]
    stp_file_path = stp_path + f"/{file_name}.stp"
    stl_file_path = stl_path + f"/{file_name}.stl"

    shp = read_step_file(stp_file_path)
    mesh = BRepMesh_IncrementalMesh(shp, 0.1)
    mesh.Perform()
    stl_writer.Write(shp, stl_file_path)





            
# stl --> CD/EMD/PMD/Hausdorff distance/AAD

# stp --> 볼륨/BB수치/3DL/2DL

# 구속조건 점수 불러와서 100 - 현재 json 점수 = 구속조건 점수