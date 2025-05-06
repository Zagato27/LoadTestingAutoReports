import datetime
import re
from datetime import datetime
from influxdb import InfluxDBClient
import pandas as pd


def mergeDataframes(frames):
    """
    Объединяет список датафреймов в один датафрейм по столбцу 'transaction_name'.

    :param frames: список датафреймов для объединения
    :return: объединенный датафрейм
    """
    try:
        df = frames[0]
        for i in range(1, len(frames)):
            df = pd.merge(how="outer", left=df, right=frames[i], on='transaction_name')
        return df
    except Exception as e:
        print(f"Error merging dataframes: {e}")
        return None


import pandas as pd

def get_lr_response_from_influx(run_id, stages):
    """
    Получает данные ответа нагрузочного теста из InfluxDB для каждой стадии теста,
    объединяет результаты и преобразует их в формат Confluence Storage.

    :param run_id: идентификатор тестового прогона
    :param stages: список стадий теста с временем начала и окончания каждой стадии
    :return: данные ответа нагрузочного теста в формате Confluence Storage
    """
    try:
        frames = []
        i = 0
        for stage in stages:
            start_time = str(int(stage[0]))
            end_time = str(int(stage[1]))
            df = getLRResponseFromInflux(run_id, start_time, end_time, 'step ' + str(i))
            if df is not None:
                frames.append(df)
            i += 1

        merged_df = mergeDataframes(frames)
        if merged_df is not None:
            storage = ('<p class="auto-cursor-target"><br/></p> '
                       '<table> '
                       '<colgroup><col/><col/></colgroup>'
                       '<tbody> ' + dataframeToConfluence(merged_df) + ' </tbody> '
                       '</table> '
                       '<p><br/></p>')
            return storage
        else:
            return None
    except Exception as e:
        print(f"Error getting LR response from InfluxDB: {e}")
        return None



import pandas as pd

def get_lr_count_from_influx(run_id, stages):
    """
    Получает количество выполненных транзакций нагрузочного теста из InfluxDB для каждой стадии теста,
    объединяет результаты и преобразует их в формат Confluence Storage.

    :param run_id: идентификатор тестового прогона
    :param stages: список стадий теста с временем начала и окончания каждой стадии
    :return: количество выполненных транзакций нагрузочного теста в формате Confluence Storage
    """
    try:
        frames = []
        i = 0
        for stage in stages:
            start_time = str(int(stage[0]))
            end_time = str(int(stage[1]))
            df = getLRCountFromInflux(run_id, start_time, end_time, 'step ' + str(i))
            if df is not None:
                frames.append(df)
            i += 1

        merged_df = mergeDataframes(frames)
        if merged_df is not None:
            storage = ('<p class="auto-cursor-target"><br/></p> '
                       '<table> '
                       '<colgroup><col/><col/></colgroup>'
                       '<tbody> ' + dataframeToConfluence(merged_df) + ' </tbody> '
                       '</table> '
                       '<p><br/></p>')
            return storage
        else:
            return None
    except Exception as e:
        print(f"Error getting LR count from InfluxDB: {e}")
        return None



def get_lr_percentile_from_influx(run_id, stages):
    """
    Получает процентили времени отклика нагрузочного теста из InfluxDB для каждой стадии теста,
    объединяет результаты и преобразует их в формат Confluence Storage.

    :param run_id: идентификатор тестового прогона
    :param stages: список стадий теста с временем начала и окончания каждой стадии
    :return: процентили времени отклика нагрузочного теста в формате Confluence Storage
    """
    try:
        frames = []
        i = 0
        for stage in stages:
            start_time = str(int(stage[0]))
            end_time = str(int(stage[1]))
            df = getLRPercentileFromInflux(run_id, start_time, end_time, 'step ' + str(i))
            if df is not None:
                frames.append(df)
            i += 1

        merged_df = mergeDataframes(frames)
        if merged_df is not None:
            storage = ('<p class="auto-cursor-target"><br/></p> '
                       '<table> '
                       '<colgroup><col/><col/></colgroup>'
                       '<tbody> ' + dataframeToConfluence(merged_df) + ' </tbody> '
                       '</table> '
                       '<p><br/></p>')
            return storage
        else:
            return None
    except Exception as e:
        print(f"Error getting LR percentiles from InfluxDB: {e}")
        return None


