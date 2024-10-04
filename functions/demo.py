# import face_recognition
#
# # 加载第一张图片，并获取人脸编码
# image_1 = face_recognition.load_image_file("/faces/1.jpg")  # 替换为第一张图片的路径
# face_encodings_1 = face_recognition.face_encodings(image_1)
#
# # 加载第二张图片，并获取人脸编码
# image_2 = face_recognition.load_image_file("/verify/1.jpg")  # 替换为第二张图片的路径
# face_encodings_2 = face_recognition.face_encodings(image_2)
#
# # 确保两张图片中至少有一个人脸
# if len(face_encodings_1) > 0 and len(face_encodings_2) > 0:
#     # 提取两张图片中的第一个人脸编码
#     face_encoding_1 = face_encodings_1[0]
#     face_encoding_2 = face_encodings_2[0]
#
#     # 使用 compare_faces 比较两个人脸编码，返回布尔值列表
#     results = face_recognition.compare_faces([face_encoding_1], face_encoding_2)
#
#     if results[0]:
#         print("两张图片中的人脸匹配!")
#     else:
#         print("两张图片中的人脸不匹配!")
# else:
#     print("两张图片中至少有一张没有检测到人脸")









user_map = ['','Nick','Hugo','Honey', 'Habilash']