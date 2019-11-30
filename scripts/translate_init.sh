pybabel extract -F babel.cfg -k _l -o messages.pot .
pybabel init -i messages.pot -d translations --locale zh
pybabel init -i messages.pot -d translations --locale zh_Hant
pybabel compile -d translations
