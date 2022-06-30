# Intro

This is an example of how to use the Software-Defined Asset APIs alongside Modern Data Stack tools
(specifically, Airbyte and dbt).

[blog](https://dagster.io/blog/software-defined-assets)
[youtube](https://www.youtube.com/watch?v=eS--8brw5YM)

# TODO

## Issue dbt tests blocking all downstream depencies when using dagster_dbt.load_assets_from_dbt_project

If a dbt model fails to run or its test fails then I still want upstream models to continue if they dont have a dependency on the failing model.

e.g. when following along to the [blog](https://dagster.io/blog/software-defined-assets) we load all our assets with the dbt build command so tests run:

```python
from dagster_dbt import load_assets_from_dbt_project

DBT_PROJECT_DIR = '..'

dbt_assets = load_assets_from_dbt_project(
    project_dir=DBT_PROJECT_DIR, io_manager_key="pandas_io_manager",
    select='mds_dbt',
    use_build_command=True
)
```

But as soon as i add a new model with no downstream dependencies and create a failing test then the upstream dependencies are skipped.

How do i get those upstream dependencies to continue if none of there dependencies have failed?

Example of the changes i made to [blog](https://dagster.io/blog/software-defined-assets) : 


# Setup

## Python

To install this example and its python dependencies, run:

```
$ pip install -e .
```

Once you've done this, you can run:

run the daemon if required
```
export DAGSTER_HOME="/home/dave/data-engineering/dagster-modern-data-stack-assets-dg/dagster-local-file-store";
dagster-daemon run;

```

Run the UI
```
export DAGSTER_HOME="/home/dave/data-engineering/dagster-modern-data-stack-assets-dg/dagster-local-file-store";
dagit;
```

To view this example in Dagster's UI, Dagit.

If you try to kick off a run immediately, it will fail, as there is no source data to ingest/transform, nor is there an active Airbyte connection. To get everything set up properly, read on.

## dbt re data

### setup

```bash
cd mds_dbt
dbt deps
pipenv install re_data -d
```

run re data for the a time window (minics running this several times)
```bash
re_data run --start-date 2021-12-23 --end-date 2021-12-31
```

or run one off with
```bash
dbt run --models package:re_data
```


### running re_data site

```bash
re_data overview generate --start-date 2021-12-23 --end-date 2021-12-31 --interval days:1
re_data overview serve;
```

### send a notification TBC
```bash
re_data notify slack \                                              ✘ INT  re-data-dbt-aMOho44y
--start-date 2022-06-20 \
--end-date 2022-06-27 \
--webhook-url https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX \
--subtitle="[Optional] Daves Markdown text to be added as a subtitle in the slack message generated"
```

## Local Postgres

To keep things running on a single machine, we'll use a local postgres instance as both the source and the destination for our data. You can imagine the "source" database as some online transactional database, and the "destination" as a data warehouse (something like Snowflake).

To get a postgres instance with the required source and destination databases running on your machine, you can run:

```
$ docker pull postgres
$ docker run --name mds-demo -p 5432:5432 -e POSTGRES_PASSWORD=password -d postgres
$ PGPASSWORD=password psql -h localhost -p 5432 -U postgres -d postgres -c "CREATE DATABASE postgres_replica;"
```

## Airbyte

Now, you'll want to get Airbyte running locally. The full instructions can be found [here](https://docs.airbyte.com/deploying-airbyte/local-deployment), but if you just want to run some commands (in a separate terminal):

```
$ git clone https://github.com/airbytehq/airbyte.git
$ cd airbyte
$ docker-compose up
```

Once you've done this, you should be able to go to http://localhost:8000, and see Airbyte's UI.

## Data and Connections

Now, you'll want to seed some data into the empty database you just created, and create an Airbyte connection between the source and destination databases.

There's a script provided that should handle this all for you, which you can run with:

```
$ python -m modern_data_stack_assets.setup_airbyte
```

At the end of this output, you should see something like:

```
Created Airbyte Connection: c90cb8a5-c516-4c1a-b243-33dfe2cfb9e8
```

This connection id is specific to your local setup, so you'll need to update `constants.py` with this
value. Once you've update your `constants.py` file, you're good to go!
