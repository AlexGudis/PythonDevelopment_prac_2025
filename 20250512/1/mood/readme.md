# Запуск сервера:
`python3 -m mood.server`

# Запуск клиента
`python3 -m mood.client <client_name>`


## Порядок работы с документацией:



## Порядок работы с переводами:
- Извлекаем строки для перевода


`pybabel extract -F babel.cfg -o messages.pot .`

- Инициализируем русский перевод

`pybabel init -i messages.pot -d locales -l ru`

- Открываем файл и добавляем вручную переводы

`locales/ru/LC_MESSAGES/messages.po`

- Компилируем переводы

`pybabel compile -d locales`


## Для обновлений в будущем:
- Извлекаем новые строки после изменения кода
  
`pybabel extract -F babel.cfg -o messages.pot .`

- Обновляем существующие переводы
  
`pybabel update -i messages.pot -d locales`

- Редактируем .po файл и компилируем:
  
`pybabel compile -d locales`