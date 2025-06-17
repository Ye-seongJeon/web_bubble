import cv2

MAX_FEATURES = 1000
RATIO_THRESHOLD = 0.8  # Lowe의 논문에서 제안된 값

def match_images(img1_path, img2_path, output_path):
    # 이미지 읽기
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        print(f"Error: Unable to read one or both images.")
        print(f"Image 1 path: {img1_path}")
        print(f"Image 2 path: {img2_path}")
        return

    # 그레이스케일로 변환
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # ORB 디텍터 생성
    orb = cv2.ORB_create(MAX_FEATURES)

    # 키포인트와 디스크립터 찾기
    kp1, des1 = orb.detectAndCompute(img1_gray, None)
    kp2, des2 = orb.detectAndCompute(img2_gray, None)

    # BFMatcher 객체 생성 (crossCheck=False로 설정)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    # knnMatch를 사용하여 각 특징점에 대해 2개의 가장 가까운 매칭 찾기
    matches = bf.knnMatch(des1, des2, k=2)

    # 비율 테스트를 적용하여 좋은 매칭 선택
    good_matches = []
    for m, n in matches:
        if m.distance < RATIO_THRESHOLD * n.distance:
            good_matches.append(m)

    # 매칭 결과 그리기
    img3 = cv2.drawMatches(img1, kp1, img2, kp2, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    # 결과 이미지 저장
    cv2.imwrite(output_path, img3)

    print(f"매칭 결과가 {output_path}에 저장되었습니다.")
    print(f"총 매칭 수: {len(matches)}")
    print(f"비율 테스트 후 좋은 매칭 수: {len(good_matches)}")

# 사용 예
img1_path = r"D:\GitHub\3D-CAD-Automatic-Grading-system\code_ver4.0.0\paper_testcase\answer\stp\3DL\view_1-1-1.png"
img2_path = r"D:\GitHub\3D-CAD-Automatic-Grading-system\code_ver4.0.0\paper_testcase\hw1\stp\3DL\hw1_s1\view_1-1-1.png"
output_path = r"D:\GitHub\3D-CAD-Automatic-Grading-system\code_ver4.0.0\paper_testcase\results\matched_image_ratio_test.png"

match_images(img1_path, img2_path, output_path)