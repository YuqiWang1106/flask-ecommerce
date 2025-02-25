from setuptools import setup, find_packages

setup(
    name="flaskr",
    version="1.0.0",
    packages=find_packages(include=["flaskr", "flaskr.*"]),  # 仅打包 flaskr
    include_package_data=True,
    install_requires=[
        "flask",
    ],
)

