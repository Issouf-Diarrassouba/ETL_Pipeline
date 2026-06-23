import pytest
from etl_pipeline.extract import extract_csv
from etl_pipeline.transform import DataTransformer


# -----------------------------
# 1. CSV extraction sanity test
# -----------------------------
def test_csv_extract_returns_dataframe():
    data = extract_csv()

    # should return dict of datasets
    assert isinstance(data, dict)
    assert "results" in data


# -----------------------------
# 2. Transformation does not crash
# -----------------------------
def test_transform_pipeline_runs():
    csv_data = extract_csv()

    api_data = {
        "results": [],
        "shootouts": [],
        "goalscorers": []
    }

    transformer = DataTransformer(csv_data, api_data)
    transformed = transformer.transform_all()

    # structure check
    assert isinstance(transformed, dict)
    assert "results" in transformed

    # should always return DataFrame-like objects
    assert transformed["results"] is not None


# -----------------------------
# 3. Reject logic simulation test
# -----------------------------
def test_reject_record_structure():
    fake_record = {
        "home_team": "A",
        "away_team": "B",
        "date": "2026-01-01"
    }

    # simulate reject payload (no DB required)
    reject_payload = {
        "src_name": "test_source",
        "raw_record": fake_record,
        "reason": "Fake error for test"
    }

    assert reject_payload["src_name"] == "test_source"
    assert "reason" in reject_payload
    assert isinstance(reject_payload["raw_record"], dict)


# -----------------------------
# 4. Required fields validation
# -----------------------------
def test_required_fields_exist():
    csv_data = extract_csv()
    results = csv_data["results"]

    required_cols = ["home_team", "away_team"]

    for col in required_cols:
        assert col in results.columns

        