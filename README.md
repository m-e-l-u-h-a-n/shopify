# Shopify

This repository holds the source code for project **Shopify** for the CSE-205N course at IIT(BHU).

## Getting started

Development:

1. Fork the repo and clone it to your system.
2. Configure your .env variables
3. Move to project directory in your terminal and run `pipenv shell` to start the project's virtual environment.(If pipenv is not installed run `pip install pipenv` and then use `pipenv shell`). It will also load environment variables required for the project.
4. Run `pipenv install` to download the project's dependencies.
5. Now start the development server using `python manage.py runserver`.
6. In case there is an error regarding settings moule not configured on above steps run `export DJANGO_SETTINGS_MODULE=djecommerce.settings` on your terminal.
