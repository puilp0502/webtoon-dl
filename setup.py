from setuptools import setup, find_packages

setup(
    name='webtoon-dl',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        webtoon-dl=webtoon_dl.main:main
    ''',
)
