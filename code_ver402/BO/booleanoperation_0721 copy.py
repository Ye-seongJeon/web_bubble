from OCC.Extend.DataExchange import read_step_file
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Common
import os
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB, Quantity_NOC_WHITE
from OCC.Core.V3d import (
    V3d_Zpos,
    V3d_Zneg,
    V3d_Xpos,
    V3d_Xneg,
    V3d_Ypos,
    V3d_Yneg,
    V3d_XposYposZpos,
    V3d_XposYnegZneg,
    V3d_XnegYposZneg,
    V3d_XnegYnegZpos,
    V3d_XposYposZneg,
    V3d_XposYnegZpos,
    V3d_XnegYposZpos,
    V3d_XnegYnegZneg,
)

lst = ["[1,1,1]","[1,1,-1]","[1,-1,1]","[-1,1,1]","[1,-1,-1]","[-1,1,-1]","[-1,-1,1]","[-1,-1,-1]","[1,0,0]","[-1,0,0]","[0,1,0]","[0,-1,0]","[0,0,1]","[0,0,-1]"]
pose = [V3d_XposYposZpos, V3d_XposYposZneg, V3d_XposYnegZpos, V3d_XnegYposZpos,
                     V3d_XposYnegZneg, V3d_XnegYposZneg, V3d_XnegYnegZpos, V3d_XnegYnegZneg,
                     V3d_Xpos, V3d_Xneg, V3d_Ypos, V3d_Yneg, V3d_Zpos, V3d_Zneg]
intersection_color = Quantity_Color(0, 0, 0, Quantity_TOC_RGB)
student_color = Quantity_Color(0, 0, 0.55, Quantity_TOC_RGB)
modelanswer_color = Quantity_Color(1, 0.56, 0.02, Quantity_TOC_RGB)

def boolean(shape1, shape2):
    intersection_shape = BRepAlgoAPI_Common(shape1, shape2).Shape()  

    cut_result = BRepAlgoAPI_Cut(shape2, shape1).Shape()  

    cut_result2 = BRepAlgoAPI_Cut(shape1, shape2).Shape()  

    return intersection_shape, cut_result, cut_result2

def display_boolean(feedback_path, file_name, intersection_shape, shape3, shape4):
    
    for k, (lst_item, pose_item) in enumerate(zip(lst, pose)):
        # 시각화 초기화
        display, start_display, add_menu, add_function = init_display()
        display.EraseAll()
        display.default_drawer.SetFaceBoundaryDraw(False)

        if intersection_shape is not None:
            display.DisplayShape(intersection_shape, color=intersection_color, transparency=0.15, update=True)
        if shape3 is not None:
            display.DisplayShape(shape3, color=student_color, transparency=0.2, update=True)
        if shape4 is not None:
            display.DisplayShape(shape4, color=modelanswer_color, transparency=0.2, update=True)

        display.View.SetProj(pose_item)
        display.hide_triedron()
        display.FitAll()
        display.View.SetBgGradientColors(
        Quantity_Color(Quantity_NOC_WHITE),
        Quantity_Color(Quantity_NOC_WHITE),
        2,
        True,
        )

        image_path = os.path.join(feedback_path, f"{file_name}_{lst_item}.png")
        display.View.Dump(image_path)
        print(f"{k}번째 Saved image: {image_path}")


# 메인 코드 부분
if __name__ == "__main__":
    feedback_path = 'code_ver4.0.0\paper_testcase\hw2\BO'
    T_stp_file = r'code_ver4.0.0\paper_testcase\answer\stp\hw2_answer.stp'
    stp_file_directory = 'code_ver4.0.0\paper_testcase\hw2\stp'

    shp1 = read_step_file(T_stp_file)

    stp_files = [f for f in os.listdir(stp_file_directory) if f.endswith('.stp')]

    for stp_file in stp_files:
        stp_file_path = os.path.join(stp_file_directory, stp_file)
        shp2 = read_step_file(stp_file_path)
        inter_shp, shp12, shp21 = boolean(shp1, shp2)


