import time
import sys
import json
import socket
import argparse
from ntplib import NTPClient, NTPException, NTPStats, REF_ID_TO_TEXT

def check_ntp_server(server_address, operation=None, timeout=5):
    """
    Проверка NTP сервера с расширенным набором метрик
    
    Args:
        server_address: IP адрес или имя хоста NTP сервера
        operation: Тип операции (доступность, время отклика, синхронизация и т.д.)
        timeout: Таймаут подключения в секундах
        
    Returns:
        Результат операции в зависимости от запрошенного параметра
    """
    client = NTPClient()
    
    # Устанавливаем таймаут для NTP запроса
    client.timeout = timeout
    
    if operation == "discovery":
        # Возвращаем список метрик для LLD (Low-Level Discovery) в Zabbix
        discovery_items = {
            "data": [
                {"{#METRIC}": "availability", "{#DESC}": "NTP Server Availability"},
                {"{#METRIC}": "response_time", "{#DESC}": "NTP Response Time"},
                {"{#METRIC}": "offset", "{#DESC}": "Time Offset"},
                {"{#METRIC}": "stratum", "{#DESC}": "NTP Stratum Level"},
                {"{#METRIC}": "root_delay", "{#DESC}": "Root Delay"},
                {"{#METRIC}": "root_dispersion", "{#DESC}": "Root Dispersion"},
                {"{#METRIC}": "ref_id", "{#DESC}": "Reference ID"},
                {"{#METRIC}": "ref_time", "{#DESC}": "Reference Timestamp"},
                {"{#METRIC}": "precision", "{#DESC}": "Clock Precision"}
            ]
        }
        return json.dumps(discovery_items)
    
    # Попытка подключения к NTP серверу
    try:
        start_time = time.time()
        response = client.request(server_address, version=4)
        end_time = time.time()
        response_time = end_time - start_time
        
        # В зависимости от запрошенной операции возвращаем соответствующие данные
        if operation == "availability":
            return 0  # Сервер доступен
        elif operation == "response_time":
            return response_time
        elif operation == "offset":
            return response.offset
        elif operation == "stratum":
            return response.stratum
        elif operation == "root_delay":
            return response.root_delay
        elif operation == "root_dispersion":
            return response.root_dispersion
        elif operation == "ref_id":
            # Получаем человекочитаемое имя источника, если оно известно
            ref_id_text = REF_ID_TO_TEXT.get(response.ref_id, hex(response.ref_id))
            return ref_id_text
        elif operation == "ref_time":
            return response.reference_time
        elif operation == "precision":
            return response.precision
        elif operation == "delay":
            return response.delay
        elif operation == "poll":
            return response.poll
        elif operation == "all":
            # Возвращаем все метрики в JSON формате
            metrics = {
                "availability": 0,
                "response_time": response_time,
                "offset": response.offset,
                "stratum": response.stratum,
                "root_delay": response.root_delay,
                "root_dispersion": response.root_dispersion,
                "ref_id": REF_ID_TO_TEXT.get(response.ref_id, hex(response.ref_id)),
                "ref_time": response.reference_time,
                "precision": response.precision,
                "delay": response.delay,
                "poll": response.poll,
                "leap": response.leap
            }
            return json.dumps(metrics)
        else:
            # По умолчанию возвращаем базовую информацию - наличие ответа от сервера
            return 0  # Сервер доступен
            
    except (NTPException, socket.timeout, socket.error, ConnectionRefusedError) as e:
        if operation == "availability":
            return 1  # Сервер недоступен
        elif operation == "all":
            error_info = {
                "availability": 1,
                "error": str(e)
            }
            return json.dumps(error_info)
        else:
            # Для всех остальных операций возвращаем ошибку
            return None

if __name__ == "__main__":
    # Создаем парсер аргументов командной строки для гибкости использования скрипта
    parser = argparse.ArgumentParser(description='NTP Server Monitoring Tool for Zabbix')
    parser.add_argument('--server', '-s', default='192.168.62.75',
                       help='NTP server address (default: 192.168.62.75)')
    parser.add_argument('--operation', '-o', 
                       choices=['availability', 'response_time', 'offset', 'stratum', 
                                'root_delay', 'root_dispersion', 'ref_id', 'ref_time', 
                                'precision', 'delay', 'poll', 'all', 'discovery'],
                       default='availability',
                       help='Operation to perform (default: availability)')
    parser.add_argument('--timeout', '-t', type=float, default=5,
                       help='Connection timeout in seconds (default: 5)')
    
    args = parser.parse_args()
    
    # Вызываем функцию проверки с переданными параметрами
    result = check_ntp_server(args.server, args.operation, args.timeout)
    
    # Выводим результат
    if result is not None:
        print(result)
        sys.exit(0)
    else:
        print("ZBX_NOTSUPPORTED")  # Специальный код для Zabbix, указывающий на ошибку
        sys.exit(1)
