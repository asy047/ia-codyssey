class Calculator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.current = '0'
        self.operator = None
        self.operand = None
        self.result = None
        self.is_new_input = True

    def input_number(self, num):
        if self.is_new_input:
            self.current = str(num)
            self.is_new_input = False
        else:
            if self.current == '0':
                self.current = str(num)
            else:
                self.current += str(num)

    def input_decimal(self):
        if '.' not in self.current:
            self.current += '.'
            self.is_new_input = False

    def add(self):
        self._calculate()
        self.operator = '+'
        self.operand = float(self.current)
        self.is_new_input = True

    def subtract(self):
        self._calculate()
        self.operator = '-'
        self.operand = float(self.current)
        self.is_new_input = True

    def multiply(self):
        self._calculate()
        self.operator = '*'
        self.operand = float(self.current)
        self.is_new_input = True

    def divide(self):
        self._calculate()
        self.operator = '/'
        self.operand = float(self.current)
        self.is_new_input = True

    def negative_positive(self):
        if self.current.startswith('-'):
            self.current = self.current[1:]
        else:
            if self.current != '0':
                self.current = '-' + self.current

    def percent(self):
        try:
            value = float(self.current) / 100
            self.current = str(value)
        except ValueError:
            self.current = 'Error'

    def equal(self):
        self._calculate()
        self.operator = None
        self.operand = None
        self.is_new_input = True
        # 소수점 6자리 이하 반올림
        try:
            value = float(self.current)
            if '.' in self.current:
                self.current = str(round(value, 6)).rstrip('0').rstrip('.') if '.' in str(round(value, 6)) else str(round(value, 6))
        except Exception:
            pass
        return self.current

    def _calculate(self):
        if self.operator and self.operand is not None:
            try:
                current_value = float(self.current)
                # 숫자 범위 체크
                if abs(current_value) > 1e308 or abs(self.operand) > 1e308:
                    self.current = 'Error: Number too large'
                    return
                
                if self.operator == '+':
                    result = self.operand + current_value
                elif self.operator == '-':
                    result = self.operand - current_value
                elif self.operator == '*':
                    result = self.operand * current_value
                elif self.operator == '/':
                    if current_value == 0:
                        self.current = 'Error: Division by zero'
                        return
                    result = self.operand / current_value
                
                # 결과값 범위 체크
                if abs(result) > 1e308:
                    self.current = 'Error: Result too large'
                    return
                    
                # 부동소수점 정밀도 처리
                if abs(result) < 1e-10:
                    result = 0
                    
                self.current = str(result)
            except Exception as e:
                self.current = f'Error: {str(e)}'

    def get_display(self):
        return self.current
