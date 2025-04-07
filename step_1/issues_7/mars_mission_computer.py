import time
import json
import threading

class DummySensor:
    def __init__(self):
        self.value = 0

    def read(self):
        self.value += 1
        return self.value


class MissionComputer:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0,
            'mars_base_external_temperature': 0,
            'mars_base_internal_humidity': 0,
            'mars_base_external_illuminance': 0,
            'mars_base_internal_co2': 0,
            'mars_base_internal_oxygen': 0
        }

        self.ds = DummySensor()
        self.stop_flag = False

        self.history = {
            key: [] for key in self.env_values
        }

        self.last_avg_time = time.time()

    def get_sensor_data(self):
        print('Press "q" and hit Enter to stop the system.')

        # 입력을 따로 받는 쓰레드 실행
        input_thread = threading.Thread(target=self._check_input)
        input_thread.daemon = True
        input_thread.start()

        while not self.stop_flag:
            for key in self.env_values:
                value = self.ds.read()
                self.env_values[key] = value
                self.history[key].append(value)

            print(json.dumps(self.env_values, indent=4))

            current_time = time.time()
            if current_time - self.last_avg_time >= 300:
                self.print_five_minute_average()
                self.last_avg_time = current_time
                for key in self.history:
                    self.history[key] = []

            time.sleep(5)

        print('System stopped...')

    def _check_input(self):
        while True:
            user_input = input()
            if user_input.strip().lower() == 'q':
                self.stop_flag = True
                break

    def print_five_minute_average(self):
        print('\n--- 5 Minute Average Values ---')
        avg_values = {}
        for key, values in self.history.items():
            avg = sum(values) / len(values) if values else 0
            avg_values[key] = round(avg, 2)
        print(json.dumps(avg_values, indent=4))
        print('-------------------------------\n')


# 실행부
if __name__ == '__main__':
    RunComputer = MissionComputer()
    RunComputer.get_sensor_data()
