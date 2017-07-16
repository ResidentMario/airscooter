from setuptools import setup, find_packages

setup(
    name='datablocks',
    version='0.0.1',
    install_requires=['apache-airflow', 'pyaml', 'click'],
    packages=find_packages(),
    include_package_data=True,
    entry_points='''
        [console_scripts]
        datablocks=datablocks.cli:cli
    ''',
    description='Simple data processing task graph manager for Python.',
    author='Aleksey Bilogur',
    author_email='aleksey.bilogur@gmail.com',
    url='https://github.com/ResidentMario/datablocks',
    download_url='https://github.com/ResidentMario/datablocks/tarball/0.0.1',
    keywords=['data', 'data analysis', 'data science', 'task graph'],
    classifiers=[]
)