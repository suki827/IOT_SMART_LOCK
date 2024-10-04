import time

import cv2
import os
import face_recognition

def open_camera():
    # 尝试打开摄像头
    cap = cv2.VideoCapture(0)

    # 检查摄像头是否成功打开，如果没有，则等待
    retry_count = 0
    max_retries = 10  # 最多重试次数

    while not cap.isOpened() and retry_count < max_retries:
        print("Waiting for the camera to initialize...")
        time.sleep(1)  # 等待1秒再重试
        cap = cv2.VideoCapture(0)
        retry_count += 1

    if not cap.isOpened():
        print("Unable to open the camera after several attempts.")
        return False, None

    print("Camera successfully initialized.")
    return True, cap


def capture_image(user_id):
    # Create a directory to store user images
    IMAGE_DIR = "registered_users"
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
    """
    Capture the user's image and save it to the IMAGE_DIR directory with the filename user_id.jpg
    :param user_id: Unique ID of the user
    """


    # print("Press 's' to capture and save the photo, press 'q' to quit")

    success, cap = open_camera()

    if success:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Unable to read frame")


            # cv2.imshow('Capture Image', frame)
            key = input("Press 'S' to capture the face and verify, or 'Q' to quit: ").lower()

            # key = cv2.waitKey(1) & 0xFF
            if key == 's':  # Press 's' to capture
                image_path = os.path.join(IMAGE_DIR, f"{user_id}.jpg")
                cv2.imwrite(image_path, frame)
                print(f"Image saved to {image_path}")
                cap.release()
            elif key == ord('q'):  # Press 'q' to quit
                exit(0)

        return True







# def verify_face(user_id, image_path,frame):
#     """
#     Capture the current user's face from the camera and verify it against the registered user ID.
#     :param user_id: Unique ID of the user
#     :return: Returns True or False indicating the verification result
#     """
#     res = False
#     registered_image_path = image_path
#
#     if not os.path.exists(registered_image_path):
#         print(f"Cannot find registered image for user {user_id}")
#         return False
#     # Load the registered image and extract its encoding
#     registered_image = face_recognition.load_image_file(registered_image_path)
#     registered_encoding = face_recognition.face_encodings(registered_image)
#
#     if len(registered_encoding) == 0:
#         print("No face detected in the registered image")
#         return False
#     registered_encoding = registered_encoding[0]
#
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#
#     # Detect face locations in the frame
#     face_locations = face_recognition.face_locations(rgb_frame)
#
#     # If at least one face is found, attempt to verify
#     if len(face_locations) > 0:
#         # Encode the face(s) in the current frame
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
#
#         # Compare the first face encoding found with the registered encoding
#         current_encoding = face_encodings[0]
#         results = face_recognition.compare_faces([registered_encoding], current_encoding)
#         # 计算两张人脸之间的距离
#         face_distance = face_recognition.face_distance([registered_encoding], current_encoding)[0]
#
#         # 打印距离和相似度判断
#         print(f"Face distance: {face_distance}")
#         if results[0]:
#             print("Verification successful! Faces match!")
#             # cv2.destroyAllWindows()
#             res = True
#
#         else:
#             print("Verification failed! Faces do not match!")
#     else:
#         print("No face detected. Please try again.")
#
#     return res


import os
import cv2
import face_recognition

def verify_face(user_id, image_path, verify_frame, scale_percent=0.25):

    res = False
    registered_image_path = image_path

    # 检查注册的用户图像是否存在
    if not os.path.exists(registered_image_path):
        print(f"Cannot find registered image for user {user_id}")
        return False

    if not os.path.exists(verify_frame):
        print(f"Cannot find verify_frame image for user {user_id}")
        return False
    original_image = face_recognition.load_image_file(image_path)  # 替换为第一张图片的路径
    face_encodings_original = face_recognition.face_encodings(original_image)

    # 加载第二张图片，并获取人脸编码
    image_verify = face_recognition.load_image_file(verify_frame)  # 替换为第二张图片的路径
    face_encodings_verify = face_recognition.face_encodings(image_verify)
    if len(face_encodings_original) > 0 and len(face_encodings_verify) > 0:
        # 提取两张图片中的第一个人脸编码
        face_encoding_o = face_encodings_original[0]
        face_encoding_v = face_encodings_verify[0]

        # 使用 compare_faces 比较两个人脸编码，返回布尔值列表
        results = face_recognition.compare_faces([face_encoding_o], face_encoding_v)

        if results[0]:
            print("Verification successful! Faces match!")
            res = True
        else:
            print("Verification failed! Faces do not match!")
    return res








# Wrapper function for easy use
def main():
    while True:
        print("\n1. Register User")
        print("2. Face Verification")
        print("3. Exit")
        choice = input("Please choose an option:")
        if choice == '1':
            user_id = input("Enter User ID: ")
            capture_image(user_id)
        elif choice == '2':
            user_id = input("Enter User ID: ")
            if verify_face(user_id):
                print("Face verification passed")
                break
            else:
                print("Face verification failed")
        elif choice == '3':
            break
        else:
            print("Invalid option, please try again")


if __name__ == "__main__":
    main()
