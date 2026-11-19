from pathlib import Path

import numpy as np
import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Genera los resúmenes de tiempos de respuesta de las solicitudes PQRS.
    """
    activity_dir = Path(__file__).resolve().parents[1]
    data_dir = activity_dir / "data"

    channels = []
    for channel, filename in (
        ("letter", "historical_requests_letter.csv.gz"),
        ("web", "historical_requests_web.csv.gz"),
    ):
        requests = pd.read_csv(data_dir / filename).drop_duplicates().copy()
        requests["channel"] = channel
        channels.append(requests)

    requests = pd.concat(channels, ignore_index=True)
    requests["in_date"] = pd.to_datetime(
        requests["in_date"], format="mixed", errors="coerce"
    )
    requests["out_date"] = pd.to_datetime(
        requests["out_date"], format="mixed", errors="coerce"
    )
    requests["year"] = requests["in_date"].dt.year

    answered = requests["out_date"].notna()
    requests["calendar_days"] = np.nan
    requests["business_days"] = np.nan

    in_dates = requests.loc[answered, "in_date"]
    out_dates = requests.loc[answered, "out_date"]
    requests.loc[answered, "calendar_days"] = (
        out_dates - in_dates
    ).dt.days

    in_numpy = in_dates.to_numpy(dtype="datetime64[D]")
    out_numpy = out_dates.to_numpy(dtype="datetime64[D]")
    requests.loc[answered, "business_days"] = np.busday_count(
        in_numpy + np.timedelta64(1, "D"),
        out_numpy + np.timedelta64(1, "D"),
    )

    requests["answered"] = answered
    requests["on_time"] = (
        requests["answered"] & (requests["business_days"] <= 15)
    )

    channel_summary = (
        requests.groupby("channel", as_index=False)
        .agg(requests=("record_id", "size"), answered=("answered", "sum"))
        .sort_values("channel")
        .reset_index(drop=True)
    )
    channel_summary["pending"] = (
        channel_summary["requests"] - channel_summary["answered"]
    )
    channel_medians = (
        requests.loc[requests["answered"]]
        .groupby("channel", as_index=False)["business_days"]
        .median()
        .rename(columns={"business_days": "median_business_days"})
    )
    channel_on_time = (
        requests.groupby("channel", as_index=False)["on_time"]
        .mean()
        .rename(columns={"on_time": "on_time_rate"})
    )
    channel_summary = (
        channel_summary.merge(channel_medians, on="channel", how="left")
        .merge(channel_on_time, on="channel", how="left")
    )
    channel_summary = channel_summary[
        [
            "channel",
            "requests",
            "answered",
            "pending",
            "median_business_days",
            "on_time_rate",
        ]
    ]
    for column in ("requests", "answered", "pending"):
        channel_summary[column] = channel_summary[column].astype("int64")

    yearly_summary = (
        requests.groupby(["year", "channel"], as_index=False)
        .agg(
            requests=("record_id", "size"),
            pending=("answered", lambda values: (~values).sum()),
        )
        .sort_values(["year", "channel"])
        .reset_index(drop=True)
    )
    yearly_on_time = (
        requests.groupby(["year", "channel"], as_index=False)["on_time"]
        .mean()
        .rename(columns={"on_time": "on_time_rate"})
    )
    yearly_summary = yearly_summary.merge(
        yearly_on_time, on=["year", "channel"], how="left"
    )
    yearly_summary = yearly_summary[
        ["year", "channel", "requests", "pending", "on_time_rate"]
    ]
    for column in ("year", "requests", "pending"):
        yearly_summary[column] = yearly_summary[column].astype("int64")

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    entry_day_counts = (
        requests.groupby("day_name", as_index=False)
        .size()
        .rename(columns={"size": "requests"})
    )
    entry_day_medians = (
        requests.loc[requests["answered"]]
        .groupby("day_name", as_index=False)[
            ["calendar_days", "business_days"]
        ]
        .median()
        .rename(
            columns={
                "calendar_days": "median_calendar_days",
                "business_days": "median_business_days",
            }
        )
    )
    entry_day_summary = (
        pd.DataFrame({"day_name": day_order})
        .merge(entry_day_counts, on="day_name", how="left")
        .merge(entry_day_medians, on="day_name", how="left")
    )
    entry_day_summary = entry_day_summary[
        [
            "day_name",
            "requests",
            "median_calendar_days",
            "median_business_days",
        ]
    ]
    entry_day_summary["requests"] = entry_day_summary["requests"].astype(
        "int64"
    )

    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)
    channel_summary.to_csv(
        submission_dir / "channel_summary.csv", index=False
    )
    yearly_summary.to_csv(
        submission_dir / "yearly_summary.csv", index=False
    )
    entry_day_summary.to_csv(
        submission_dir / "entry_day_summary.csv", index=False
    )

    return channel_summary, yearly_summary, entry_day_summary
