import json
from wsgiref.simple_server import make_server
from pytz import timezone, all_timezones
from datetime import datetime

def application(environ, start_response):
    # Определяем путь и метод запроса
    path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # Обрабатываем GET запрос для получения текущего времени в заданной временной зоне
    if method == 'GET' and (path == '/' or path.startswith('/')):
        tz_name = path[1:] if len(path) > 1 else 'GMT'
        return get_current_time(tz_name, start_response)
    # Обрабатываем POST запрос для конвертации времени из одной временной зоны в другую
    elif method == 'POST' and path == '/api/v1/convert':
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
        data = json.loads(request_body)
        return convert_time(data, start_response)
    # Обрабатываем POST запрос для вычисления разницы между двумя датами
    elif method == 'POST' and path == '/api/v1/datediff':
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
        data = json.loads(request_body)
        return date_difference(data, start_response)
    else:
        return not_found(start_response)

def get_current_time(tz_name, start_response):
    # Получаем текущее время в заданной временной зоне
    try:
        if tz_name not in all_timezones:
            raise ValueError("Invalid timezone")
        tz = timezone(tz_name)
        current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [f"<html><body><h1>Current time in {tz_name} is {current_time}</h1></body></html>".encode('utf-8')]
    except Exception as e:
        return error_response(start_response, str(e))

def convert_time(data, start_response):
    # Конвертируем
    try:
        date_str = data.get('date')
        source_tz = data.get('tz')
        target_tz = data.get('target_tz')
        source_tz = timezone(source_tz)
        target_tz = timezone(target_tz)
        date = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
        source_date = source_tz.localize(date)
        target_date = source_date.astimezone(target_tz)
        result = target_date.strftime('%Y-%m-%d %H:%M:%S')
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps({"converted_date": result}).encode('utf-8')]
    except Exception as e:
        return error_response(start_response, str(e))

def date_difference(data, start_response):
    # Вычисляем разницу
    try:
        first_date_str = data.get('first_date')
        first_tz = data.get('first_tz')
        second_date_str = data.get('second_date')
        second_tz = data.get('second_tz')
        first_tz = timezone(first_tz)
        second_tz = timezone(second_tz)
        first_date = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')
        second_date = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d')
        first_date = first_tz.localize(first_date)
        second_date = second_tz.localize(second_date)
        diff_seconds = int((second_date - first_date).total_seconds())
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps({"difference_seconds": diff_seconds}).encode('utf-8')]
    except Exception as e:
        return error_response(start_response, str(e))

def error_response(start_response, message):
    # Обрабатываем ошибки и возвращаем сообщение об ошибке
    start_response('400 Bad Request', [('Content-Type', 'application/json')])
    return [json.dumps({"error": message}).encode('utf-8')]

def not_found(start_response):
    # 404 
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b"404 Not Found"]

if __name__ == '__main__':
    # Запуск
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
