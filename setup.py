from setuptools import find_packages, setup

SHORT_DESCRIPTION = 'Serve click scripts over the web with minimal effort.'

# Use the README as the long description
with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

requirements = [
    'click>=7.0',
    'Flask>=1.0',
    'Jinja2>=2.10'
]

testing_requirements = [
    'pytest>=4.1',
    'flake8>=3.6',
    'beautifulsoup4>=4.7.1'
]


setup(
    name='click-web',
    version='0.6.3',
    url='https://github.com/fredrik-corneliusson/click-web',
    author='Fredrik Corneliusson',
    author_email='fredrik.corneliusson@gmail.com',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license='MIT',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    install_requires=requirements,
    dependency_links=[],
    extras_require={
        'testing': testing_requirements
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