def get_lr_MINMAXAVG_from_influx(run_id, stages):
    """
    Получает минимальное, максимальное и среднее время отклика нагрузочного теста из InfluxDB для каждой стадии теста,
    объединяет результаты и преобразует их в формат Confluence Storage.

    :param run_id: идентификатор тестового прогона
    :param stages: список стадий теста с временем начала и окончания каждой стадии
    :return: минимальное, максимальное и среднее время отклика нагрузочного теста в формате Confluence Storage
    """
    try:
        frames = []
        i = 0
        for stage in stages:
            start_time = str(int(stage[0]))
            end_time = str(int(stage[1]))
            df = getLRResponseMINMAXAVGFromInflux(run_id, start_time, end_time, 'step ' + str(i))
            if df is not None:
                frames.append(df)
            i += 1

        merged_df = mergeDataframes(frames)
        if merged_df is not None:
            storage = ('<p class="auto-cursor-target"><br/></p> '
                       '<table> '
                       '<colgroup><col/><col/></colgroup>'
                       '<tbody> ' + dataframeToConfluence(merged_df) + ' </tbody> '
                       '</table> '
                       '<p><br/></p>')
            return storage
        else:
            return None
    except Exception as e:
        print(f"Error getting LR MIN/MAX/AVG from InfluxDB: {e}")
        return None




def getLRResponseFromInflux(run_id, start_time, end_time, step):
    """
    Получает среднее время отклика тестов из InfluxDB для заданного временного интервала.

    :param run_id: идентификатор тестового прогона
    :param start_time: начальное время интервала в миллисекундах
    :param end_time: конечное время интервала в миллисекундах
    :param step: название стадии теста
    :return: DataFrame с средним временем отклика для каждой транзакции
    """
    try:
        # Подключение к базе данных InfluxDB
        client = InfluxDBClient(host='rbqacas00004.gts.rus.socgen', port=8086, username='pcuser', password='pcuser',
                                database='test')

        # Преобразование start_time и end_time из миллисекунд в строки формата InfluxDB
        start_time_str = datetime.fromtimestamp((((int(start_time) / 1000) - 3600 * 3) * 1000) / 1000).strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        end_time_str = datetime.fromtimestamp((((int(end_time) / 1000) - 3600 * 3) * 1000) / 1000).strftime(
            '%Y-%m-%dT%H:%M:%SZ')

        # Запрос данных по тесту
        query = f"SELECT * FROM es_tr_response_time WHERE QcRunId = '{run_id}' AND time >= '{start_time_str}' AND time <= '{end_time_str}'"
        result = client.query(query)

        # Конвертирование результатов в pandas DataFrame
        dataframe = pd.DataFrame(result["es_tr_response_time"]).rename(
            columns={"MeasurementName": "transaction_name"})

        # Группировка данных по названию транзакции
        grouped_dataframe = dataframe.groupby("transaction_name")

        # Расчет статистик: среднее значение
        mean_dataframe = grouped_dataframe["value"].mean().reset_index().rename(
            columns={"value": "mean_response_time" + '_' + step})
        mean_dataframe["mean_response_time" + '_' + step] = mean_dataframe["mean_response_time" + '_' + step].round(4)

        return mean_dataframe[['transaction_name', 'mean_response_time' + '_' + step]]

    except Exception as e:
        print(f"Error getting LR response from InfluxDB: {e}")
        return None



def getLRPercentileFromInflux(run_id, start_time, end_time, step):
    """
    Получает 90-й перцентиль времени отклика тестов из InfluxDB для заданного временного интервала.

    :param run_id: идентификатор тестового прогона
    :param start_time: начальное время интервала в миллисекундах
    :param end_time: конечное время интервала в миллисекундах
    :param step: название стадии теста
    :return: DataFrame с 90-м перцентилем времени отклика для каждой транзакции
    """
    try:
        # Подключение к базе данных InfluxDB
        client = InfluxDBClient(host='rbqacas00004.gts.rus.socgen', port=8086, username='pcuser', password='pcuser',
                                database='test')

        # Преобразование start_time и end_time из миллисекунд в строки формата InfluxDB
        start_time_str = datetime.fromtimestamp((((int(start_time) / 1000) - 3600 * 3) * 1000) / 1000).strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        end_time_str = datetime.fromtimestamp((((int(end_time) / 1000) - 3600 * 3) * 1000) / 1000).strftime(
            '%Y-%m-%dT%H:%M:%SZ')

        # Запрос данных по тесту
        query = f"SELECT * FROM es_tr_response_time WHERE QcRunId = '{run_id}' AND time >= '{start_time_str}' AND time <= '{end_time_str}'"
        result = client.query(query)

        # Конвертирование результатов в pandas DataFrame
        dataframe = pd.DataFrame(result["es_tr_response_time"]).rename(
            columns={"MeasurementName": "transaction_name"})

        # Группировка данных по названию транзакции
        grouped_dataframe = dataframe.groupby("transaction_name")

        # Расчет статистик: 90 перцентиль
        percentile_90_dataframe = grouped_dataframe["value"].quantile(0.9).reset_index().rename(
            columns={"value": "percentile_90_response_time" + '_' + step})
        percentile_90_dataframe["percentile_90_response_time" + '_' + step] = percentile_90_dataframe[
            "percentile_90_response_time" + '_' + step].round(4)

        return percentile_90_dataframe[['transaction_name', 'percentile_90_response_time' + '_' + step]]

    except Exception as e:
        print(f"Error getting LR 90th percentile from InfluxDB: {e}")
        return None



