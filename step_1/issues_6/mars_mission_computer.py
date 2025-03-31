import random
import time


class DummySensor:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = random.uniform(18.0, 30.0)
        self.env_values['mars_base_external_temperature'] = random.uniform(0.0, 21.0)
        self.env_values['mars_base_internal_humidity'] = random.uniform(50.0, 60.0)
        self.env_values['mars_base_external_illuminance'] = random.uniform(500.0, 715.0)
        self.env_values['mars_base_internal_co2'] = random.uniform(0.02, 0.1)
        self.env_values['mars_base_internal_oxygen'] = random.uniform(4.0, 7.0)

    def get_env(self):
        try:
            log_line = self._format_log()
            with open('env_log.txt', 'a', encoding='utf-8') as file:
                file.write(log_line + '\n')
        except Exception as e:
            print('로그 파일 저장 중 오류:', e)

        return self.env_values

    def _format_log(self):
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        values = self.env_values
        log = (
            now + ', '
            + f"{values['mars_base_internal_temperature']:.2f}, "
            + f"{values['mars_base_external_temperature']:.2f}, "
            + f"{values['mars_base_internal_humidity']:.2f}, "
            + f"{values['mars_base_external_illuminance']:.2f}, "
            + f"{values['mars_base_internal_co2']:.4f}, "
            + f"{values['mars_base_internal_oxygen']:.2f}"
        )
        return log


# 인스턴스 생성 및 테스트
if __name__ == '__main__':
    ds = DummySensor()
    ds.set_env()
    values = ds.get_env()

    print('[현재 센서 데이터]')
    for key in values:
        print(key + ':', round(values[key], 2))
