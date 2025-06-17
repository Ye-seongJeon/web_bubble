import sys
from OCC.Extend.DataExchange import read_step_file, read_stl_file, write_step_file, write_stl_file
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.Quantity import (
    Quantity_Color,
    Quantity_NOC_ALICEBLUE,
    Quantity_NOC_ANTIQUEWHITE,
    Quantity_TOC_RGB,
    Quantity_NOC_WHITE
)
from OCC.Core.Geom import Geom_Curve, Geom_Surface
from OCC.Core.Geom2d import Geom2d_Curve
from OCC.Core.Visualization import Display3d
from OCC.Core.V3d import (
    V3d_ZBUFFER,
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
import os
# 현재 파이썬 파일 경로
FILE_DIR = os.path.dirname(os.path.abspath(__file__))

# student14.stp 파일 경로
STUDENT14_STP = os.path.join(FILE_DIR, 'student14.stp')
# 이미지 저장 폴더 경로
PNG_DIR = os.path.join(FILE_DIR, 'external_png')
display, start_display, add_menu, add_function_to_menu = init_display()
class Cap3D:
    def __init__(self) -> None:
        pass
    def cap(self):
        shp = read_step_file(STUDENT14_STP)
        lst = ["[1,1,1]","[1,1,-1]","[1,-1,1]","[-1,1,1]","[1,-1,-1]","[-1,1,-1]","[-1,-1,1]","[-1,-1,-1]","[1,0,0]","[-1,0,0]","[0,1,0]","[0,-1,0]","[0,0,1]","[0,0,-1]"]
        pose=[V3d_XposYposZpos,V3d_XposYposZneg,V3d_XposYnegZpos,V3d_XnegYposZpos,V3d_XposYnegZneg,V3d_XnegYposZneg,V3d_XnegYnegZpos,V3d_XnegYnegZneg,V3d_Xpos,V3d_Xneg,V3d_Ypos,V3d_Yneg,V3d_Zpos,V3d_Zneg]
        for i in range(len(lst)):
            display.EraseAll()
            display.DisplayShape(shp, color="black",transparency=0.1)
            display.View.SetProj(pose[i])
            display.hide_triedron()
            display.FitAll()
            display.View.SetBgGradientColors(
            Quantity_Color(Quantity_NOC_WHITE),
            Quantity_Color(Quantity_NOC_WHITE),
            2,
            True,
            )
            display.View.Dump(os.path.join(PNG_DIR,"student_{}.png".format(lst[i])))

if __name__ == "__main__":
    a = Cap3D()
    a.cap()