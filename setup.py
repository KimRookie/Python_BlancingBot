from setuptools import setup, find_packages

setup(
    name='BalancingBot',
    version='0.1.0',
    description='Discord Balancing Bot for managing user interactions',
    author='Suhwan Kim',
    author_email='gam9852@naver.com',
    packages=find_packages(),
    install_requires=[
        'discord.py==2.3.2',  # 이 버전은 예시이며, 필요에 따라 변경해주세요.
        'asyncio',
        'tkinter',
    ],
    entry_points={
        'console_scripts': [
            'balancingbot=balancingbot.main:main',
        ],
    },
)
