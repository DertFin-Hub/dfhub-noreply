# DFHub NoReply
**DFHub NoReply** - сервис DFHub, отвечающий за отправку электронных почтовых писем.

## Установка
Клонируйте репозиторий к себе на компьютер:  
```bash
git clone https://github.com/DertFin-Hub/dfhub-noreply.git
```

Настройте `config.json`, указав следующие параметры:  
`public-address` - публичный адрес сервера, на который будут поступать запросы  
`port` - порт сервера  
`smtp-address`- адресс [SMTP](https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol)-сервера  
`smtp-port` - порт SMTP-сервера. Обычно - `587`  
`accessed-ips` - вайтлист адресов, с которых можно отправлять запросы на Ваш сервер  
`is-ssl` - использует ли SMTP-сервер SSL *(по-стандарту false - используется TLS)*  

`https.enables` - использовать ли SSL для DFHub-NoReply  
`https.cert-file` - путь к `.pem` файлу с сертификатом  
`https.key-file` - путь к приватному `.pem`-ключу от сертификата  

Создайте файл `.env` в той же директории, что и сама программа и укажите следующие параметры:
```.env
DFHUB_NOREPLY_APP_MAIL=ваша_почта
DFHUB_NOREPLY_APP_TOKEN=пароль_вашего_приложения
```

ВАЖНО! `APP_TOKEN` - это не пароль от вашей почты, а пароль для авторизации приложений, который создается отдельно на
сервисе, через который создана почта *(обычно требует верификации)*

## Запуск

Скачайте Python:
```bash
apt install python3 python3-pip -y
```

Установите зависимости:
```bash
pip install -r requirements.txt
```

Запустите приложение:
```bash
python3 main.py
```

## Использование

Для проверки перейдите на главную страницу `/`. Если вы получили ошибку браузера, то приложение запущено неверно. 
Если вы получили ошибку сайта, то, вероятно, ваш IP не добавлен в `accessed_ips` в конфигурации. Если вы увидели *"DFHub-NoReply active"*, 
то приложение запущено успешно.

Все адреса, предназначенные для отправки сообщений работают только с методом `POST`. Для каждого из них нужен JSON с 
определенными параметрами, отличающимися в зависимости от требований.

### Send-Raw
`/api/v1/send-raw` - отправляет сообщение с сырым текстом. Вот список JSON-параметров, которые нужны для его отправки:

`to` - почта получателя  
`subject` - тема сообщения  
`context` - cодержимое сообщения  

### Send-HTML
`/api/v1/send-html` - отправляет сообщение с текстом, который поддерживает форматирование в формате html.

Требует такие же параметры, что и `send-raw`

### Send-HTML-url
`/api/v1/send-html-url` - отправляет сообщение с текстом, который поддерживает форматирование в формате html. Текст не
передается в запросе, а достается по ссылке, указанной в нем. Для данного запроса нужны следующие параметры:

`to` - почта получателя  
`subject` - тема сообщения  
`attachment-url` - ссылка на ресурс с прикрепляемым контентом

## Запуск с Docker

Скачайте образ:
```bash
docker pull dertfin1/dfhub-noreply
```

Скачайте стандартный конфиг:
```bash
wget -O config.json https://raw.githubusercontent.com/DertFin-Hub/dfhub-noreply/refs/heads/master/config.json
# или
curl -o config.json https://raw.githubusercontent.com/DertFin-Hub/dfhub-noreply/refs/heads/master/config.json
```

Настройте конфиг, как указано выше

Запустите образ, смонтировав Ваш конфиг и указав данные авторизации для SMTP-сервера в переменных окружения:
```bash
docker run \
  -v /path/to/config.json:/app/config.json \
  -e DFHUB_NOREPLY_APP_MAIL=mail@example.com \
  -e DFHUB_NOREPLY_APP_TOKEN=your_application_auth_token \
  dertfin1/dfhub-noreply
```

`/path/to/config.json` - **полный** путь к настроенному конфигу. `/app/config.json` трогать не нужно  
`mail@exaple.com` - электронная почта, с которой будут отправляться сообщения  
`your_application_auth_token` - токен авторизации для приложения  

При необходимости можно добавить `--restart=always`.

