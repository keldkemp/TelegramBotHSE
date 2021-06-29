<b>Телеграм бот для расписания ВШЭ.</b>

<b>Описание:</b><br>
Позволяет получать информацию о расписании группы(групп).
Есть возможность добавить в общий чат.

<b>Инструкция по установке:</b><br>
Для работы необходима БД PostgreSQL.
1) необходимо создать в корне проекта файл settings.json и заполнить.<br>
`{
  "telegram_token": "token",
  "db_name": "db_name",
  "db_user": "db_user",
  "db_password": "db_pass",
  "host": "host"
}`<br>
2) Запускать программу из файла main.py<br>
3) Для автоматического обновления расписания - создать крон на выполнение UpdateTimeTable.py<br>
