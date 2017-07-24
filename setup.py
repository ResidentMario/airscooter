from setuptools import setup, find_packages

setup(
    name='airscooter',
    version='0.0.1',
    install_requires=['apache-airflow', 'pyaml', 'click', 'click-plugins'],
    packages=find_packages(),
    include_package_data=True,
    entry_points='''
        [console_scripts]
        airscooter=airscooter.cli:cli
    ''',
    description='Simple data processing task graph manager for Python.',
    author='Aleksey Bilogur',
    author_email='aleksey.bilogur@gmail.com',
    url='https://github.com/ResidentMario/airscooter',
    download_url='https://github.com/ResidentMario/airscooter/tarball/0.0.1',
    keywords=['data', 'data analysis', 'data science', 'task graph'],
    classifiers=[]
)