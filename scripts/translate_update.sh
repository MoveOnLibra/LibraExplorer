pybabel extract --add-location=file -F babel.cfg -k _l -o messages.pot .
pybabel update -i messages.pot -d translations --omit-header
pybabel compile -f -d translations
