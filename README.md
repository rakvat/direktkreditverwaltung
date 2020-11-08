# Direktkreditverwaltung

Nach Erfordernissen eines Mietshäuser Syndikat Projekts.

## Features

### Verwaltet

- Kontaktdaten
- Verträge
- Versionen von Verträgen (Laufzeiten und Zinssatz kann sich ändern)
- Buchungen

### Erstellt

- Kontoauszüge
- Zinsberechnungen
- Vertragsübersicht nach Auslaufdatum

### Zinsberechnung

- nach 30/360 (Europäische Methode)

### PDF Ausgaben

- Für Zinsübersicht, Zinsbriefe und Dankesbriefe.
- Kann mit Bildern und Textsnippets angepasst werden.

## Setup

- Use a modern python version.
- `pip install -r reqirements.txt`
- In `dkapp/static/custom/` are three template files which are used for the PDF generation. Copy the files in the same location removing the `_template` from the filename. Replace the copied fieles with your content.
- `python manage.py collectstatic` copies static files (e.g. your custom files) to the root folder.
- `python manage.py runserver` starts the server.
- Access http://localhost:8000/ in your browswer and enter some data.

### Migrate from [the Rails Version](https://github.com/rakvat/direktkreditverwaltung_deprecated)

If you used [the now deprecated Rails version](https://github.com/rakvat/direktkreditverwaltung_deprecated) before, you can migrate like this:

- find the .sqlite3 file of the rails app
- run `python manage.py import_from_rails_app rails_app_sqlite.sqlite3`
