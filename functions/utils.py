import tensorflow as tf


# 定义 MobileNet V2 模型架构
model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),  # 输入图像的大小
    alpha=1.0,                  # 控制模型的复杂度，默认值为1.0
    include_top=False,          # 如果你只加载权重，则可能不需要全连接层（no_top 版本）
    weights=None,               # 初始化模型，但不加载任何权重
)

# 加载预训练权重
model.load_weights('/Users/huanyan/PycharmProjects/IOT/IOT/functions/mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_224_no_top.h5')


# 加载已有的 Keras .h5 模型
# model = tf.keras.models.load_model('/Users/huanyan/PycharmProjects/IOT/IOT/functions/mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_224_no_top.h5')

# 创建 TensorFlow Lite 转换器
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# 启用优化选项
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# 转换为 TensorFlow Lite 模型
tflite_model = converter.convert()

# 将转换后的优化模型保存为 .tflite 文件
with open('optimized_model.tflite', 'wb') as f:
    f.write(tflite_model)

print("Optimized model converted and saved as optimized_model.tflite")
