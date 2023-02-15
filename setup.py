import setuptools

import src.DLMS_SPODES.settings

with open("README.md", "r") as fh:
    long_description = fh.read()

a = setuptools.find_packages("DLMSStringValues")

setuptools.setup(
    name="DLMSStringValues",
    version=src.DLMS_SPODES.settings.version(),
    author="Serj Kotilevski",
    author_email="youserj@outlook.com",
    description="keep string constants",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/youserj/DlmsSPODES",
    # packages=["DLMSStringValues"],
    package_data={'DLMSStringValues': ['EN']},
    keywords=['dlms', 'string', 'constant', 'values'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License"
    ],
    entry_points={
        'console_scripts': [
            'parser=DLMSStringValues.main:main'
        ]
    },
    python_requires='>=3.11',
)
