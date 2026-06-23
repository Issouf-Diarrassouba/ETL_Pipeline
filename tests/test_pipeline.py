import pytest
from etl_pipeline.extract import extract_csv
from etl_pipeline.transform import DataTransformer
from etl_pipeline.database import get_connection, init_db
from etl_pipeline.load import DataLoader


def test_extract_csv_returns_data():
    data = extract_csv()

    assert data is not None
    assert len(data) > 0

# if data not passed in as dataframe how does system react 
def test_transformation_structure():
    csv_data = extract_csv()

    api_data = {
        "results": [],
        "shootouts": [],
        "goalscorers": []
    }

    transformer = DataTransformer(csv_data, api_data)
    transformed = transformer.transform_all()

    assert isinstance(transformed, dict)
    assert "results" in transformed
    assert "shootouts" in transformed
    assert "goalscorers" in transformed


def test_no_null_matches_required_fields():
    csv_data = extract_csv()

    results_df = csv_data["results"]  # or whichever contains matches

    assert "home_team" in results_df.columns
    assert results_df["home_team"].isnull().sum() == 0
    assert results_df["away_team"].isnull().sum() == 0


def test_db_connection():
    conn = get_connection()
    assert conn is not None


def test_db_init_runs():
    conn = get_connection()

    try:
        init_db(conn)
        assert True
    except Exception as e:
        pytest.fail(f"DB init failed: {e}")


def test_load_nation_insert():
    db_config = {
        "host": "localhost",
        "database": "etl",
        "user": "etl_user",
        "password": "password",
        "port": 5433
    }

    loader = DataLoader({}, db_config)

    nation_id = loader.load_nation("Testland")

    assert nation_id is not None


def test_reject_logging():
    db_config = {
        "host": "localhost",
        "database": "etl",
        "user": "etl_user",
        "password": "password",
        "port": 5433
    }

    loader = DataLoader({}, db_config)

    try:
        raise ValueError("Fake error")
    except Exception as e:
        loader.load_stg_rejects(
            {"test": "data"},
            str(e),
            "test_source"
        )

    assert True