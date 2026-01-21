import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent


VERSION = '1.9.1'
PACKAGE_NAME = 'lanusstats'
AUTHOR = 'Federico Rábanos'
AUTHOR_EMAIL = 'lanusstats@gmail.com'
URL = 'https://github.com/federicorabanos'

LICENSE = 'MIT'
DESCRIPTION = 'Python library for scraping football data and visualize it / Libreria de Python para scrapear data de fútbol y visualizarla'
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding='utf-8')
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'pandas', 'mplsoccer', 'requests', 'matplotlib', 'numpy', 'bs4', 'Pillow', 'faker', 'undetected_chromedriver'
      ]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True,
    package_data={'LanusStats': ['fonts/*.ttf']}
)

