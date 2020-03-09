from setuptools import setup

setup(
    name='pyta_server',
    packages=['pyta_server'],
    include_package_data=True,
    install_requires=[
        'flask', 'flask_sqlalchemy',
    ],
)
