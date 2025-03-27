# -*- coding: utf-8 -*-




from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from real_time_video_me import Emotion_Rec
from os import getcwd
import numpy as np
import cv2
import time
from base64 import b64decode
from os import remove
from slice_png import img as bgImg
from EmotionRecongnition_UI import Ui_MainWindow
import image1_rc


class Emotion_MainWindow(Ui_MainWindow):
    def __init__(self, MainWindow):
        self.path = getcwd()
        self.timer_camera = QtCore.QTimer()  # 定时器
        self.timer_video = QtCore.QTimer()  # 定时器

        self.setupUi(MainWindow)
        self.retranslateUi(MainWindow)
        self.slot_init()  # 槽函数设置

        # 设置界面动画
        gif = QMovie(':/newPrefix/icons/scan.gif')
        self.label_face.setMovie(gif)
        gif.start()

        self.cap = cv2.VideoCapture()  # 屏幕画面对象
        self.cap2 = cv2.VideoCapture()
        self.CAM_NUM = 0  # 摄像头标号
        self.model_path = None  # 模型路径
        # self.__flag_work = 0

    def slot_init(self):  # 定义槽函数
        self.toolButton_camera.clicked.connect(self.button_open_camera_click)
        self.toolButton_model.clicked.connect(self.choose_model)
        self.toolButton_video.clicked.connect(self.button_open_video_click)

        self.timer_camera.timeout.connect(self.show_camera)
        self.timer_video.timeout.connect(self.show_video)
        self.toolButton_file.clicked.connect(self.choose_pic)

    def button_open_camera_click(self):
        # 界面处理
        self.timer_camera.stop()
        self.timer_video.stop()
        self.cap.release()
        self.cap2.release()
        self.label_face.clear()
        self.label_result.setText('None')
        self.label_time.setText('0 s')
        self.textEdit_camera.setText('实时摄像已关闭')
        self.textEdit_video.setText("视频未选中")
        self.label_outputResult.clear()
        self.label_outputResult.setStyleSheet("border-image: url(:/newPrefix/icons/ini.png);")

        if self.timer_camera.isActive() == False:  # 检查定时状态
            flag = self.cap.open(self.CAM_NUM)  # 检查相机状态
            if flag == False:  # 相机打开失败提示
                msg = QtWidgets.QMessageBox.warning(self.centralwidget, u"Warning",
                                                    u"请检测相机与电脑是否连接正确！ ",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)

            else:
                # 准备运行识别程序
                self.textEdit_pic.setText('文件未选中')
                QtWidgets.QApplication.processEvents()
                self.textEdit_camera.setText('实时摄像已开启')
                self.label_face.setText('正在启动识别系统...\n\nleading')
                # 新建对象
                self.emotion_model = Emotion_Rec(self.model_path)
                QtWidgets.QApplication.processEvents()
                # 打开定时器
                self.timer_camera.start(30)
        else:
            # 定时器未开启，界面回复初始状态
            self.timer_camera.stop()
            self.timer_video.stop()
            self.cap.release()
            self.cap2.release()
            self.label_face.clear()
            self.textEdit_camera.setText('实时摄像已关闭')
            self.textEdit_pic.setText('文件未选中')
            self.textEdit_video.setText('文件未选中')
            gif = QMovie(':/newPrefix/icons/scan.gif')
            self.label_face.setMovie(gif)
            gif.start()
            self.label_outputResult.clear()
            self.label_outputResult.setStyleSheet("border-image: url(:/newPrefix/icons/ini.png);")

            self.label_result.setText('None')
            self.label_time.setText('0 s')

    def button_open_video_click(self):
        # 界面处理
        self.timer_camera.stop()
        self.timer_video.stop()
        self.cap.release()
        self.cap2.release()
        self.label_face.clear()
        self.label_result.setText('None')
        self.label_time.setText('0 s')
        self.textEdit_camera.setText('实时摄像已关闭')
        self.textEdit_video.setText("视频未选中")
        self.label_outputResult.clear()
        self.label_outputResult.setStyleSheet("border-image: url(:/newPrefix/icons/ini.png);")

        if self.timer_video.isActive() == False:  # 检查定时状态
            # 使用文件选择对话框选择图片
            fileName_choose, filetype = QFileDialog.getOpenFileName(
                self.centralwidget, "选取图片文件",
                self.path,  # 起始路径
                "视频(*.mp4;)")  # 文件类型
            self.path = fileName_choose  # 保存路径
            if fileName_choose != '':
                self.textEdit_video.setText(fileName_choose + '文件已选中')
                # 新建对象
                self.cap2 = cv2.VideoCapture(self.path)
                self.emotion_model = Emotion_Rec(self.model_path)
                # 打开定时器
                self.label_face.setText('正在启动识别系统...\n\nleading')
                self.timer_video.start(30)
                QtWidgets.QApplication.processEvents()
            else:
                # 准备运行识别程序
                self.textEdit_pic.setText('文件未选中')
                self.textEdit_video.setText('文件未选中')
                QtWidgets.QApplication.processEvents()
                self.textEdit_camera.setText('实时摄像已关闭')

        else:
            # 定时器未开启，界面回复初始状态
            self.timer_camera.stop()
            self.timer_video.stop()
            self.cap.release()
            self.cap2.release()
            self.label_face.clear()
            self.textEdit_camera.setText('实时摄像已关闭')
            self.textEdit_pic.setText('文件未选中')
            self.textEdit_video.setText('文件未选中')
            gif = QMovie(':/newPrefix/icons/scan.gif')
            self.label_face.setMovie(gif)
            gif.start()
            self.label_outputResult.clear()
            self.label_outputResult.setStyleSheet("border-image: url(:/newPrefix/icons/ini.png);")

            self.label_result.setText('None')
            self.label_time.setText('0 s')

    def show_camera(self):
        # 定时器槽函数，每隔一段时间执行
        flag, self.image = self.cap.read()  # 获取画面
        self.image = cv2.flip(self.image, 1)  # 左右翻转

        tmp = open('slice.png', 'wb')
        tmp.write(b64decode(bgImg))
        tmp.close()
        canvas = cv2.imread('slice.png')  # 用于数据显示的背景图片
        remove('slice.png')

        time_start = time.time()  # 计时
        # 使用模型预测
        result = self.emotion_model.run(self.image, canvas, self.label_face, self.label_outputResult)
        time_end = time.time()
        # 在界面显示结果
        self.label_result.setText(result)
        self.label_time.setText(str(round((time_end - time_start), 3)) + ' s')


    def show_video(self):
        # 定时器槽函数，每隔一段时间执行
        flag, self.image = self.cap2.read()  # 获取画面

        # self.image = cv2.flip(self.image, 1)  # 左右翻转

        tmp = open('slice.png', 'wb')
        tmp.write(b64decode(bgImg))
        tmp.close()
        canvas = cv2.imread('slice.png')  # 用于数据显示的背景图片
        remove('slice.png')

        time_start = time.time()  # 计时
        # 使用模型预测
        result = 'None'
        if self.image is not None:
            result = self.emotion_model.run(self.image, canvas, self.label_face, self.label_outputResult)
        time_end = time.time()
        # 在界面显示结果
        self.label_result.setText(result)
        self.label_time.setText(str(round((time_end - time_start), 3)) + ' s')


    def choose_pic(self):
        # 界面处理
        self.timer_camera.stop()
        self.timer_video.stop()
        self.cap.release()
        self.cap2.release()
        self.label_face.clear()
        self.label_result.setText('None')
        self.label_time.setText('0 s')
        self.textEdit_camera.setText('实时摄像已关闭')
        self.textEdit_video.setText('文件未选中')
        self.label_outputResult.clear()
        self.label_outputResult.setStyleSheet("border-image: url(:/newPrefix/icons/ini.png);")

        # 使用文件选择对话框选择图片
        fileName_choose, filetype = QFileDialog.getOpenFileName(
            self.centralwidget, "选取图片文件",
            self.path,  # 起始路径
            "图片(*.jpg;*.jpeg;*.png)")  # 文件类型
        self.path = fileName_choose  # 保存路径
        if fileName_choose != '':
            self.textEdit_pic.setText(fileName_choose + '文件已选中')
            self.label_face.setText('正在启动识别系统...\n\nleading')
            QtWidgets.QApplication.processEvents()
            # 生成模型对象
            self.emotion_model = Emotion_Rec(self.model_path)
            # 读取背景图
            tmp = open('slice.png', 'wb')
            tmp.write(b64decode(bgImg))
            tmp.close()
            canvas = cv2.imread('slice.png')
            remove('slice.png')

            image = self.cv_imread(fileName_choose)  # 读取选择的图片
            # 计时并开始模型预测
            QtWidgets.QApplication.processEvents()
            time_start = time.time()
            result = self.emotion_model.run(image, canvas, self.label_face, self.label_outputResult)
            time_end = time.time()
            # 显示结果
            self.label_result.setText(result)
            self.label_time.setText(str(round((time_end - time_start), 3)) + ' s')

        else:
            # 选择取消，恢复界面状态
            self.textEdit_pic.setText('文件未选中')
            gif = QMovie(':/newPrefix/icons/scan.gif')
            self.label_face.setMovie(gif)
            gif.start()
            self.label_outputResult.clear()  # 清除画面
            self.label_outputResult.setStyleSheet("border-image: url(:/newPrefix/icons/ini.png);")
            self.label_result.setText('None')
            self.label_time.setText('0 s')

    def cv_imread(self, filePath):
        # 读取图片
        cv_img = cv2.imdecode(np.fromfile(filePath, dtype=np.uint8), -1)
        ## imdecode读取的是rgb，如果后续需要opencv处理的话，需要转换成bgr，转换后图片颜色会变化
        ## cv_img=cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)
        return cv_img

    def choose_model(self):
        # 选择训练好的模型文件
        self.timer_camera.stop()
        self.timer_video.stop()
        self.cap.release()
        self.cap2.release()
        self.label_face.clear()
        self.label_result.setText('None')
        self.label_time.setText('0 s')
        self.textEdit_camera.setText('实时摄像已关闭')
        self.textEdit_video.setText('文件未选中')
        self.textEdit_pic.setText('文件未选中')
        self.label_outputResult.clear()
        self.label_outputResult.setStyleSheet("border-image: url(:/newPrefix/icons/ini.png);")

        # 调用文件选择对话框
        fileName_choose, filetype = QFileDialog.getOpenFileName(self.centralwidget,
                                                                "选取图片文件", getcwd(),  # 起始路径
                                                                "Model File (*.hdf5)")  # 文件类型
        # 显示提示信息
        if fileName_choose != '':
            self.model_path = fileName_choose
            self.textEdit_model.setText(fileName_choose + ' 已选中')
        else:
            self.textEdit_model.setText('使用默认模型')

        # 恢复界面
        gif = QMovie(':/newPrefix/icons/scan.gif')
        self.label_face.setMovie(gif)
        gif.start()