def getLRCountFromInflux(run_id, start_time, end_time, step):
    """
    Получает количество запросов из InfluxDB для заданного временного интервала.

    :param run_id: идентификатор тестового прогона
    :param start_time: начальное время интервала в миллисекундах
    :param end_time: конечное время интервала в миллисекундах
    :param step: название стадии теста
    :return: DataFrame с количеством тестов для каждой транзакции
    """
    try:
        # Подключение к базе данных InfluxDB
        client = InfluxDBClient(host='rbqacas00004.gts.rus.socgen', port=8086, username='pcuser', password='pcuser',
                                database='test')

        # Преобразование start_time и end_time из миллисекунд в строки формата InfluxDB
        start_time_str = datetime.fromtimestamp((((int(start_time) / 1000) - 3600 * 3) * 1000) / 1000).strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        end_time_str = datetime.fromtimestamp((((int(end_time) / 1000) - 3600 * 3) * 1000) / 1000).strftime(
            '%Y-%m-%dT%H:%M:%SZ')

        # Запрос данных по тесту
        query = f"SELECT * FROM es_tr_response_time WHERE QcRunId = '{run_id}' AND time >= '{start_time_str}' AND time <= '{end_time_str}'"
        result = client.query(query)

        # Конвертирование результатов в pandas DataFrame
        dataframe = pd.DataFrame(result["es_tr_response_time"]).rename(
            columns={"MeasurementName": "transaction_name"})

        # Группировка данных по названию транзакции
        grouped_dataframe = dataframe.groupby("transaction_name")

        # Расчет статистик: количество
        count_dataframe = grouped_dataframe["value"].count().reset_index().rename(
            columns={"value": "count" + '_' + step})
        count_dataframe["count" + '_' + step] = count_dataframe["count" + '_' + step].round(4)

        return count_dataframe[['transaction_name', 'count' + '_' + step]]

    except Exception as e:
        print(f"Error getting LR count from InfluxDB: {e}")
        return None



def getLRResponseMINMAXAVGFromInflux(run_id, start_time, end_time, step):
    """
    Получает минимальное, максимальное и среднее время ответа из InfluxDB для заданного временного интервала.

    :param run_id: идентификатор тестового прогона
    :param start_time: начальное время интервала в миллисекундах
    :param end_time: конечное время интервала в миллисекундах
    :param step: название стадии теста
    :return: DataFrame с минимальным, максимальным и средним временем ответа для каждой транзакции
    """
    try:
        # Подключение к базе данных InfluxDB
        client = InfluxDBClient(host='rbqacas00004.gts.rus.socgen', port=8086, username='pcuser', password='pcuser',
                                database='test')

        # Преобразование start_time и end_time из миллисекунд в строки формата InfluxDB
        start_time_str = datetime.fromtimestamp((((int(start_time) / 1000) - 3600 * 3) * 1000) / 1000).strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        end_time_str = datetime.fromtimestamp((((int(end_time) / 1000) - 3600 * 3) * 1000) / 1000).strftime(
            '%Y-%m-%dT%H:%M:%SZ')

        # Запрос данных по тесту
        query = f"SELECT * FROM es_tr_response_time WHERE QcRunId = '{run_id}' AND time >= '{start_time_str}' AND time <= '{end_time_str}'"
        result = client.query(query)

        # Конвертирование результатов в pandas DataFrame
        dataframe = pd.DataFrame(result["es_tr_response_time"]).rename(
            columns={"MeasurementName": "transaction_name"})

        # Группировка данных по названию транзакции
        grouped_dataframe = dataframe.groupby("transaction_name")

        # Расчет статистик: среднее значение, минимальное, максимальное
        mean_dataframe = grouped_dataframe["value"].mean().reset_index().rename(
            columns={"value": "mean_response_time"})
        min_dataframe = grouped_dataframe["value"].min().reset_index().rename(
            columns={"value": "min_response_time"})
        max_dataframe = grouped_dataframe["value"].max().reset_index().rename(
            columns={"value": "max_response_time"})

        mean_dataframe["mean_response_time"] = mean_dataframe["mean_response_time"].round(4)
        min_dataframe["min_response_time"] = min_dataframe["min_response_time"].round(4)
        max_dataframe["max_response_time"] = max_dataframe["max_response_time"].round(4)

        # Объединение результатов в один DataFrame
        summary_dataframe = pd.merge(mean_dataframe, min_dataframe, on="transaction_name")
        summary_dataframe = pd.merge(summary_dataframe, max_dataframe, on="transaction_name")

        summary_dataframe = summary_dataframe.rename(
            columns={"mean_response_time": "avg" + '_' + step, "min_response_time": "min" + '_' + step,
                     "max_response_time": "max" + '_' + step})

        return summary_dataframe[['transaction_name', "min" + '_' + step, "avg" + '_' + step, "max" + '_' + step]]
    except Exception as e:
        print(f"Ошибка при получении минимального, максимального и среднего времени ответа: {e}")
        return None





