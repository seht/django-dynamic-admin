import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-dynamic-admin',
    version='0.3.0-alpha.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Create dynamic models from Django administration',
    long_description=README,
    url='https://github.com/seht/django-dynamic-admin',
    author='Seht',
    author_email='seht@hyx.net',
    install_requires=[
        'django>=2.0',
        'django-polymorphic>=2.0',
    ],
    python_requires='>=3.5',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
