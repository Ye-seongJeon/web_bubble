import os
import sys
from OCC.Extend.DataExchange import read_step_file
import open3d as o3d
import math

import os
from OCC.Core.BRepGProp import brepgprop_VolumeProperties
from OCC.Core.GProp import GProp_GProps
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add

from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pln, gp_Pnt, gp_Dir
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_WHITE
import os

import cv2
import numpy as np

import json

MAX_FEATURES = 1000
RATIO_THRESHOLD = 0.8

def measure_shape_volume(shape):
    """Returns shape volume"""
    inertia_props = GProp_GProps()
    brepgprop_VolumeProperties(shape, inertia_props)
    mass = inertia_props.Mass()
    return round(mass)

def measure_bnd_box(shape):
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox) # shape에 bbox 추가
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    x_length = xmax - xmin
    x_length = round(x_length)
    y_length = ymax - ymin
    y_length = round(y_length)
    z_length = zmax - zmin
    z_length = round(z_length)
    return x_length, y_length, z_length

def grading_volume(answer_volume, student_volume):
    # 2배 초과 = 0점
    if (student_volume/answer_volume > 2 or student_volume == 0):
        score = 0

    # 0~1배 (작을 경우)
    elif (student_volume/answer_volume < 1):
        score = 100*(student_volume/answer_volume)
    
    # 1~2배 (클 경우)
    else:
        score = -100*(student_volume/answer_volume) + 200

    return round(score, 2)
    
def grading_bb(answer_bb, student_bb):
    BndScores = 0
    for i in range(3):
        # 2배 초과 = 0점
        if (student_bb[i]/answer_bb[i] > 2):
            BndScores += 0
        # 0~1배 (작을 경우)
        elif (student_bb[i]/answer_bb[i] <= 1):
            BndScores += 33.3*(student_bb[i]/answer_bb[i])
        # 1~2배 (클 경우)
        else:
            BndScores += -33.3*(student_bb[i]/answer_bb[i]) + 66.6
    BndScores = round(BndScores, 2)
    if BndScores == 99.9:
        BndScores = 100
 
    return round(BndScores, 2)

def cap_3d(shp, save_dir):
    display, start_display, add_menu, add_function_to_menu = init_display()
    views = [
        ("111", (1, 1, 1)), ("11-1", (1, 1, -1)), ("1-11", (1, -1, 1)), ("-111", (-1, 1, 1)),
        ("1-1-1", (1, -1, -1)), ("-11-1", (-1, 1, -1)), ("-1-11", (-1, -1, 1)), ("-1-1-1", (-1, -1, -1)),
        ("100", (1, 0, 0)), ("-100", (-1, 0, 0)), ("010", (0, 1, 0)), ("0-10", (0, -1, 0)),
        ("001", (0, 0, 1)), ("00-1", (0, 0, -1))
    ]
    
    for name, direction in views:
        display.EraseAll()
        display.DisplayShape(shp, color="BLACK", transparency=0.5)
        display.View.SetProj(*direction)
        display.hide_triedron()
        display.FitAll()
        display.View.SetBgGradientColors(
            Quantity_Color(Quantity_NOC_WHITE),
            Quantity_Color(Quantity_NOC_WHITE),
            2, True
        )
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        display.View.Dump(os.path.join(save_dir, f"view_{name}.png"))
    
    display.EraseAll()