def getTransactionFromInflux(run_id, start_time, end_time):

    """
    Получает название транзакций из InfluxDB для заданного временного интервала и номера запуска.

    :param run_id: идентификатор тестового прогона
    :param start_time: начальное время интервала в миллисекундах
    :param end_time: конечное время интервала в миллисекундах
    :return: DataFrame с названиями транзакций
    """
    try:
        # Подключение к базе данных InfluxDB
        client = InfluxDBClient(host='rbqacas00004.gts.rus.socgen', port=8086, username='pcuser', password='pcuser',
                                database='test')

        # Преобразование start_time и end_time из миллисекунд в строки формата InfluxDB
        start_time_str = datetime.fromtimestamp((((int(start_time) / 1000) - 3600 * 3) * 1000) / 1000).strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        end_time_str = datetime.fromtimestamp((((int(end_time) / 1000) - 3600 * 3) * 1000) / 1000).strftime(
            '%Y-%m-%dT%H:%M:%SZ')

        # Запрос данных по тесту
        query = f"SELECT * FROM es_tr_response_time WHERE QcRunId = '{run_id}' AND time >= '{start_time_str}' AND time <= '{end_time_str}'"
        result = client.query(query)

        # Конвертирование результатов в pandas DataFrame
        dataframe = pd.DataFrame(result["es_tr_response_time"]).rename(
            columns={"MeasurementName": "transaction_name"})

        # Группировка данных по названию транзакции
        grouped_dataframe = dataframe.groupby("transaction_name")

        # Расчет статистик: количество
        count_dataframe = grouped_dataframe["value"].count().reset_index()

        count_dataframe.rename({'transaction_name': 'Operation'}, axis=1, inplace=True)
        count_dataframe = count_dataframe["Operation"]
        count_dataframe = count_dataframe.to_numpy()

        return count_dataframe
    except Exception as e:
        print(f"Ошибка при получении списка транзакций: {e}")
        return None





def dataframeToConfluence(df):

    """
    Конвертирует DataFrame в вид подходящий для добавления в Confluence.

    :param df: исходный DataFrame
    :return: String сданными из DataFrame
    """
    try:
        # Инициализация переменных
        columns = []
        columnsName = '<tr>'

        # Формирование строки с названиями столбцов
        for column in df.columns:
            columns.append(column)
            columnsName = str(columnsName) + '<th>' + str(column) + '</th>'
        columnsName = columnsName + '</tr>'

        # Формирование строк с данными
        columnsData = ''
        for index, row in df.iterrows():
            columnsData = columnsData + '<tr>'
            for column1 in columns:
                columnsData = str(columnsData) + '<td>' + str(row[column1]) + '</td>'
            columnsData = str(columnsData) + '</tr>'

        # Объединение названий столбцов и данных
        columnsData = columnsName + columnsData

        return columnsData
    except Exception as e:
        print(f"Ошибка при преобразовании DataFrame в HTML-таблицу для Confluence: {e}")
        return None




