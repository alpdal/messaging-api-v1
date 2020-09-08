# Offline Messaging API

Döküman:
https://documenter.getpostman.com/view/10885838/TVCiSkkM

#### Gereklilikler
```sh
pip3 install virtualenv
```

## Kurulum 
```sh
$ git clone https://github.com/alpdal/messaging-api-v1
$ cd messaging-api-v1
$ python3 -m venv env
$ source env/bin/activate
$ pip3 install -r requirements.txt
$ python manage.py runserver    
```

#### Superuser yaratmak ve admin paneline erişim

```sh
$ python3 manage.py createsuperuser
```
  http://127.0.0.1:8000/admin/

#### Allowed_host eklemek için

```sh
# offline_messaging/settings.py

ALLOWED_HOSTS = ['127.0.0.1']
```

## Test

- %10 test covarage.
- api/tests.py 3 test içeriyor.

```sh
$ python3 manage.py test
```

![alt text](https://armut-case.s3.eu-central-1.amazonaws.com/test.png)

## Notlar

- Kullanıcı aktiviteleri log/activity.log'da tutuluyor.
- Geçmişe dönük mesaj görüntülenmelerinde tarih/kişi kategorizyonu ve sayfalandırma yapılabilir.
- Mesaj iletilme/okunma zamanları kaydediliyor ve gönderen kullanıcı tarafından görülebilir. 
