import os
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.BRepGProp import brepgprop_VolumeProperties
from OCC.Core.GProp import GProp_GProps
from OCC.Display.SimpleGui import init_display
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.AIS import AIS_Shape
from OCC.Core.gp import gp_Pnt
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox

def read_step_file(filename):
    reader = STEPControl_Reader()
    status = reader.ReadFile(filename)
    if status == IFSelect_RetDone:
        reader.TransferRoot()
        return reader.Shape()
    else:
        raise Exception("Failed to read STEP file")

def measure_bnd_box(shape):
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    x_length = round(xmax - xmin, 2)
    y_length = round(ymax - ymin, 2)
    z_length = round(zmax - zmin, 2)
    return bbox, x_length, y_length, z_length

def display_shape_and_bounding_box(display, shape, bbox, x_length, y_length, z_length):
    display.EraseAll()
    
    # Display original shape
    shape_ais = AIS_Shape(shape)
    shape_ais.SetColor(Quantity_Color(0.1, 0.1, 0.1, Quantity_TOC_RGB))  # 진한 검정색
    shape_ais.SetTransparency(0.3)  # 낮은 투명도
    display.Context.Display(shape_ais, True)
    
    # Create and display bounding box
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    box_shape = BRepPrimAPI_MakeBox(gp_Pnt(xmin, ymin, zmin), gp_Pnt(xmax, ymax, zmax)).Shape()
    box_ais = AIS_Shape(box_shape)
    box_ais.SetColor(Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB))  # 회색
    box_ais.SetTransparency(0.7)  # 높은 투명도
    display.Context.Display(box_ais, True)
    
    # Display dimensions
    center = gp_Pnt((xmin+xmax)/2, (ymin+ymax)/2, (zmin+zmax)/2)
    diagonal = ((xmax-xmin)**2 + (ymax-ymin)**2 + (zmax-zmin)**2)**0.5
    text_height = diagonal * 0.1  # 텍스트 크기를 10배 증가
    
    display.DisplayMessage(gp_Pnt(center.X(), ymax, center.Z()), f"X: {x_length} mm", height=text_height, message_color=(0, 0, 0))  # 검정색
    display.DisplayMessage(gp_Pnt(xmax, center.Y(), center.Z()), f"Y: {y_length} mm", height=text_height, message_color=(0, 0, 0))  # 검정색
    display.DisplayMessage(gp_Pnt(center.X(), center.Y(), zmax), f"Z: {z_length} mm", height=text_height, message_color=(0, 0, 0))  # 검정색
    
    display.FitAll()

def main(step_file_path):
    shape = read_step_file(step_file_path)
    bbox, x_length, y_length, z_length = measure_bnd_box(shape)

    display, start_display, add_menu, add_function_to_menu = init_display()
    display_shape_and_bounding_box(display, shape, bbox, x_length, y_length, z_length)

    print(f"Bounding Box Dimensions:")
    print(f"X: {x_length} mm")
    print(f"Y: {y_length} mm")
    print(f"Z: {z_length} mm")

    start_display()

if __name__ == "__main__":
    step_file_path = r'D:\GitHub\3D-CAD-Automatic-Grading-system\code_ver4.0.0\paper_testcase\answer\stp\hw1_answer.stp'
    main(step_file_path)