import tupian_rc
import ChuJiTwo
# ----------------------------------
import cv2
import time
import threading
from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Tuanduijieshao import Ui_MainWindow1
from Caozuoshuoming import Ui_MainWindow2
from pathlib import Path
import os
from PPYOLO.detection import Detector
from Sort_OH.tracker import Sort_OH

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'


# 时间--------------------------------------------------------------
class Display1(QMainWindow, QTabWidget, ChuJiTwo.Ui_MainWindow, Ui_MainWindow1, Ui_MainWindow2):
    # 定义一个列表全局变量，用来存储检索到视频的地址
    bianliang = []

    def __init__(self):
        super(Display1, self).__init__()
        self.setupUi(self)

        self.horizontalSlider.valueChanged.connect(self.lcd)
        self.lcdNumber.display(str("%03.2f" % (self.horizontalSlider.value() / 100)))

        # 输出人数
        self.threshold = 0.3
        self.frame_num = 0
        self.textEdit.setText("****输出信息****")
        self.detector = Detector('./PPYOLO/model/', threshold=0.3, use_gpu=True)
        self.tracker = Sort_OH(conf_trgt=0.92, conf_objt=0.92)

        # ==========================
        # 默认视频源为本地文件
        self.radioButtonFile.setChecked(True)
        # self.isCamera = False 用Fales表示播放本地文件
        self.isCamera = False
        # self.Jinzhidianjiguanbi()
        self.a = 0
        self.b = 0
        self.close_clicked = 1

        # 创建一个关闭事件并设为未触发
        self.continueEvent1 = threading.Event()
        self.continueEvent1.clear()

        self.stopEvent = threading.Event()
        self.stopEvent.clear()

        # 动态显示时间在label_4上，显示时间
        timer = QTimer(self)
        timer.timeout.connect(self.showtime)
        timer.start()

    def lcd(self):
        self.lcdNumber.display(str("%03.2f" % (self.horizontalSlider.value() / 100)))
        self.threshold = self.horizontalSlider.value() / 100
        # print(self.threshold)

    # 关闭界面后，关闭所有程序
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.a = 0
        self.stopEvent.set()

    # 定义动态背景图片事件
    def beijingtupian(self):
        None
        # time.sleep(0.7)
        # self.gif = QMovie("TuPian/龙背景.png")
        # self.DispalyLabel.setMovie(self.gif)
        # self.gif.start()

    # 视频列表 ===================================================================
    # 主界面检索视频按钮，用于检索本地视频
    def clicked(self):
        # 默认本地文件被选择
        self.radioButtonFile.setChecked(True)

        # 默认视频列表可以被点击
        self.shipinliebiao.setEnabled(True)
        # self.fileName = QFileDialog.getExistingDirectory(None,"请选择视频文件夹路径",os.getcwd())
        self.fileName = "./video/"
        if self.fileName == "":
            return

        # print(self.fileName)
        self.list = os.listdir(self.fileName)  # 遍历选择的文件夹

        num = 0  # 记录视频的数量
        self.shipinliebiao.clear()  # 清空列表项
        # self.list.clear()                       # 清空视频地址列表
        global bianliang
        self.bianliang.clear()
        for i in range(0, len(self.list)):
            filepath = os.path.join(self.fileName, self.list[i])  # 记录遍历到的文件地址
            # print("记录遍历到的文件地址666"+filepath)

            if os.path.isfile(filepath):  # 判断是否为文件
                imgType = os.path.splitext(filepath)[1]  # 获取扩展名
                # print(imgType)
                if imgType in [".mp4", ".avi"]:  # 判断是否为想要视频格式
                    num += 1  # 视频数量+1
                    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    zhenshu = 180  # 定于帧数变量
                    filename1 = Path(filepath).stem  # 不带后缀和地址的文件名
                    cap = cv2.VideoCapture(filepath)  # 读取视频文件地址
                    cap.set(cv2.CAP_PROP_POS_FRAMES, float(zhenshu))  # 帧数
                    if cap.isOpened():  # 判断是否正常打开
                        rval, frame = cap.read()  # 参数ret 为True 或者False,代表有没有读取到图片,第二个参数frame表示截取到一帧的图片
                    Diyizhen = str(self.fileName) + "/" + str(filename1) + ".jpg"
                    a = "Tupian"
                    cv2.imencode(".jpg", frame)[1].tofile(Diyizhen)  # 英文或中文路径均适用(保存)
                    # print(Diyizhen)  # 打印生成的路径名
                    cap.release()

                    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    # self.shipinliebiao.addItem(self.list [ i ])
                    # self.shipinliebiao.addIcon(QtGui.QIcon("TuPian/logo.jpg"))
                    self.item = QtWidgets.QListWidgetItem(self.shipinliebiao)
                    self.item.setIcon(QtGui.QIcon(Diyizhen))
                    self.item.setText(self.list[i])
                    # print(num)  # 显示视频列表数量

                    # 编写视频地址信息，保存在全局变量bianliang【】中
                    bianliang = self.fileName + "/" + self.list[i]
                    print("self.list[i]" + self.list[i])
                    self.bianliang.append(bianliang)
                    print("bianliang" + bianliang)
        # 检索的时候直接跳到本地文件
        self.radioButtonFile1()

    # 视频列表控制=========================================================

    # 界面双击直接打开本地文件
    def open2(self):
        # 若已经播放视频，先使得视频关闭

        if self.a == 1:
            if self.b == 1:
                self.continueEvent1.set()
            self.a = 0
            self.stopEvent.set()

            del self.tracker
            self.textEdit.clear()
            self.frame_num = 0
            self.textEdit.append(">>> 算法重新初始化...")

        self.textEdit.append(">>> 算法初始化...")
        self.tracker = Sort_OH(conf_trgt=0.92, conf_objt=0.92)

        # 视频播放前的加载背景图片========
        time.sleep(0.07)
        self.gif = QMovie("TuPian/动图基地.gif")
        self.DispalyLabel.setMovie(self.gif)
        self.gif.start()

        # 播放本地文件======================
        # 选择本地文件按钮
        self.radioButtonFile.setChecked(True)
        # 查找所点击位置的序号
        i = self.shipinliebiao.currentRow()
        if self.a == 0:
            self.isCamera = False
        if not self.isCamera:
            self.cap = cv2.VideoCapture(self.bianliang[i])
            self.frameRate = self.cap.get(cv2.CAP_PROP_FPS)
            self.textEdit.append(">>> 初始化成功，准备检测与跟踪\n")
            # 创建视频显示线程
            th = threading.Thread(target=self.Display)
            th.start()
        self.stopEvent.clear()
        self.a = 1

        # QMessageBox.information(self, "QListView", "你选择了: " + self.qList [ qModelIndex.row() ])
        # print("点击的是：" + str(qModelIndex.row()))

    # 显示时间======================================================================
    # 显示的时间内容
    def showtime(self):
        datetime = QDateTime.currentDateTime()
        text = datetime.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.label_3.setText("    " + text)

    # 团队界面=====================================================================
    # 查看团队信息，打开另一个界面
    def tuanduixinxi1(self):
        self.form1 = QtWidgets.QWidget()
        self.ui2 = Ui_MainWindow1()
        self.ui2.setupUi(self.form1)
        self.form1.show()

    #   查看帮助信息，打开另一个界面
    def caozuoshuoming1(self):
        self.form1 = QtWidgets.QWidget()
        # 调用Help模块的类
        self.ui2 = Ui_MainWindow2()
        self.ui2.setupUi(self.form1)
        self.form1.show()

    # 输出视频========================================================================
    # 状态栏选择摄像头
    def radioButtonCam2(self):
        # 禁止点击视频列表
        self.shipinliebiao.setEnabled(False)
        # 禁止点击视频按钮
        self.a = 0
        if self.a == 0:
            self.radioButtonCam.setChecked(True)
            self.isCamera = True
            self.Open1()

    # 状态栏选择本地文件
    def radioButtonFile2(self):
        # 禁止点击视频列表
        self.shipinliebiao.setEnabled(False)
        self.a = 0
        self.verticalLayout_2.addWidget(self.radioButtonFile)
        if self.a == 0:
            # 默认选择本地文件按钮
            self.radioButtonFile.setEnabled(True)
            # 非摄像头
            self.isCamera = False
        # 直接打开视频
        self.Open1()

    # 主界面=========================================================
    # 主界面选择摄像头
    def radioButtonCam1(self):
        self.shipinliebiao.setEnabled(False)
        if self.a == 1:
            self.a = 0
            self.stopEvent.set()
            # self.beijingtupian()
        self.isCamera = True

    # 主界面选择本地文件
    def radioButtonFile1(self):
        self.shipinliebiao.setEnabled(True)
        if self.a == 1:
            self.a = 0
            self.stopEvent.set()
            # self.beijingtupian()
        self.isCamera = False

    # 主界面暂停按钮
    def suspend_continue1(self):
        if self.a == 1:
            self.continueEvent1.set()

    # def pause(self):
    #     self.__flag.clear()  # 设置为False, 让线程阻塞
    #     print("pause")
    #
    # def resume(self):
    #     self.__flag.set()  # 设置为True, 让线程停止阻塞
    #     print("resume")

    # 主界面打开按钮
    def Open1(self):
        if self.a == 1:
            if self.b == 1:
                self.continueEvent1.set()
                self.b = 0
            self.a = 0
            self.stopEvent.set()

            del self.tracker
            self.textEdit.clear()
            self.textEdit.append(">>> 算法重新初始化...")

        # 展示背景动态图片
        # self.beijingtupian()
        self.textEdit.append(">>> 算法初始化...")
        self.tracker = Sort_OH(conf_trgt=0.92, conf_objt=0.92)
        self.frame_num = 0

        self.fileName = ""
        # self.isCamera为True打开摄像头，self.isCamera为False打开本地文件
        if not self.isCamera:
            self.fileName, self.fileType = QFileDialog.getOpenFileName(self, 'Choose file', './video',
                                                                       "MP4Files(*.mp4);;AVI Files(*.avi)")
            self.cap = cv2.VideoCapture(self.fileName)
            self.frameRate = self.cap.get(cv2.CAP_PROP_FPS)
        else:
            self.a = 1
            self.cap = cv2.VideoCapture(0)

        # 创建视频显示线程
        if (self.fileName != "") or (self.a == 1):
            th = threading.Thread(target=self.Display)
            th.start()
        self.stopEvent.clear()
        self.a = 1
        self.textEdit.append(">>> 初始化成功，准备检测与跟踪\n")

    # 主界面关闭按钮
    def Close1(self):

        if self.a == 1:
            if self.b == 1:
                self.continueEvent1.set()
            self.a = 0
            self.stopEvent.set()
            del self.tracker
            self.textEdit.clear()
            self.frame_num = 0

        self.tracker = Sort_OH(conf_trgt=0.92, conf_objt=0.92)

            # 展示背景动态图片
            # self.beijingtupian()

    def Display(self):

        while self.cap.isOpened() and True:
            success, frame = self.cap.read()

            print(success)
            if success == False:
                # print("play finished")  # 判断本地文件播放完毕
                break

            # 为摄像头设置水平翻转
            if self.isCamera == True:
                frame = cv2.flip(frame, 1)
            # RGB转BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # 检测、跟踪
            start = time.time()
            tlwh, xyxy, confidences = self.detector.predict(frame)
            output, output1, output2, count = self.tracker.update(frame, xyxy, confidences)
            end = time.time()

            # show information
            num = 0
            for j in range(output.shape[0]):
                if self.threshold < output[j][5]:
                    num = num + 1
                    cv2.putText(frame, str(int(output[j][4])), (int(output[j][0]), int(output[j][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                    cv2.rectangle(frame, (int(output[j][0]), int(output[j][1])), (int(output[j][2]), int(output[j][3])),
                                  (0, 0, 255), 2)

            self.frame_num = self.frame_num + 1
            cv2.putText(frame, str(self.frame_num), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

            cv2.putText(frame, 'Num:' + str(num), (frame.shape[1] - 200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0),
                        3)

            fps = "%.1f" % (1 / (end - start))
            cv2.putText(frame, 'Fps:' + str(fps), (frame.shape[1] - 200, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0),
                        3)

            self.lcdNumber_2.display('{:^5}'.format(str(count)))

            output_str = "[frame-" + str(self.frame_num + 1) + "]: 成功跟踪目标" + str(
                output.shape[0]) + "个，" + "待匹配目标" + str(output1.shape[0]) + "个，" + "被遮挡目标" + str(output2.shape[0]) + "个"
            self.textEdit.append(">>> " + output_str)
            self.textEdit.moveCursor(self.textEdit.textCursor().End)

            img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            # 使视频与lable自适应大小
            p = img.scaled(self.DispalyLabel.width(), self.DispalyLabel.height())
            self.DispalyLabel.setPixmap(QPixmap.fromImage(p))

            # 播放摄像头
            if self.isCamera:
                cv2.waitKey(1)
            else:
                cv2.waitKey(1)
                # 输出本地视频帧率
                # cv2.waitKey(int(1000 / self.frameRate))
            # 判断关闭事件是否已触发

            # 点击暂定，再点击继续
            if True == self.continueEvent1.is_set():
                self.continueEvent1.clear()
                self.b = 1
                self.First.setText("继续")
                # 使得关闭按钮不可被选取
                # self.Jinzhidianjiguanbi()
                while self.b == 1:
                    if True == self.continueEvent1.is_set():
                        self.continueEvent1.clear()
                        self.b = 0
                        self.First.setText("暂停")
                        # 使得关闭按钮可被选取
                        # self.Yunxudianjiguanbi()
            if True == self.stopEvent.is_set():
                # 关闭事件置为未触发，清空显示label
                break

        self.cap.release()
        self.stopEvent.clear()
        self.DispalyLabel.clear()

    # 主界面最小化
    def Zuixiaohua(self):
        self.setWindowState(Qt.WindowMinimized)

    # 主界面最大化
    def Zuidahua(self):
        self.setWindowState(Qt.WindowMaximized)


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    my = Display1()
    my.show()
    sys.exit(app.exec_())
