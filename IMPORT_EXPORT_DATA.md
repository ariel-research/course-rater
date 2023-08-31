## Importing & Exporting database
#### 1. Save the database to a JSON file:
`python manage.py dumpdata > datadump.json`
#### 2. Open the 'datadump.json' file:
1. Delete the first line: "import signals..."
2. Search for and remove any "link counter" entities.
#### 3. If you prefer, you can change 'settings.py' to use a different database.
> For MySQL, ensure you can connect successfully (permissions, etc.).

#### 4. Run the following command:
`python manage.py migrate`
#### 5. Exclude ContentType data using the following snippet in the shell:

`python manage.py shell`

    from django.contrib.contenttypes.models import ContentType
    ContentType.objects.all().delete()
    quit()

`python manage.py loaddata datadump.json`

#### 6. The database is now loaded.
> Credit: https://stackoverflow.com/a/41045999
