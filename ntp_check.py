import time
from ntplib import NTPClient, NTPException
import sys

def check_ntp_server(server_address):
    client = NTPClient()

    try:
        start_time = time.time()
        response = client.request(server_address)
        end_time = time.time()
        # Возвращаем время отклика
        return end_time - start_time
    except NTPException:
        # Возвращаем код ошибки 1
        return 1

if __name__ == "__main__":
    response_time = check_ntp_server('192.168.62.75')
    if response_time == 1:
        print(1) # Сервер недоступен
        sys.exit(1)
    else:
        print(0) # Сервер доступен
        print(response_time) # Время отклика
