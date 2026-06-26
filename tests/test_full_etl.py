import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

import etl_pipeline.etl as etl
from etl_pipeline.transform import DataTransformer
from etl_pipeline.database import get_connection, init_db
from etl_pipeline.extract import extract_api
from etl_pipeline.load import DataLoader


# =========================================================
# 1. ETL ERROR PATHS
# =========================================================

@patch("etl_pipeline.etl.init_db")
@patch("etl_pipeline.etl.get_connection")
@patch("etl_pipeline.etl.DataLoader")
@patch("etl_pipeline.etl.DataTransformer")
@patch("etl_pipeline.etl.extract_api", side_effect=Exception("API failure"))
@patch("etl_pipeline.etl.extract_csv", side_effect=Exception("CSV failure"))
def test_etl_error_paths(
    mock_extract_csv,
    mock_extract_api,
    mock_transformer,
    mock_loader,
    mock_get_connection,
    mock_init_db
):
    mock_get_connection.return_value = MagicMock()
    etl.main()


# =========================================================
# 2. ETL HAPPY PATH
# =========================================================

@patch("etl_pipeline.etl.init_db")
@patch("etl_pipeline.etl.get_connection")
@patch("etl_pipeline.etl.DataLoader")
@patch("etl_pipeline.etl.DataTransformer")
@patch("etl_pipeline.etl.extract_api")
@patch("etl_pipeline.etl.extract_csv")
def test_etl_happy_path(
    mock_extract_csv,
    mock_extract_api,
    mock_transformer,
    mock_loader,
    mock_get_connection,
    mock_init_db
):

    mock_extract_csv.return_value = {
        "results": pd.DataFrame({
            "home_team": ["A"],
            "away_team": ["B"],
            "tournament": ["Cup"],
            "date": ["2020-01-01"],
            "home_score": [1],
            "away_score": [0]
        })
    }

    mock_extract_api.return_value = pd.DataFrame({
        "scorer": ["player1"],
        "team": ["A"],
        "home_team": ["A"],
        "away_team": ["B"],
        "date": ["2020-01-01"],
        "minute": [10],
        "penalty": [0]
    })

    transformer_instance = MagicMock()
    transformer_instance.transform_all.return_value = {
        "results": pd.DataFrame({
            "home_team": ["A"],
            "away_team": ["B"],
            "tournament": ["Cup"],
            "date": ["2020-01-01"],
            "home_score": [1],
            "away_score": [0]
        }),
        "goalscorers": pd.DataFrame({
            "scorer": ["player1"],
            "team": ["A"],
            "home_team": ["A"],
            "away_team": ["B"],
            "date": ["2020-01-01"],
            "minute": [10],
            "penalty": [0]
        }),
        "shootouts": pd.DataFrame()
    }

    mock_transformer.return_value = transformer_instance

    loader_instance = MagicMock()
    loader_instance.load_nation.return_value = 1
    loader_instance.load_tournament.return_value = 1
    loader_instance.load_matches.return_value = 1
    loader_instance.load_players.return_value = 1
    loader_instance.load_goals.return_value = 1
    loader_instance.load_shootout.return_value = 1

    mock_loader.return_value = loader_instance
    mock_get_connection.return_value = MagicMock()

    etl.main()


# =========================================================
# 3. DATABASE TESTS
# =========================================================

@patch("psycopg2.connect")
def test_get_connection(mock_connect):
    mock_connect.return_value = MagicMock()

    conn = get_connection()
    assert conn is not None


def test_init_db():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    init_db(mock_conn)
    assert True


# =========================================================
# 4. EXTRACT TESTS
# =========================================================

@patch("requests.get")
def test_extract_api_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": 1}]
    mock_get.return_value = mock_response

    result = extract_api("http://127.0.0.1:5000/api/goalscorers")
    assert result is not None




# =========================================================
# 5. LOAD TESTS
# =========================================================

@patch("psycopg2.connect")
def test_loader_init(mock_connect):
    mock_connect.return_value = MagicMock()

    loader = DataLoader({}, {
        "host": "x",
        "database": "x",
        "user": "x",
        "password": "x",
        "port": 5433
    })

    assert loader.connection is not None


@patch("psycopg2.connect")
def test_load_nation(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = [1]
    mock_connect.return_value = mock_conn

    loader = DataLoader({}, {
        "host": "x",
        "database": "x",
        "user": "x",
        "password": "x",
        "port": 5433
    })

    result = loader.load_nation("France")
    assert result == 1


@patch("psycopg2.connect")
def test_load_rejects(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    loader = DataLoader({}, {
        "host": "x",
        "database": "x",
        "user": "x",
        "password": "x",
        "port": 5433
    })

    loader.load_stg_rejects({"bad": "data"}, "error", "test")
    assert mock_cursor.execute.called


# =========================================================
# 6. TRANSFORM TESTS
# =========================================================

def test_transform_invalid_input():
    t = DataTransformer({}, {})
    result = t.normalize_column_names("not_a_dataframe")
    assert isinstance(result, pd.DataFrame)


def test_transform_merge():
    csv = {
        "results": pd.DataFrame({
            "home_team": ["A"],
            "away_team": ["B"]
        })
    }

    api = {
        "results": pd.DataFrame({
            "home_team": ["A"],
            "away_team": ["B"]
        })
    }

    t = DataTransformer(csv, api)
    result = t.transform_all()

    assert "results" in result