# Расширенный мониторинг NTP сервера с Zabbix

Это руководство поможет вам настроить расширенный мониторинг NTP сервера с использованием Python-скрипта и интегрировать его с Zabbix.

## Предварительные требования

- Python 3
- Zabbix сервер и Zabbix агент 2
- NTP сервер для мониторинга

## Шаг 1: Установка необходимых библиотек Python

```bash
pip install ntplib argparse
```

## Шаг 2: Настройка Python-скрипта

Скопируйте улучшенный скрипт `ntp_check.py` в директорию, доступную для Zabbix агента, например, `/etc/zabbix/scripts/`.

```bash
mkdir -p /etc/zabbix/scripts/
cp ntp_check.py /etc/zabbix/scripts/
chmod +x /etc/zabbix/scripts/ntp_check.py
```

## Шаг 3: Настройка Zabbix-агента

Добавьте следующие строки в конфигурационный файл Zabbix агента (`/etc/zabbix/zabbix_agent2.conf`):

```
# NTP мониторинг
UserParameter=ntp.check[*],/etc/zabbix/scripts/ntp_check.py --server $1 --operation $2 --timeout $3
UserParameter=ntp.discovery,/etc/zabbix/scripts/ntp_check.py --operation discovery
```

Перезапустите Zabbix агент:

```bash
sudo systemctl restart zabbix-agent2
```

## Шаг 4: Создание правила обнаружения в Zabbix

1. Войдите в веб-интерфейс Zabbix
2. Перейдите в раздел **Настройка** → **Узлы сети**
3. Выберите нужный узел и перейдите на вкладку **Правила обнаружения**
4. Нажмите **Создать правило обнаружения**:
   - **Имя**: NTP Metrics Discovery
   - **Тип**: Zabbix агент
   - **Ключ**: ntp.discovery
   - **Интервал обновления**: 1h (или по вашему усмотрению)
5. Перейдите на вкладку **Прототипы элементов данных** и нажмите **Создать прототип элемента данных**:
   - **Имя**: NTP {#DESC}
   - **Тип**: Zabbix агент
   - **Ключ**: ntp.check[192.168.62.75,{#METRIC},5]
   - **Тип информации**: зависит от метрики (используйте Число с плавающей точкой для большинства метрик)
   - **Единица измерения**: для response_time - s (секунды), для offset - ms (миллисекунды), для остальных можно оставить пустым
   - **Интервал обновления**: 1m (или по вашему усмотрению)
6. Сохраните прототип элемента данных и правило обнаружения

## Шаг 5: Создание дополнительных элементов данных (опционально)

Для особо важных метрик, таких как доступность и время отклика, можно создать отдельные элементы данных:

1. Перейдите на вкладку **Элементы данных** и нажмите **Создать элемент данных**:
   - **Имя**: NTP Доступность сервера
   - **Тип**: Zabbix агент
   - **Ключ**: ntp.check[192.168.62.75,availability,5]
   - **Тип информации**: Числовой (целое положительное)
   - **Интервал обновления**: 1m

2. Создайте ещё один элемент данных:
   - **Имя**: NTP Время отклика
   - **Тип**: Zabbix агент
   - **Ключ**: ntp.check[192.168.62.75,response_time,5]
   - **Тип информации**: Числовой (с плавающей точкой)
   - **Единица измерения**: s
   - **Интервал обновления**: 1m

## Шаг 6: Создание триггеров

Создайте триггеры для важных метрик:

1. Перейдите на вкладку **Триггеры** и нажмите **Создать триггер**:
   - **Имя**: NTP сервер недоступен на {HOST.NAME}
   - **Выражение**: `{your_host:ntp.check[192.168.62.75,availability,5].last()}=1`
   - **Степень важности**: Высокая

2. Создайте дополнительный триггер:
   - **Имя**: NTP высокое время отклика на {HOST.NAME}
   - **Выражение**: `{your_host:ntp.check[192.168.62.75,response_time,5].avg(5m)}>0.5`
   - **Степень важности**: Средняя

3. Создайте триггер для контроля stratum:
   - **Имя**: NTP высокий уровень stratum на {HOST.NAME}
   - **Выражение**: `{your_host:ntp.check[192.168.62.75,stratum,5].last()}>3`
   - **Степень важности**: Предупреждение

4. Создайте триггер для смещения времени:
   - **Имя**: NTP большое смещение времени на {HOST.NAME}
   - **Выражение**: `{your_host:ntp.check[192.168.62.75,offset,5].abs()}>100`
   - **Степень важности**: Средняя

## Шаг 7: Создание графиков

1. Перейдите на вкладку **Графики** и нажмите **Создать график**:
   - **Имя**: NTP время отклика
   - Добавьте элемент с ключом `ntp.check[192.168.62.75,response_time,5]`

2. Создайте график для смещения времени:
   - **Имя**: NTP смещение времени
   - Добавьте элемент с ключом `ntp.check[192.168.62.75,offset,5]`

## Описание мониторируемых метрик

| Метрика | Описание | Рекомендуемые пороги |
|---------|----------|----------------------|
| availability | Доступность NTP сервера (0 - доступен, 1 - недоступен) | 0 - норма, 1 - тревога |
| response_time | Время отклика в секундах | <0.1с - хорошо, >0.5с - плохо |
| offset | Смещение времени в секундах между вашими часами и NTP сервером | <50мс - хорошо, >100мс - плохо |
| stratum | Уровень stratum NTP сервера (чем меньше, тем лучше) | ≤2 - хорошо, >3 - проблема |
| root_delay | Задержка до корневого источника времени | <100мс - нормально |
| root_dispersion | Максимальная погрешность от корневого источника | <100мс - нормально |
| ref_id | Идентификатор источника времени | Мониторинг изменений |
| ref_time | Время последней синхронизации с источником | Мониторинг регулярности |
| precision | Точность системных часов (log2) | Мониторинг резких изменений |
| delay | Задержка прохождения пакета | <50мс - хорошо |
| poll | Интервал опроса в секундах | Обычно 64-1024с |

## Дополнительные рекомендации

- **Замените IP-адрес**: Во всех командах выше замените `192.168.62.75` на IP-адрес вашего NTP сервера.
- **Настройте шаблон**: Для мониторинга нескольких NTP серверов создайте шаблон с макросами.
- **Версия Zabbix 6.4+**: Для оптимального использования рекомендуется Zabbix версии 6.4 и выше, где улучшена поддержка JSON и обнаружения.
