release: python -m nltk.downloader punkt wordnet stopwords && python manage.py migrate
web: gunicorn cashjournal.wsgi --log-file - 
