import setuptools

with open("version", 'r') as f:
    version = f.read()

setuptools.setup(
    name="jitab", 
    version=version,
    author="Alberto Coletta",
    description="Integrate GitLab and Jira for a faster development flow.",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['jitab=jitab.app:run'],
    },
    install_requires=[
        "requests",
        "questionary"
    ],
    zip_safe=False,
    python_requires='>=3.7',
)
