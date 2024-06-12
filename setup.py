from setuptools import find_packages, setup

SHORT_DESCRIPTION = 'Serve click scripts over the web with minimal effort.'

# Use the README as the long description
with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

requirements = [
    'click>=8.0',
    'Flask>=2.3.2',
    'Jinja2>=3.1.3',
    'flask_httpauth>=3.2.4'
]

dev_requirements = [
    'pytest>=6.2',
    'flake8>=3.9',
    'beautifulsoup4>=4.9',
    'isort>=5.8',
    'twine>=3.4',
    'wheel'
]


setup(
    name='click-web',
    version='0.8.5',
    url='https://github.com/fredrik-corneliusson/click-web',
    author='Fredrik Corneliusson',
    author_email='fredrik.corneliusson@gmail.com',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license='MIT',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    python_requires='>=3.8',
    install_requires=requirements,
    dependency_links=[],
    extras_require={
        'dev': dev_requirements
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: System :: Shells',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ]
)
