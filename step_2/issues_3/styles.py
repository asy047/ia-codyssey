def get_button_style(text):
    """
    버튼 스타일을 설정하는 함수
    - 연산자, 숫자, AC 등 각 버튼의 스타일을 다르게 설정
    """
    if text in ["÷", "×", "-", "+", "="]:
        return """
            QPushButton {
                background-color: #FF9500;
                color: white;
                border-radius: 40px;
            }
            QPushButton:pressed {
                background-color: #cc7a00;
            }
        """
    elif text in ["AC", "+/-", "%", "⌫"]:
        return """
            QPushButton {
                background-color: #505050;
                color: white;
                border-radius: 40px;
            }
            QPushButton:pressed {
                background-color: #666666;
            }
        """
    else:
        return """
            QPushButton {
                background-color: #1C1C1C;
                color: white;
                border-radius: 40px;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """