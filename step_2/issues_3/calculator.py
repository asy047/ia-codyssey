from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from styles import get_button_style 


def split_expression(expr): # 연산자 기준으로 수식 분리

    tokens = []
    number = ""
    for char in expr:
        if char in "+-×÷":
            if number:
                tokens.append(number)
                number = ""
            tokens.append(char)
        else:
            number += char
    if number:
        tokens.append(number)
    return tokens


def format_number_with_commas(expr): # 1000단위 쉼표 추가
    
    tokens = split_expression(expr)
    formatted = []
    for token in tokens:
        if token not in "+-×÷":
            try:
                if "." in token:
                    integer_part, decimal_part = token.split(".")
                    integer_part = f"{int(integer_part):,}"
                    formatted.append(f"{integer_part}.{decimal_part}")
                else:
                    formatted.append(f"{int(token):,}")
            except:
                formatted.append(token)
        else:
            formatted.append(token)
    return "".join(formatted)


class IPhoneCalculator(QWidget):
    def __init__(self):
        """
        초기화 메소드
        - 윈도우 타이틀, 크기 설정
        - 계산기 상태 변수 초기화
        """
        super().__init__()
        self.setWindowTitle("iPhone Calculator - PyQt5 Clone")
        self.setStyleSheet("background-color: black;")
        self.setFixedSize(360, 600)

        self.current_input = ""
        self.display_expression = ""
        self.result_displayed = False

        self.init_ui()

    def init_ui(self):
        """
        UI 요소 초기화 및 버튼 배치
        """
        self.formula = QLabel("")
        self.formula.setStyleSheet("color: #A5A5A5; font-size: 20px;")
        self.formula.setAlignment(Qt.AlignRight)

        self.result = QLabel("0")
        self.result.setStyleSheet("color: white; font-size: 56px; font-weight: bold;")
        self.result.setAlignment(Qt.AlignRight)

        buttons = [
            ["AC", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["⌸", "0", ".", "="]
        ]

        grid = QGridLayout()
        grid.setSpacing(10)

        for row, row_data in enumerate(buttons):
            for col, text in enumerate(row_data):
                btn = QPushButton(text)
                btn.setFixedSize(80, 80)
                btn.setFont(QFont("Helvetica", 20))
                btn.setStyleSheet(get_button_style(text))
                btn.clicked.connect(lambda _, t=text: self.on_button_click(t))
                if text == "AC":
                    self.clear_btn = btn
                grid.addWidget(btn, row, col)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.formula)
        layout.addWidget(self.result)
        layout.addSpacing(10)
        layout.addLayout(grid)

        self.setLayout(layout)

    def update_display(self): # 결과값 디스플레이 업데이트
        
        if self.result_displayed:
            self.result.setText(format_number_with_commas(self.current_input))
            self.clear_btn.setText("AC")
        else:
            self.result.setText(format_number_with_commas(self.display_expression or "0"))
            self.clear_btn.setText("⌫" if self.display_expression else "AC")

    def get_last_number(self): # 마지막 숫자 반환
        
        num = ""
        for c in reversed(self.display_expression):
            if c in "+-×÷":
                break
            num = c + num
        return num

    def replace_last_number(self, new_val): #마지막 숫자 교체
        """
        마지막 숫자를 새 값으로 교체하는 함수
        """
        i = len(self.display_expression) - len(self.get_last_number())
        self.display_expression = self.display_expression[:i] + new_val

    def on_button_click(self, key): # 사칙연산,= 처리 함수
        
        if key in "0123456789":
            if self.result_displayed:
                self.display_expression = ""
                self.result_displayed = False
            self.display_expression += key
            self.update_display()

        elif key == ".":
            if self.result_displayed:
                self.display_expression = "0"
                self.result_displayed = False
            if not self.display_expression or self.display_expression[-1] in "+-×÷":
                self.display_expression += "0."
            else:
                last = self.get_last_number()
                if "." not in last:
                    self.display_expression += "."
            self.update_display()

        elif key in ["+", "-", "×", "÷"]:
            if self.result_displayed:
                self.display_expression = self.current_input
                self.result_displayed = False
            if not self.display_expression:
                self.display_expression = "0"
            if self.display_expression[-1:] in "+-×÷":
                self.display_expression = self.display_expression[:-1] + key
            else:
                self.display_expression += key
            self.update_display()

        elif key == "=":
            try:
                if not self.display_expression:
                    return
                formula = self.display_expression.replace(",", "").replace("×", "*").replace("÷", "/")
                result = str(eval(formula))
                if result.endswith(".0"):
                    result = result[:-2]
                self.formula.setText(format_number_with_commas(self.display_expression))
                self.current_input = result
                self.result_displayed = True
                self.update_display()
            except:
                self.result.setText("Error")
                self.formula.setText("")
                self.display_expression = ""
                self.result_displayed = True

        elif key in ["AC", "⌫"]:
            if self.clear_btn.text() == "⌫" and self.display_expression:
                self.display_expression = self.display_expression[:-1]
                self.update_display()
            else:
                self.display_expression = ""
                self.current_input = ""
                self.result_displayed = False
                self.formula.setText("")
                self.result.setText("0")
                self.clear_btn.setText("AC")

        elif key == "+/-":
            num = self.get_last_number()
            if num:
                if num.startswith("-"):
                    num = num[1:]
                else:
                    num = "-" + num
                self.replace_last_number(num)
                self.update_display()

        elif key == "%":
            num = self.get_last_number()
            try:
                if num:
                    percent = str(float(num) / 100)
                    self.replace_last_number(percent)
                    self.update_display()
            except:
                pass


if __name__ == "__main__":
    app = QApplication([]) # 이벤트 처리, GUI에 필요한 PyQt5 애플리케이션  
    calc = IPhoneCalculator() #시스템의 메인 함수
    calc.show()  
    app.exec_() 