def get_test_time_steps(run_id):
    """
    Получает временные интервалы по каждой ступени теста из InfluxDB для заданного идентификатора тестового прогона.

    :param run_id: идентификатор тестового прогона
    :return: DataFrame с  временем начала и окончания каждой ступени теста
    """
    try:
        print("Method getInfluxDatetimeOfSteps starts")

        # Подключение к базе данных InfluxDB
        client = InfluxDBClient(host='rbqacas00004.gts.rus.socgen', port=8086, username='pcuser', password='pcuser',
                                database='test')

        # Запрос данных о временных шагах теста
        query_full_test = f"SELECT * FROM es_tr_runtime_vusers WHERE QcRunId = '{run_id}';"
        result_full_test = client.query(query_full_test, params={'epoch': 'ms'})

        steps = []
        points = list(result_full_test.get_points())

        users = 0
        i = 0
        for index, item in enumerate(points):
            if index == 0:
                users = int(item['value'])
                steps.append([item['time'], users])
                i += 1
                continue

            current_users = int(item['value'])

            if current_users != users:
                users = current_users
                steps[i - 1].append(item['time'])
                steps.append([item['time'], users])
                i += 1

            if index == len(points) - 1 and current_users == users:
                steps[i - 1].append(item['time'])
                steps.append([item['time'], users])
                continue

        client.close()

        df = pd.DataFrame(steps, columns=['TimeStepStart', 'CountOfUsers', 'TimeStepEnd'])
        df['Duration, sec'] = (df['TimeStepEnd'] - df['TimeStepStart']) / 1000
        steps_array = df[df['Duration, sec'] > 1100]
        steps_array.reset_index(drop=True, inplace=True)

        for i in range(len(steps_array.index)):
            difference = steps_array.iloc[i, 3] % 300 * 1000

            if (difference % 2 == 0):
                steps_array.iloc[i, 0] += difference / 2
                steps_array.iloc[i, 2] -= difference / 2
                steps_array.iloc[i, 3] = (steps_array.iloc[i, 2] - steps_array.iloc[i, 0]) / 1000
            else:
                steps_array.iloc[i, 0] += (difference / 2 + 1000)
                steps_array.iloc[i, 2] -= difference / 2
                steps_array.iloc[i, 3] = (steps_array.iloc[i, 2] - steps_array.iloc[i, 0]) / 1000

        steps = steps_array[['TimeStepStart', 'TimeStepEnd']].values.tolist()

        steps = [[int(item) for item in sublist] for sublist in steps]

        return steps
    except Exception as e:
        print(f"Ошибка при получении временных шагов теста из InfluxDB: {e}")
        return None



def get_test_data_time(run_id):
    """
    Получает временной интервал начала и окончания теста из InfluxDB для заданного идентификатора тестового прогона.

    :param run_id: идентификатор тестового прогона
    :return: DataFrame с временным интервалом начала и окончания теста
    """
    try:
        # Замените значения ниже на соответствующие значения для вашей базы данных InfluxDB
        measurement_name = "es_tr_response_time"
        client = InfluxDBClient(host='rbqacas00004.gts.rus.socgen', port=8086, username='pcuser', password='pcuser',
                                database='test')

        # Запрос для получения всех данных для данного run_id
        query = f'SELECT * FROM "{measurement_name}" WHERE "QcRunId" = \'{run_id}\''
        result = client.query(query)

        points = list(result.get_points())

        if points:
            # Преобразование данных в DataFrame
            df = pd.DataFrame(points)

            # Нахождение времени начала и окончания теста
            start_time = df['time'].min()
            end_time = df['time'].max()

            start_time = int(pd.to_datetime(start_time).timestamp())
            end_time = int(pd.to_datetime(end_time).timestamp())
            test_time = [start_time, end_time]

            print(f"Start time: {start_time}, End time: {end_time}")
        else:
            print(f"No data found for run_id: {run_id}")
            test_time = None

        return test_time
    except Exception as e:
        print(f"Ошибка при получении данных о времени теста из InfluxDB: {e}")
        return None



def getTransactionsByRunID(project, runID, transactions_filter):
    print("Method getTransactionsByRunID starts")

    # Initializing the LRE params of the project
    # host, port, username, password, dbname = initLREParam(project)
    client = InfluxDBClient(host='rbqacas00004.gts.rus.socgen', port=8086, username='pcuser', password='pcuser',
                            database='test')


    # client = InfluxDBClient(host, port, username, password, dbname)
    allSeries = client.get_list_series(database='test', measurement='es_tr_response_time', tags={'QcRunId': runID})
    transactionsList = []
    for item in allSeries:
        # print(item)
        transaction = re.search('MeasurementName=(.*?),', item).group(
            1)  # We need group to exclude all others from searched phrase
        # print(transaction)
        if transactions_filter:
            if transaction in ['Actions_Transaction', 'Action_Transaction', 'vuser_end_Transaction', 'vuser_init_Transaction']:
                continue
            else:
                if project in ["BIS"]:
                    transaction = transaction[:4]
                transactionsList.append(transaction)
        else:
            if project in ["BIS"]:
                transaction = transaction[:4]
            transactionsList.append(transaction)
    print("We have the transactions list")
    # print(transactionsList)

    client.close()
    transactionsList.sort()

    return transactionsList

