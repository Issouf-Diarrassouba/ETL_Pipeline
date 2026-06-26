import etl_pipeline.etl as etl
from unittest.mock import patch, MagicMock
import pandas as pd

@patch("etl_pipeline.etl.extract_csv")
@patch("etl_pipeline.etl.extract_api")
@patch("etl_pipeline.etl.DataTransformer")
@patch("etl_pipeline.etl.DataLoader")
@patch("etl_pipeline.etl.get_connection")
@patch("etl_pipeline.etl.init_db")
def test_main_pipeline_runs(
    mock_init_db,
    mock_conn,
    mock_loader,
    mock_transformer,
    mock_api,
    mock_csv
):

    # ---- CSV mock ----
    mock_csv.return_value = {
        "results": pd.DataFrame({
            "home_team": ["A"],
            "away_team": ["B"],
            "tournament": ["Cup"],
            "date": ["2020-01-01"],
            "home_score": [1],
            "away_score": [0]
        })
    }

    # ---- API mock ----
    mock_api.return_value = pd.DataFrame({
        "team": ["A"],
        "scorer": ["player1"],
        "minute": [10],
        "penalty": [0],
        "home_team": ["A"],
        "away_team": ["B"],
        "date": ["2020-01-01"]
    })

    # ---- transformer mock ----
    fake_df = pd.DataFrame({
        "home_team": ["A"],
        "away_team": ["B"],
        "tournament": ["Cup"],
        "date": ["2020-01-01"]
    })

    transformer_instance = MagicMock()
    transformer_instance.transform_all.return_value = {
        "results": fake_df,
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

    # ---- loader mock ----
    loader_instance = MagicMock()
    loader_instance.load_nation.return_value = 1
    loader_instance.load_tournament.return_value = 1
    loader_instance.load_matches.return_value = 1
    loader_instance.load_players.return_value = 1
    loader_instance.load_goals.return_value = 1
    loader_instance.load_shootout.return_value = 1

    mock_loader.return_value = loader_instance

    mock_conn.return_value = MagicMock()

    # ---- RUN PIPELINE ----
    etl.main()