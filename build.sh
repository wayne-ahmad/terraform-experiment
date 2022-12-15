rm deploy.zip
rm -rf package
pip install --target ./package -r requirements.txt
cp -r dataquery_processor ./package
cp deploy/* ./package
# Hack for Python 3.7 and old version of importlib - it can't find
# resources withhout __init__.py. Newer versions can't find them
# when we do include it!
touch ./package/metadata_specifications/metadata/__init__.py
cd package || exit
zip -r ../deploy.zip .
cd .. || exit
zip -g deploy.zip lambda_function.py
rm -rf package