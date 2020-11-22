import setuptools


def parse_requirements(file):
    lines = (line.strip() for line in open(file))
    return [line for line in lines if line and not line.startswith("#")]


setuptools.setup(
    name='actions',
    version='0.1',
    packages=setuptools.find_packages(),
    install_requires=parse_requirements('requirements.txt'),
)
