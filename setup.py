from setuptools import find_packages, setup

setup(
    name="modern_data_stack_assets",
    version="0+dev",
    author="Elementl",
    author_email="hello@elementl.com",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["test"]),
    package_data={"modern_data_stack_assets": ["mds_dbt/*"]},
    install_requires=[
        # "jsonschema==3.0.0", # currently required for re_data, but if dont use re data then 3.2.0 works
        "re_data",
        "dagster",
        "dagit",
        "dagster-airbyte",
        "dagster-dbt",
        "dagster-postgres",
        "pandas",
        "numpy",
        "scipy",
        "dbt-core",
        "dbt-postgres",
    ],
    extras_require={"tests": ["mypy", "pylint", "pytest"]},
)
