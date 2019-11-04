import numpy as np
import os
from PIL import Image
import matplotlib
import paddle
import paddle.fluid as fluid
from __future__ import print_function
try:
    from paddle.fluid.contrib.trainer import *
    from paddle.fluid.contrib.inferencer import *
except ImportError:
    print(
        "In the fluid 1.0, the trainer and inferencer are moving to paddle.fluid.contrib",
        file=sys.stderr)
    from paddle.fluid.trainer import *
    from paddle.fluid.inferencer import *
matplotlib.use('Agg')
%matplotlib inline

#softmax分类器
def softmax_regression():
    img = fluid.layers.data(name='img', shape =[1,28,28],dtype = 'float32')
    predict= fluid.layers.fc(input=hidden, size=10, act='softmax')
    return predict

#多层感知机
def multilayer_perceptron():
    img = fluid.layers.data(name='img', shape=[1, 28, 28], dtype='float32')
    h1 = fluid.layers.fc(input=x, size=128, act='ReLU')
    h2 = fluid.layers.fc(input=h1, size=64, act='ReLU')
    predict = fluid.layers.fc(input=h2, size=10, act='Softmax')
    return predict
#卷积神经网络
def convolutional_neural_network():
    img = fluid.layers.data(name='img', shape =[1,28,28],dtype = 'float32')
    h1=fluid.layers.fc(input=img, size=20, act='ReLU')
    h2=fluid.layers.fc(input=h1, size=50, act='ReLU')
    predict=fluid.layers.fc(input=h2, size=10, act='ReLU')
    return predict
# 设置训练场所
use_cuda = False
# use_cuda = True
place = fluid.CUDAPlace(1) if use_cuda else fluid.CPUPlace()
#训练
def train_func():
    predict = multilayer_perceptron()
    cost = fluid.layers.cross_entropy(input=predict, label=label)
    avg_cost = fluid.layers.mean(cost)
    return avg_cost
#定义optimizer
def optimizer_func():
    optimizer=fluid.optimizer.Momentum(learning_rate=0.0004,momentum=0.9)
    return optimizer
feed_order = ['img', 'label']
params_dirname = "./CNN_model"
from paddle.v2.plot import Ploter
train_title = "Train cost"
test_title = "Test cost"
plot_cost = Ploter(train_title, test_title)

step = 0
# 事件处理
def event_handler_plot(event):
    global step
    if isinstance(event, EndStepEvent):
        if event.step % 2 == 0: # 若干个batch,记录cost
            if event.metrics[0] < 10:
                plot_cost.append(train_title, step, event.metrics[0])
        if event.step % 20 == 0: # 若干个batch,记录cost
            test_metrics = trainer.test(
            reader=test_reader, feed_order=feed_order)
            if test_metrics[0] < 10:
                plot_cost.append(test_title, step, test_metrics[0])
        # 将参数存储，用于预测使用
        if params_dirname is not None:
            trainer.save_params(params_dirname)
    step += 1
# 设置 BATCH_SIZE 的大小
BATCH_SIZE = 128
# 设置训练reader
train_reader = paddle.batch(
    paddle.reader.shuffle(
        paddle.dataset.mnist.train(),
        buf_size=500),
    batch_size=BATCH_SIZE)

#设置测试 reader
test_reader = paddle.batch(
    paddle.reader.shuffle(
        paddle.dataset.mnist.test(),
        buf_size=500),
    batch_size=BATCH_SIZE)

#创建训练器
trainer = Trainer(
    train_func= train_func,
    place= place,
    optimizer_func= optimizer_func)
trainer.train(
    reader=train_reader,
    num_epochs=3,
    event_handler=event_handler_plot,
    feed_order=feed_order)
#加载图片
def load_image(file):
    im = Image.open(file).convert('L')
    im = im.resize((28, 28), Image.ANTIALIAS)
    im = np.array(im).reshape(1, 1, 28, 28).astype(np.float32)
    im = im / 255.0 * 2.0 - 1.0
    return im

# 读取并预处理要预测的图片
cur_dir = os.getcwd()
img = load_image(cur_dir + '/image/infer_3.png')

# 设置训练场所
use_cuda = False
# use_cuda = True
place = fluid.CUDAPlace(1) if use_cuda else fluid.CPUPlace()

inferencer = Inferencer(
    infer_func=softmax_regression, # uncomment for softmax regression
#     infer_func=multilayer_perceptron, # uncomment for MLP
#     infer_func=convolutional_neural_network,  # uncomment for LeNet5
    param_path=params_dirname,place=place )

results = inferencer.infer({'img': img})
lab = np.argsort(results)  # probs and lab are the results of one batch data
print( "Label of image/infer_3.png is: %d" % lab[0][0][-1] )