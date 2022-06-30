from typing import Any, Tuple

import numpy as np
import pandas as pd
from dagster_dbt import dbt_cli_resource, load_assets_from_dbt_project
from scipy import optimize

from dagster import asset, load_assets_from_current_module, repository, materialize, ScheduleDefinition
from dagster.core.execution.with_resources import with_resources

from modern_data_stack_assets.constants import *  # pylint: disable=wildcard-import,unused-wildcard-import
from modern_data_stack_assets.pandas_io_manager import pandas_io_manager

dbt_assets = load_assets_from_dbt_project(
    project_dir=DBT_PROJECT_DIR, io_manager_key="pandas_io_manager",
    select='re_data',
    use_build_command=True
)




# all of the resources needed for interacting with our tools
resource_defs = {
    "dbt": dbt_cli_resource.configured(DBT_CONFIG),
    "pandas_io_manager": pandas_io_manager.configured(PANDAS_IO_CONFIG),
}

@repository
def re_data_repo():
    from dagster import define_asset_job

    assets_with_resource = with_resources(
        dbt_assets,
        resource_defs=resource_defs,
    )

    define_job_all_assets = define_asset_job("re_data")
    schedule_all = ScheduleDefinition(job=define_job_all_assets, cron_schedule="@hourly", execution_timezone='Australia/NSW')

    return  assets_with_resource + [define_job_all_assets, schedule_all]

if __name__ == "__main__":


    assets_to_load = with_resources(
        dbt_assets,
        resource_defs=resource_defs,
    )

    materialize(assets_to_load)