def cap_2d(shp, n, save_dir):
    display, start_display, add_menu, add_function_to_menu = init_display()
    
    # 바운딩 박스 계산
    bbox = Bnd_Box()
    bbox.SetGap(0)
    brepbndlib_Add(shp, bbox)
    XMin, YMin, ZMin, XMax, YMax, ZMax = bbox.Get()
    
    for axis in ['x', 'y', 'z']:
        for i in range(1, n):
            if axis == 'x':
                pnt = gp_Pnt(XMin + ((XMax-XMin)/n) * i, 0, 0)
                direction = gp_Dir(1, 0, 0)
            elif axis == 'y':
                pnt = gp_Pnt(0, YMin + ((YMax-YMin)/n) * i, 0)
                direction = gp_Dir(0, 1, 0)
            else:  # z
                pnt = gp_Pnt(0, 0, ZMin + ((ZMax-ZMin)/n) * i)
                direction = gp_Dir(0, 0, 1)
            
            # 평면 생성 및 단면 계산
            plane = gp_Pln(pnt, direction)
            face = BRepBuilderAPI_MakeFace(plane).Shape()
            section = BRepAlgoAPI_Section(shp, face).Shape()
            
            # 디스플레이 설정
            display.EraseAll()
            display.hide_triedron()
            display.View.SetBgGradientColors(                     
                Quantity_Color(Quantity_NOC_WHITE),
                Quantity_Color(Quantity_NOC_WHITE),
                2,
                True,
            )
            display.DisplayShape(section, color="BLACK", update=True)
            display.FitAll()
            
            # 뷰 설정
            if axis == 'x':
                display.View_Right()
            elif axis == 'y':
                display.View_Front()
            else:
                display.View_Top()
            
            # 이미지 저장
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            file_path = os.path.join(save_dir, f"section_{axis}_{i}.png")
            display.View.Dump(file_path)
    
    display.EraseAll()

def match_images_with_distance(img1_path, img2_path):
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    
    if img1 is None or img2 is None:
        print(f"Error: Unable to read one or both images.")
        print(f"Image 1 path: {img1_path}")
        print(f"Image 2 path: {img2_path}")
        return 0, 0
    
    orb = cv2.ORB_create(MAX_FEATURES)
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    
    if des1 is None or des2 is None:
        print(f"Warning: No descriptors found in one or both images.")
        return 0, 0
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    matches = bf.knnMatch(des1, des2, k=2)
    
    good_matches = []
    for match in matches:
        if len(match) == 2:
            m, n = match
            if m.distance < RATIO_THRESHOLD * n.distance:
                good_matches.append(m)
    
    return len(matches), len(good_matches)

def calculate_image_score(num_matches, num_good_matches):
    if num_matches == 0:
        return 0
    
    score = 100 * (num_good_matches / num_matches)
    return round(score, 2)

def match_and_score_images(answer_dir, student_dir, image_type):
    scores = []
    
    if image_type == '3d':
        views = ["111", "11-1", "1-11", "-111", "1-1-1", "-11-1", "-1-11", "-1-1-1", 
                 "100", "-100", "010", "0-10", "001", "00-1"]
        file_pattern = "view_{}.png"
    else:  # 2d
        views = ['x', 'y', 'z']
        file_pattern = "section_{}_{}.png"
    
    for view in views:
        i = 1 if image_type == '2d' else 0
        while True:
            if image_type == '2d':
                answer_img = os.path.join(answer_dir, file_pattern.format(view, i))
                student_img = os.path.join(student_dir, file_pattern.format(view, i))
            else:
                answer_img = os.path.join(answer_dir, file_pattern.format(view))
                student_img = os.path.join(student_dir, file_pattern.format(view))
            
            if not (os.path.exists(answer_img) and os.path.exists(student_img)):
                break
            
            num_matches, num_good_matches = match_images_with_distance(answer_img, student_img)
            score = calculate_image_score(num_matches, num_good_matches)
            scores.append(score)
            
            if image_type == '3d':
                break
            i += 1
    
    return round(sum(scores) / len(scores), 2) if scores else 0

