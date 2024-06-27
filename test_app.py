import unittest
import json
from app import application
from io import BytesIO

class TestTimeZoneApp(unittest.TestCase):
    # Функция для имитации запроса к приложению
    def make_request(self, method, path, data=None):
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'wsgi.input': BytesIO(data.encode('utf-8') if data else b''),
            'CONTENT_LENGTH': str(len(data)) if data else '0',
        }
        status = []
        headers = []
        
        def start_response(s, h):
            status.append(s)
            headers.extend(h)
        
        response = application(environ, start_response)
        return status[0], headers, b''.join(response).decode('utf-8')
    
    # Тест для проверки получения текущего времени в заданной временной зоне
    def test_get_current_time(self):
        status, headers, response = self.make_request('GET', '/Europe/Moscow')
        self.assertIn('200 OK', status)
        self.assertIn('Current time in Europe/Moscow', response)
    
    # Тест для проверки конвертации времени
    def test_convert_time(self):
        data = json.dumps({
            "date": "12.20.2021 22:21:05",
            "tz": "EST",
            "target_tz": "Europe/Moscow"
        })
        status, headers, response = self.make_request('POST', '/api/v1/convert', data)
        self.assertIn('200 OK', status)
        self.assertIn('converted_date', response)
    
    # Тест для проверки вычисления разницы между двумя датами
    def test_date_difference(self):
        data = json.dumps({
            "first_date": "12.06.2024 22:21:05",
            "first_tz": "EST",
            "second_date": "12:30pm 2024-02-01",
            "second_tz": "Europe/Moscow"
        })
        status, headers, response = self.make_request('POST', '/api/v1/datediff', data)
        self.assertIn('200 OK', status)
        self.assertIn('difference_seconds', response)

if __name__ == '__main__':
    unittest.main()
