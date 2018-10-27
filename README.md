## Wymagania

- VirtualBox (https://www.virtualbox.org/)
- Vagrant 2.0 lub nowszy (https://www.vagrantup.com/)

## Pobranie źródeł

Sklonuj repozytorium `backend`:

```bash
git clone https://gitlab.dane.gov.pl/mcod/backend.git
```

Przejdź do katalogu z projektem `backend` i sklonuj repozytoria `test-data` oraz `frontend`:

```bash
cd backend
git clone https://gitlab.dane.gov.pl/mcod/test-data.git
git clone https://gitlab.dane.gov.pl/mcod/frontend.git
```

## Budowanie środowiska lokalnego

W katalogu z projektem `backend` wykonaj:
```bash
vagrant up --provision
```

Proces budowania środowiska może trwać nawet kilkadziesiąt minut.

## Ustawienia lokalne
Otwórz plik /etc/hosts (lub C:\Windows\System32\Drivers\etc w systemie MS Windows) jako root (lub administrator) i dodaj do niego następujące linie:
```bash
172.28.28.28 mcod.local
172.28.28.28 www.mcod.local
172.28.28.28 api.mcod.local 
172.28.28.28 svr.mcod.local 
```

## Uruchomienie/zatrzymanie środowiska lokalnego
Aby uruchomić środowisko lokalne, w katalogu projektu `backend` wykonaj:
```bash
vagrant up
```
Aby zatrzymać środowisko lokalne, w katalogu projektu `backend` wykonaj:
```bash
vagrant halt
```

## Uruchomienie/zatrzymywanie usług (supervisor)
Po uruchomieniu środowiska lokalnego, otwórz przeglądarkę WWW i przejdź do adresu http://svr.mcod.local by otworzyć panel zarządzania usługami.

Korzystając z panelu, uruchom/zatrzymaj wybrane, bądź wszystie usługi.

#### Usługa admin
Po uruchomieniu usługi, pod adresem http://admin.mcod.local będzie dostępny panel administracyjny (login: admin@mcod.local, hasło: Otwarte.1)

#### Usługa api
Po uruchomieniu usługi pod adresem http://api.mcod.local bedzie dostępne API projektu.

#### Usługa frontend
Po uruchomieniu usługi, po upływie ok 1 minuty, pod adresem http://www.mcod.local bedzie dostępna aplikacja WWW - portal Otwarte Dane. 

Do prawidłowego funkcjonowania niezbędne jest uruchomienie usługi API.

#### Usługa celery
Uruchomienie usługi jest niezbędne, jeżeli zamierzamy korzystać z zadań asynchronicznych, takich jak wysyłanie mailu czy walidacja plików zasobów.

## Ręcznie uruchamianie usług
W katalogu z projektem `backend` wykonaj poniższe polecenia by zalogować się na maszynę wirtualną środowiska lokalnego i uruchomić VirtualEnv projektu:

```bash
vagrant ssh
supervisorctl stop 
workon mcod
```
Za pomocą polecenia `pwd` sprawdź, czy jesteś w katalogu `/vagrant`

Wszystkie poniższe polecenia wykonujemy na maszynie wirtualnej, w środowisku virtuaenv i z katalogu `/vagrant`.

#### Uruchamianie API
Upewnij się, że na porcie 8000 nie jest uruchomiona żadna instancja API
```bash
supervisorctl stop api
netstat -nltp | grep 8000
```
By uruchomić API wykonaj
```bash
python mcod.api.py
```
API będzie dostępne na hoście pod następującymi adresami:
- http://172.28.28.28:8000/
- http://api.mcod.local
- http://mcod.local:8000
- http://api.mcod.local:8000

#### Uruchamianie panelu administracyjnego
Upewnij się, że na porcie 8080 nie jest uruchomiona żadna instancja panelu administracujnego
```bash
supervisorctl stop admin
netstat -nltp | grep 8080
```
By uruchomić panel administracyjny, wykonaj
```bash
python manage.py runserver 0:8080
```
Aplikacja będzie dostępna na hoście pod następującymi adresami:
- http://172.28.28.28:8080/
- http://admin.mcod.local
- http://mcod.local:8080
- http://admin.mcod.local:8080

#### Uruchamianie aplikacji WWW (frontendu)
Upewnij się, że na porcie 8081 nie jest uruchomiona żadna instancja aplikacji WWW.
```bash
supervisorctl stop admin
netstat -nltp | grep 8080
```
By uruchomić aplikację WWW wykonaj:
```bash
/vagrant/frontend/node_modules/.bin/ng serve --host 0.0.0.0 --port 8081 --proxy-config /vagrant/frontend/local-proxy.conf.json
```
Aplikacja będzie dostępna na hoście pod następującymi adresami:
- http://172.28.28.28:8081/
- http://www.mcod.local
- http://mcod.local:8081

#### Uruchamianie celery
Upewnij się, że nie są uruchomione inne instance celery
```bash
supervisorctl stop celery
```
By uruchomić celery, wykonaj
```bash
celery --app=mcod.celeryapp:app worker -B -l info
```

## Inne przydatne polecenia
Wszystkie poniższe polecenia wykonujemy na maszynie wirtualnej, w środowisku virtuaenv i z katalogu `/vagrant`.

##### Uruchamianie testów jednostkowych
```bash
pytest mcod
```
##### Reindeksacja wszystkich danych
```bash
python manage.py search_index --rebuild -f
```

##### Ponowna walidacja zasobu
```bash
python manage.py validate_resources --pks <id_1,...,id_N>
```

##### Zaindeksowanie pliku zasobu (wygenerowanie danych tabelarycznych)
```bash
python manage.py index_file --pks <id_1,...,id_N>
```
