from setuptools import setup

setup(
    name='melbalabs_summarize_consumes',
    packages=['melbalabs.summarize_consumes'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'summarize_consumes=melbalabs.summarize_consumes.main:main',
        ],
    }
)
