from typing import Any, Tuple

import numpy as np
import pandas as pd
from dagster_airbyte import airbyte_resource, build_airbyte_assets
from dagster_dbt import dbt_cli_resource, load_assets_from_dbt_project
from scipy import optimize

from dagster import asset, load_assets_from_current_module, repository, materialize, ScheduleDefinition
from dagster.core.execution.with_resources import with_resources

from modern_data_stack_assets.constants import *  # pylint: disable=wildcard-import,unused-wildcard-import
from modern_data_stack_assets.pandas_io_manager import pandas_io_manager

airbyte_assets = build_airbyte_assets(
    connection_id=AIRBYTE_CONNECTION_ID,
    destination_tables=["orders", "users"],
    asset_key_prefix=["postgres_replica"],
)

dbt_assets = load_assets_from_dbt_project(
    project_dir=DBT_PROJECT_DIR, io_manager_key="pandas_io_manager",
    select='mds_dbt'
    # use_build_command=True
)


@asset(compute_kind="python")
def order_forecast_model(daily_order_summary: pd.DataFrame) -> Any:
    """Model parameters that best fit the observed data"""
    df = daily_order_summary
    return tuple(
        optimize.curve_fit(
            f=model_func, xdata=df.order_date.astype(np.int64), ydata=df.num_orders, p0=[10, 100]
        )[0]
    )


@asset(compute_kind="python", io_manager_key="pandas_io_manager")
def predicted_orders(
    daily_order_summary: pd.DataFrame, order_forecast_model: Tuple[float, float]
) -> pd.DataFrame:
    """Predicted orders for the next 30 days based on the fit paramters"""
    a, b = order_forecast_model
    start_date = daily_order_summary.order_date.max()
    future_dates = pd.date_range(start=start_date, end=start_date + pd.DateOffset(days=30))
    predicted_data = model_func(x=future_dates.astype(np.int64), a=a, b=b)
    return pd.DataFrame({"order_date": future_dates, "num_orders": predicted_data})


# all of the resources needed for interacting with our tools
resource_defs = {
    "airbyte": airbyte_resource.configured(AIRBYTE_CONFIG),
    "dbt": dbt_cli_resource.configured(DBT_CONFIG),
    "pandas_io_manager": pandas_io_manager.configured(PANDAS_IO_CONFIG),
}

@repository
def mds_repo():
    from dagster import define_asset_job

    assets_with_resource = with_resources(
        load_assets_from_current_module(),
        resource_defs=resource_defs,
    )

    define_job_all_assets = define_asset_job("all")
    schedule_all = ScheduleDefinition(job=define_job_all_assets, cron_schedule="@hourly", execution_timezone='Australia/NSW')

    return  assets_with_resource + [define_job_all_assets, schedule_all]

    # return  assets_with_resource + [define_job_all_assets]

if __name__ == "__main__":


    assets_to_load = with_resources(
        load_assets_from_current_module(),
        resource_defs=resource_defs,
    )

    materialize(assets_to_load)