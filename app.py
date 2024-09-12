from flask import Flask, request, redirect, url_for, render_template
import smtplib
from email.mime.text import MIMEText
import schedule
import time
import threading
import pandas as pd
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Функция для загрузки данных из файла
def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = file.readlines()
        return [line.strip() for line in data]
    except FileNotFoundError:
        return []

# Инициализация файлов данных
tasks = load_data('tasks.txt')
reports = load_data('reports.txt')
absences = load_data('absences.txt')
contracts = load_data('contracts.txt')

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks, reports=reports, absences=absences, contracts=contracts)

@app.route('/add_task', methods=['POST'])
def add_task():
    task = request.form.get('task')
    if task:
        tasks.append(task)
        with open('tasks.txt', 'a', encoding='utf-8') as file:
            file.write(task + '\n')
    return redirect(url_for('index'))

@app.route('/complete_task/<int:task_id>', methods=['GET'])
def complete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        with open('tasks.txt', 'w', encoding='utf-8') as file:
            for task in tasks:
                file.write(task + '\n')
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>', methods=['GET'])
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        with open('tasks.txt', 'w', encoding='utf-8') as file:
            for task in tasks:
                file.write(task + '\n')
    return redirect(url_for('index'))

@app.route('/add_report', methods=['POST'])
def add_report():
    report = request.form.get('report')
    if report:
        reports.append(report)
        with open('reports.txt', 'a', encoding='utf-8') as file:
            file.write(report + '\n')
    return redirect(url_for('index'))

@app.route('/add_absence', methods=['POST'])
def add_absence():
    employee = request.form.get('employee')
    type_absence = request.form.get('type_absence')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    if employee and type_absence and start_date and end_date:
        absence = f'{employee} - {type_absence} - {start_date} по {end_date}'
        absences.append(absence)
        with open('absences.txt', 'a', encoding='utf-8') as file:
            file.write(absence + '\n')
    return redirect(url_for('index'))

@app.route('/add_contract', methods=['POST'])
def add_contract():
    contract_name = request.form.get('contract_name')
    end_date = request.form.get('end_date')
    if contract_name and end_date:
        contract = f'{contract_name} - {end_date}'
        contracts.append(contract)
        with open('contracts.txt', 'a', encoding='utf-8') as file:
            file.write(f'{contract}\n')
    return redirect(url_for('index'))

@app.route('/generate_timesheet', methods=['GET'])
def generate_timesheet():
    absences = load_data('absences.txt')
    tasks = load_data('tasks.txt')
    contracts = load_data('contracts.txt')
    
    timesheet = "Табель учета рабочего времени\n\n"
    timesheet += "Задачи:\n"
    for task in tasks:
        timesheet += f'{task}\n'
    
    timesheet += "\nОтсутствия:\n"
    for absence in absences:
        timesheet += f'{absence}\n'
    
    timesheet += "\nДоговоры:\n"
    for contract in contracts:
        timesheet += f'{contract}\n'
    
    # Сохранение сгенерированного табеля в файл
    with open('timesheet.txt', 'w', encoding='utf-8') as file:
        file.write(timesheet)
    
    return redirect(url_for('index'))

@app.route('/send_email', methods=['POST'])
def send_email():
    recipient = request.form.get('email')
    subject = request.form.get('subject')
    body = request.form.get('body')
    
    # Настройки для отправки email
    smtp_server = 'smtp.mail.ru'
    smtp_port = 587
    smtp_user = 'viktoriya_popova0312@mail.ru'  # Замените на ваш email
    smtp_password = 't43k6zpZrLWY4gLqE5iX'  # Замените на пароль приложения

    # Создание сообщения
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = recipient
    
    # Отправка сообщения
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return redirect(url_for('index'))
    except Exception as e:
        return str(e)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        search_results = []
        
        # Поиск в задачах
        for task in tasks:
            if query.lower() in task.lower():
                search_results.append(f'Задача: {task}')
        
        # Поиск в отчетах
        for report in reports:
            if query.lower() in report.lower():
                search_results.append(f'Отчет: {report}')
        
        # Поиск в отсутствиях
        for absence in absences:
            if query.lower() in absence.lower():
                search_results.append(f'Отсутствие: {absence}')
        
        # Поиск в договорах
        for contract in contracts:
            if query.lower() in contract.lower():
                search_results.append(f'Договор: {contract}')
        
        return render_template('search_results.html', query=query, results=search_results)
    return redirect(url_for('index'))

