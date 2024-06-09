import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras import layers, models
from sklearn.metrics import confusion_matrix
import seaborn as sns
import pandas as pd
from tensorflow.keras import models, layers
from tensorflow.keras.utils import to_categorical
import idx2numpy


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def get_local_mnist_data():
    # 读取本地的MNIST数据集文件
    train_images_file = 'C:/Users/Even/Desktop/Lu/guidebook/minst/data/train-images.idx3-ubyte'
    train_labels_file = 'C:/Users/Even/Desktop/Lu/guidebook/minst/data/train-labels.idx1-ubyte'
    test_images_file = 'C:/Users/Even/Desktop/Lu/guidebook/minst/data/t10k-images.idx3-ubyte'
    test_labels_file = 'C:/Users/Even/Desktop/Lu/guidebook/minst/data/t10k-labels.idx1-ubyte'

    # 使用idx2numpy读取数据集文件
    x_train_original = idx2numpy.convert_from_file(train_images_file)
    y_train_original = idx2numpy.convert_from_file(train_labels_file)
    x_test_original = idx2numpy.convert_from_file(test_images_file)
    y_test_original = idx2numpy.convert_from_file(test_labels_file)

    # 从训练集中分配验证集
    x_val = x_train_original[55000:]
    y_val = y_train_original[55000:]
    x_train = x_train_original[:55000]
    y_train = y_train_original[:55000]

    # 将图像转换为三维矩阵(nums, timesteps, features)，这里将图像的28*28像素视为28个时间步长和28个特征
    x_train_lstm = x_train.reshape(x_train.shape[0], 28, 28).astype('float32')
    x_val_lstm = x_val.reshape(x_val.shape[0], 28, 28).astype('float32')
    x_test_lstm = x_test_original.reshape(x_test_original.shape[0], 28, 28).astype('float32')

    # 原始图像的像素灰度值为0-255，为了提高模型的训练精度，通常将数值归一化映射到0-1。
    x_train_lstm /= 255
    x_val_lstm /= 255
    x_test_lstm /= 255

    # 图像标签一共有10个类别即0-9，这里将其转化为独热编码（One-hot）向量
    y_train = to_categorical(y_train, 10)
    y_val = to_categorical(y_val, 10)
    y_test = to_categorical(y_test_original, 10)

    return x_train_lstm, y_train, x_val_lstm, y_val, x_test_lstm, y_test

# 调用函数获取本地数据集
x_train_lstm, y_train, x_val_lstm, y_val, x_test_lstm, y_test = get_local_mnist_data()

# 建立神经网络模型
model = Sequential()
model.add(LSTM(128, input_shape=(28, 28)))  # 一个具有128个单元的LSTM层
model.add(Dense(10, activation='softmax'))  # 具有10个类别的输出层

# 编译模型
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# 训练模型
train_history = model.fit(x_train_lstm, y_train, epochs=20, batch_size=32, validation_data=(x_val_lstm, y_val))

model.save('lstm_train')

# 评估模型
test_loss, test_accuracy = model.evaluate(x_test_lstm, y_test)
print(f'Test loss: {test_loss}, Test accuracy: {test_accuracy}')




# 定义训练过程可视化函数
def show_train_history(train_history, train, validation):
    plt.plot(train_history.history[train])
    plt.plot(train_history.history[validation])
    plt.title('Train History')
    plt.ylabel(train)
    plt.xlabel('Epoch')
    plt.legend(['train', 'validation'], loc='best')
    plt.show()

# 定义可视化预测结果函数
def mnist_visualize_multiple_predict(start, end, length, width, predictions, true_labels):
    (x_train_original, y_train_original), (x_test_original, y_test_original) = tf.keras.datasets.mnist.load_data()

    for i in range(start, end):
        plt.subplot(length, width, 1 + i)
        plt.imshow(x_test_original[i], cmap=plt.get_cmap('gray'))
        title_true = 'true=' + str(true_labels[i])
        title_prediction = ', prediction=' + str(predictions[i])
        title = title_true + title_prediction
        plt.title(title)
        plt.xticks([])
        plt.yticks([])
    plt.show()


# 可视化训练历史
show_train_history(train_history, 'accuracy', 'val_accuracy')
show_train_history(train_history, 'loss', 'val_loss')

# 输出网络在测试集上的损失与精度
score = model.evaluate(x_test_lstm, y_test)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

# 测试集结果预测
predictions = model.predict(x_test_lstm)
predictions = np.argmax(predictions, axis=1)
true_labels = np.argmax(y_test, axis=1)
print('前20张图片预测结果：', predictions[:20])

# 预测结果图像可视化
mnist_visualize_multiple_predict(start=0, end=9, length=3, width=3, predictions=predictions, true_labels=true_labels)

# 混淆矩阵
cm = confusion_matrix(true_labels, predictions)
cm = pd.DataFrame(cm)
class_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def plot_confusion_matrix(cm):
    plt.figure(figsize=(10, 10))
    sns.heatmap(cm, cmap='Oranges', linecolor='black', linewidth=1, annot=True, fmt='', xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.show()

plot_confusion_matrix(cm)