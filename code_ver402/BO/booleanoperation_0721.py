from OCC.Extend.DataExchange import read_step_file
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Common
import os
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB, Quantity_NOC_WHITE
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

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import traceback
import psutil

class Boolean:
    def __init__(self):
        self.lst = ["[1,1,1]","[1,1,-1]","[1,-1,1]","[-1,1,1]","[1,-1,-1]","[-1,1,-1]","[-1,-1,1]","[-1,-1,-1]","[1,0,0]","[-1,0,0]","[0,1,0]","[0,-1,0]","[0,0,1]","[0,0,-1]"]
        self.pose = [V3d_XposYposZpos, V3d_XposYposZneg, V3d_XposYnegZpos, V3d_XnegYposZpos,
                     V3d_XposYnegZneg, V3d_XnegYposZneg, V3d_XnegYnegZpos, V3d_XnegYnegZneg,
                     V3d_Xpos, V3d_Xneg, V3d_Ypos, V3d_Yneg, V3d_Zpos, V3d_Zneg]
        self.intersection_color = Quantity_Color(0, 0, 0, Quantity_TOC_RGB)
        self.student_color = Quantity_Color(0, 0, 0.55, Quantity_TOC_RGB)
        self.modelanswer_color = Quantity_Color(1, 0.56, 0.02, Quantity_TOC_RGB)

    def boolean_cap(self, T_stp_file, stp_file_list, feedback_path, file_name):
        # if file_name == "hw2_s3":
        #     logging.info(f"Processing file: {file_name}")
            
        try:
            # STEP 파일 읽기
            logging.info(f"Reading STEP files: {T_stp_file}, {stp_file_list}")
            shape1 = read_step_file(T_stp_file)
            shape2 = read_step_file(stp_file_list)
            logging.info("STEP files read successfully")

            logging.info("Starting Boolean operations")
            common_builder = BRepAlgoAPI_Common(shape1, shape2)
            common_builder.Build()
            intersection_shape = common_builder.Shape()  
            cut_result = BRepAlgoAPI_Cut(shape2, shape1)
            cut_result.Build()
            shape3 = cut_result.Shape()
            cut_result2 = BRepAlgoAPI_Cut(shape1, shape2)
            cut_result2.Build()
            shape4 = cut_result2.Shape()
            logging.info("Boolean operations completed")
            
            for k, (lst_item, pose_item) in enumerate(zip(self.lst, self.pose)):
                logging.info(f"Processing viewpoint {k+1}/{len(self.lst)}: {lst_item}")
                try:
                    # 시각화 초기화
                    logging.info("Initializing display")
                    display, start_display, add_menu, add_function = init_display()
                    display.EraseAll()
                    display.default_drawer.SetFaceBoundaryDraw(False)

                    if intersection_shape is not None:
                        display.DisplayShape(intersection_shape, color=self.intersection_color, transparency=0.15, update=True)
                    if shape3 is not None:
                        display.DisplayShape(shape3, color=self.student_color, transparency=0.2, update=True)
                    if shape4 is not None:
                        display.DisplayShape(shape4, color=self.modelanswer_color, transparency=0.2, update=True)

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
                    if os.path.exists(image_path):
                        logging.info(f"Image saved: {image_path}")
                    else:
                        logging.warning(f"Failed to save image: {image_path}")
                except Exception as e:
                    logging.error(f"Error processing viewpoint {lst_item}: {str(e)}")
                    logging.error(traceback.format_exc())

            logging.info(f"Memory usage: {psutil.virtual_memory().percent}%")
            logging.info(f"CPU usage: {psutil.cpu_percent()}%")

        except Exception as e:
            logging.error(f"Error processing {file_name}: {str(e)}")
            logging.error(traceback.format_exc())

# 메인 코드 부분
if __name__ == "__main__":
    try:
        a = Boolean()
        feedback_path = r'code_ver4.0.0\paper_testcase\hw2\BO'
        T_stp_file = r'code_ver4.0.0\paper_testcase\answer\stp\hw2_answer.stp'
        stp_file_directory = r'code_ver4.0.0\paper_testcase\hw2\stp'

        stp_files = [f for f in os.listdir(stp_file_directory) if f.endswith('.stp') and f != os.path.basename(T_stp_file)]

        for stp_file in stp_files:
            stp_file_path = os.path.join(stp_file_directory, stp_file)
            file_name = os.path.splitext(stp_file)[0]
            logging.info(f"Processing {stp_file}...")
            a.boolean_cap(T_stp_file, stp_file_path, feedback_path, file_name)

    except Exception as e:
        logging.error(f"Unhandled exception in main: {str(e)}")
        logging.error(traceback.format_exc())