def save_json(results, RESULT_PATH):
    os.makedirs(RESULT_PATH, exist_ok=True)
    with open(os.path.join(RESULT_PATH, "results.json"), "w", encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # 환경변수에서 읽어오기
    student_file_path = os.environ.get("STUDENT_FILE_PATH")
    answer_file_path = os.environ.get("ANSWER_FILE_PATH")
    student_id = os.environ.get("STUDENT_ID", "unknown")
    assignment_id = os.environ.get("ASSIGNMENT_ID", "unknown")
    result_path = os.environ.get("RESULT_PATH")

    print("=== CAD 분석 시작 ===")
    print(f"학생 파일: {student_file_path}")
    print(f"정답 파일: {answer_file_path}")
    print(f"학생 ID: {student_id}")
    print(f"과제 ID: {assignment_id}")

    # 1) 학생 파일이 없을 때
    if not os.path.exists(student_file_path):
        error_result = {
            "success": False,
            "error": "학생 파일이 존재하지 않습니다.",
            "error_code": "STUDENT_FILE_NOT_FOUND",
            "student_id": student_id,
            "assignment_id": assignment_id
        }
        print("=== ANALYSIS_RESULT_START ===")
        print(json.dumps(error_result, ensure_ascii=False))
        print("=== ANALYSIS_RESULT_END ===")
        sys.exit(1)

    try:
        # 2) 학생 파일로 분석
        student_stp = read_step_file(student_file_path)
        volume = measure_shape_volume(student_stp)
        bb = measure_bnd_box(student_stp)

        results = {
            "success": True,
            "student_id": student_id,
            "assignment_id": assignment_id,
            "student_analysis": {
                "volume": volume,
                "bounding_box": bb
            }
        }

        # 3) 정답 파일이 있으면 비교 분석
        if answer_file_path and os.path.exists(answer_file_path):
            ans_stp = read_step_file(answer_file_path)
            answer_volume = measure_shape_volume(ans_stp)
            answer_bb = measure_bnd_box(ans_stp)

            volume_score = grading_volume(answer_volume, volume)
            bb_score = grading_bb(answer_bb, bb)

            # 이미지 3D/2D 비교 (선택사항)
            try:
                import tempfile
                with tempfile.TemporaryDirectory() as temp_dir:
                    ans_3d_path = os.path.join(temp_dir, "answer_3d")
                    ans_2d_path = os.path.join(temp_dir, "answer_2d")
                    student_3d_path = os.path.join(temp_dir, "student_3d")
                    student_2d_path = os.path.join(temp_dir, "student_2d")

                    cap_3d(ans_stp, ans_3d_path)
                    cap_3d(student_stp, student_3d_path)
                    score_3d = match_and_score_images(ans_3d_path, student_3d_path, '3d')

                    cap_2d(ans_stp, 10, ans_2d_path)
                    cap_2d(student_stp, 10, student_2d_path)
                    score_2d = match_and_score_images(ans_2d_path, student_2d_path, '2d')
            except Exception as e:
                print(f"이미지 분석 중 오류: {e}")
                score_3d = 0
                score_2d = 0

            results["answer_analysis"] = {
                "volume": answer_volume,
                "bounding_box": answer_bb
            }
            results["comparison_scores"] = {
                "volume_score": volume_score,
                "bounding_box_score": bb_score,
                "3d_similarity_score": score_3d,
                "2d_similarity_score": score_2d,
                "total_score": round((volume_score + bb_score + score_3d + score_2d) / 4, 2)
            }
        else:
            results["warning"] = "정답 파일이 제공되지 않아 비교 분석 없이 학생 분석만 수행했습니다."

        # 4) 결과를 파일로 저장
        if result_path:
            os.makedirs(result_path, exist_ok=True)
            with open(os.path.join(result_path, "results.json"), 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

        # 5) 최종 JSON 출력 (Bubble이 파싱)
        print("=== ANALYSIS_RESULT_START ===")
        print(json.dumps(results, ensure_ascii=False))
        print("=== ANALYSIS_RESULT_END ===")

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "error_code": "ANALYSIS_ERROR",
            "student_id": student_id,
            "assignment_id": assignment_id
        }
        print("=== ANALYSIS_RESULT_START ===")
        print(json.dumps(error_result, ensure_ascii=False))
        print("=== ANALYSIS_RESULT_END ===")
        sys.exit(1)