@app.route('/upload_timesheet', methods=['POST'])
def upload_timesheet():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.xlsx'):
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        
        # Чтение данных из Excel
        df = pd.read_excel(file_path)
        
        # Пример обработки данных из Excel
        timesheet_data = df.to_dict(orient='records')
        
        # Здесь можно добавить код для преобразования данных в формат табеля и сохранения
        # Пример преобразования:
        timesheet = "Табель учета рабочего времени\n\n"
        for record in timesheet_data:
            timesheet += f"Сотрудник: {record.get('Сотрудник')}, Время: {record.get('Время')}\n"
        
        with open('timesheet_from_excel.txt', 'w', encoding='utf-8') as file:
            file.write(timesheet)
        
        return redirect(url_for('index'))
    
    return "Неверный формат файла"

# Функция для проверки сроков задач и отчетов
def check_deadlines():
    today = datetime.now().date()
    
    for task in tasks:
        if 'дедлайн' in task:
            try:
                # Пример проверки дедлайна (нужно доработать под ваш формат)
                deadline_date_str = task.split('дедлайн: ')[1]
                deadline_date = datetime.strptime(deadline_date_str, '%Y-%m-%d').date()
                if deadline_date == today:
                    send_email('Напоминание о задаче', f'Напоминаем, что сегодня срок выполнения задачи: {task}', 'viktoriya_popova0312@mail.ru')
                elif deadline_date == today - timedelta(days=10):
                    send_email('Напоминание о задаче за 10 дней', f'Напоминаем, что осталось 10 дней до срока выполнения задачи: {task}', 'viktoriya_popova0312@mail.ru')
                elif deadline_date == today - timedelta(days=7):
                    send_email('Напоминание о задаче за 7 дней', f'Напоминаем, что осталось 7 дней до срока выполнения задачи: {task}', 'viktoriya_popova0312@mail.ru')
            except ValueError:
                print(f"Ошибка формата даты в задаче: {task}")

    for report in reports:
        if 'дедлайн' in report:
            try:
                # Пример проверки дедлайна (нужно доработать под ваш формат)
                deadline_date_str = report.split('дедлайн: ')[1]
                deadline_date = datetime.strptime(deadline_date_str, '%Y-%m-%d').date()
                if deadline_date == today:
                    send_email('Напоминание о отчете', f'Напоминаем, что сегодня срок подачи отчета: {report}', 'viktoriya_popova0312@mail.ru')
                elif deadline_date == today - timedelta(days=10):
                    send_email('Напоминание о отчете за 10 дней', f'Напоминаем, что осталось 10 дней до срока подачи отчета: {report}', 'viktoriya_popova0312@mail.ru')
                elif deadline_date == today - timedelta(days=7):
                    send_email('Напоминание о отчете за 7 дней', f'Напоминаем, что осталось 7 дней до срока подачи отчета: {report}', 'viktoriya_popova0312@mail.ru')
            except ValueError:
                print(f"Ошибка формата даты в отчете: {report}")

    for contract in contracts:
        try:
            # Извлекаем дату окончания договора из строки
            _, end_date_str = contract.rsplit(' - ', 1)
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if end_date == today:
                send_email('Напоминание о договоре', f'Напоминаем, что сегодня срок заключения договора: {contract}', 'viktoriya_popova0312@mail.ru')
            elif end_date == today - timedelta(days=10):
                send_email('Напоминание о договоре за 10 дней', f'Напоминаем, что осталось 10 дней до срока заключения договора: {contract}', 'viktoriya_popova0312@mail.ru')
            elif end_date == today - timedelta(days=7):
                send_email('Напоминание о договоре за 7 дней', f'Напоминаем, что осталось 7 дней до срока заключения договора: {contract}', 'viktoriya_popova0312@mail.ru')
        except ValueError:
            print(f"Ошибка формата даты в договоре: {contract}")

# Функция для планирования проверки дедлайнов
def schedule_tasks():
    schedule.every().day.at("09:00").do(check_deadlines)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# Запуск планировщика в отдельном потоке
scheduler_thread = threading.Thread(target=schedule_tasks)
scheduler_thread.daemon = True
scheduler_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
