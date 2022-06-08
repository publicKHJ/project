import sqlite3
import sys
from socket import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from threading import *

datacon = sqlite3.connect('Animal.db')
ui = uic.loadUiType("base.ui")[0]

class Data: # 데이터 최초 불러오기 (출현현황)
    def __init__(self):
        con = sqlite3.connect("Animal.db")
        with con:
            cur = con.cursor()
            rows = cur.execute('select * from 출현현황')
            for row in rows:
                print(row)


class MainStudent(QWidget, ui):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.score=0
        # self.lcdNumber.display(self.score)
        self.sock=socket(AF_INET,SOCK_STREAM)
        self.sock.connect(('127.0.0.1',4321))

        self.overlap_btn.clicked.connect(self.overlapCheck)
        self.login_btn.clicked.connect(self.Login)
        self.qna_btn.clicked.connect(lambda :self.move_page('QnA'))
        self.send_line.returnPressed.connect(self.sendqna)

    def receive_messages(self,sock):

        while True:
            recv_message = sock.recv(4096)
            self.final_message=recv_message.decode('utf-8')
            print('QnA 받은메시지: ',self.final_message)
            self.textBrowser.append(self.final_message)

    def sendqna(self): # QnA or 상담용 채팅방?
        if self.send_line.text()=='':
            pass
        else:
            nickname=self.name_line.text()
            if nickname=='':
                nickname = '익명'

            sendData=f'QnA/{nickname}:{self.send_line.text()}' # QnA/닉네임:내용
            self.sock.send(sendData.encode('utf-8'))
            self.send_line.clear()

    def overlapCheck(self):
        sign_id=self.sign_idline.text() # 회원가입 ID lineEdit 값 가져오기
        sign_pw=self.sign_pwline.text() # 회원가입 PW lineEdit 값 가져오기

        if self.student_check.isChecked(): # 체크박스 여부에 따라 전송데이터 판단
            sendData=f"{'중복확인/학생/'+sign_id+'/'+sign_pw}"
        else:
            sendData=f"{'중복확인/교사/'+sign_id+'/'+sign_pw}"

        self.sock.send(sendData.encode()) # 회원가입/ID/PW

        recv_message=self.sock.recv(4096).decode()
        print('회원가입 메시지: ',recv_message)

        if '통과' in recv_message:
            QMessageBox.information(self, '중복확인', '사용가능한 아이디입니다.')
            self.sign_btn.clicked.connect(self.SignUp) # 통과시 회원가입 성공 메시지 or 로그인페이지 이동

        else:
            QMessageBox.warning(self, '중복확인', '이미 존재하는 아이디입니다.')

    def Login(self):
        login_id = self.sign_idline.text()  # 로그인 ID lineEdit 값 가져오기
        login_pw = self.sign_pwline.text()  # 로그인 PW lineEdit 값 가져오기
        self.sock.send(f"{'로그인/'+login_id+'/'+login_pw}".encode()) # 로그인/ID/PW

        recv_message = self.sock.recv(4096).decode()
        print('로그인 메시지: ', recv_message)
        if '통과' in recv_message:
            self.move_page('학생메인')

    def SignUp(self):
        QMessageBox.information(self, '회원가입', '회원가입 성공!.')
        self.move_page('로그인')


    def move_page(self,page):
        if page=='로그인':
            self.stackedWidget.setCurrentWidget(self.login_page)
        elif page=='QnA':
            self.stackedWidget.setCurrentWidget(self.qna_page)
            receiver = Thread(target=self.receive_messages,args=(self.sock,))  # 수신 스레드
            receiver.start()
        elif page=='학생메인':
            self.stackedWidget.setCurrentWidget(self.student_main_page)
        elif page=='학생1':
            self.stackedWidget.setCurrentWidget(self.student_page1)
        elif page=='퀴즈':
            self.stackedWidget.setCurrentWidget(self.student_quiz)


if __name__ == '__main__':
    # Data()

    app = QApplication(sys.argv)
    ex = MainStudent()
    ex.show()
    app.exec()