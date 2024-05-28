from fast_bitrix24 import Bitrix
import datetime
from config import webhook

bitrix = Bitrix(webhook)


def get_all_deal_info():
    """ Получение "ID сделки"""
    try:
        deals = bitrix.get_all('crm.deal.list', params={
            'select': ['ID'],
            'filter': {
                'CLOSED': 'N',  # Все открытые сделки
                'CATEGORY_ID': ['1', '11', '13', '15', '19', '29', '31', '35', '37']  # Все воронки Касымовой
            }
        })
        return deals
    except Exception as ex:
        return f'Ошибка при выполнении запроса', ex


def get_tasks_for_deal(deal_id):
    try:
        deals = bitrix.get_all('tasks.task.list', params={
            'select': ['ID', 'TITLE'],
            'filter': {
                'UF_CRM_TASK': 'D_' + str(deal_id)
            }
        })
        return deals
    except Exception as ex:
        return f'Ошибка при выполнении запроса', ex


def get_deal_info(deal_id):
    """ Функция предоставляющая информацию о сделке в Битриксе по ID"""
    assigned_by_id = bitrix.call('crm.deal.get', {"ID": deal_id}, raw=True)['result']['ASSIGNED_BY_ID']
    return assigned_by_id


def create_bitrix_task_os(deal_id):
    try:
        """ Функция создающая задачу в сделке Битрикса. На вход принимает ID сделки, номер папки для скачивания и, при наличии, текст дополнительного комментария"""
        responsible_user = get_deal_info(deal_id)
        deal_link = f"https://trubexp.bitrix24.ru/crm/deal/details/{deal_id}/"
        data = {'fields': {
            'TITLE': "Внимание! Ты сейчас все потеряешь! У тебя сделка без задач!",
            'DESCRIPTION': f"Сделка №{deal_id}. Ссылка на сделку: {deal_link}",
            'STATUS': 2,
            'CREATED_BY': 1,
            'RESPONSIBLE_ID': int(responsible_user),
            'CREATED_DATE': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'DEADLINE': (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            'UF_CRM_TASK': [f'D_{deal_id}']
        }}
        bitrix.call('tasks.task.add', data)
    except Exception as ex:
        print('create_bitrix_task_os', ex)


def main():
    """ Функция запускающая проверку наличия задач в активных сделках Битрикса"""
    all_deals = get_all_deal_info()
    active_statuses = ['2', '3', '4', '6']  # Список активных статусов
    
    for deal in all_deals:
        company_id = deal['ID']
        tasks = get_tasks_for_deal(company_id)

                if not tasks:  # Если список задач пуст
            # create_bitrix_task_os(company_id)  # Создание новую задачи
            print(f'Создание новой задачи для сделки {company_id} где не было задач')
        else:
            for task in tasks:
                if task['status'] in active_statuses:  # Если статусы, кроме "завершена"
                    break  # Задача найдена, выходим из цикла
            else:  # Если цикл завершился без break, значит задач с активнми статусами нет
                # create_bitrix_task_os(company_id)  # Создание новую задачи
                print(f'Создание новой задачи для сделки {company_id} с завершенными задачами')


if __name__ == '__main__':
    create_bitrix_task_os(55599)
