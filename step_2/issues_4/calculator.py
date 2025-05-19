class Calculator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.current = '0'
        self.operator = None
        self.operand = None
        self.result = None
        self.is_new_input = True
        self.display_expression = ''

    def format_number(self, num_str):
        """숫자 문자열을 천 단위 콤마가 포함된 형식으로 변환"""
        try:
            if '.' in num_str:
                integer_part, decimal_part = num_str.split('.')
                integer_part = f"{int(integer_part):,}"
                return f"{integer_part}.{decimal_part}"
            return f"{int(num_str):,}"
        except:
            return num_str

    def input_number(self, num):
        if self.is_new_input:
            self.current = str(num)
            self.is_new_input = False
        else:
            if self.current == '0':
                self.current = str(num)
            else:
                self.current += str(num)
        self.display_expression = self.format_number(self.current)

    def input_decimal(self):
        if self.is_new_input:
            self.current = '0.'
            self.is_new_input = False
        elif '.' not in self.current:
            self.current += '.'
        self.display_expression = self.format_number(self.current)

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
                current_value = float(self.current.replace(',', ''))
                operand_value = float(str(self.operand).replace(',', ''))
                
                # 숫자 범위 체크
                if abs(current_value) > 1e308 or abs(operand_value) > 1e308:
                    self.current = 'Error: Number too large'
                    return
                
                if self.operator == '+':
                    result = operand_value + current_value
                elif self.operator == '-':
                    result = operand_value - current_value
                elif self.operator == '*':
                    result = operand_value * current_value
                elif self.operator == '/':
                    if current_value == 0:
                        self.current = 'Error: Division by zero'
                        return
                    result = operand_value / current_value
                
                # 결과값 범위 체크
                if abs(result) > 1e308:
                    self.current = 'Error: Result too large'
                    return
                    
                # 부동소수점 정밀도 처리
                if abs(result) < 1e-10:
                    result = 0
                
                # 소수점 6자리 이하 반올림
                if isinstance(result, float):
                    result = round(result, 6)
                    if result.is_integer():
                        result = int(result)
                
                self.current = str(result)
                self.display_expression = self.format_number(self.current)
            except Exception as e:
                self.current = f'Error: {str(e)}'
                self.display_expression = self.current

    def get_display(self):
        """현재 표시될 값을 반환"""
        return self.display_expression if self.display_expression else self.current
