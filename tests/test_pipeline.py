
import pytest
import json
from unittest.mock import patch, MagicMock, call
from etl_pipeline.load import DataLoader


# ---------------------------------------------------------------------------
# Fixture: DataLoader with a fully mocked psycopg2 connection
# ---------------------------------------------------------------------------

DB_CONFIG = {
    "host": "localhost",
    "database": "etl",
    "user": "etl_user",
    "password": "password",
    "port": 5433,
}


@pytest.fixture
def mock_loader():
    """Return a DataLoader whose psycopg2 connection is completely mocked."""
    with patch("etl_pipeline.load.psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        loader = DataLoader({}, DB_CONFIG)

        # Expose the mocks for assertions inside tests
        loader._mock_conn = mock_conn
        loader._mock_cursor = mock_cursor
        yield loader


# ---------------------------------------------------------------------------
# __init__: connection is established
# ---------------------------------------------------------------------------

def test_dataloader_init_connects_to_db():
    with patch("etl_pipeline.load.psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = MagicMock()
        mock_connect.return_value = mock_conn

        loader = DataLoader({}, DB_CONFIG)

        mock_connect.assert_called_once_with(
            host="localhost",
            database="etl",
            user="etl_user",
            password="password",
            port=5433,
        )
        assert loader.connection is mock_conn


# ---------------------------------------------------------------------------
# load_nation
# ---------------------------------------------------------------------------

def test_load_nation_returns_id(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (42,)

    nation_id = mock_loader.load_nation("Brazil")

    assert nation_id == 42
    mock_loader._mock_cursor.execute.assert_called_once()
    sql = mock_loader._mock_cursor.execute.call_args[0][0]
    assert "football.nation" in sql
    mock_loader._mock_conn.commit.assert_called()


def test_load_nation_passes_correct_value(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (7,)

    mock_loader.load_nation("Germany")

    args = mock_loader._mock_cursor.execute.call_args[0][1]
    assert args == ("Germany",)


# ---------------------------------------------------------------------------
# load_tournament
# ---------------------------------------------------------------------------

def test_load_tournament_returns_id(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (3,)

    tournament_id = mock_loader.load_tournament("World Cup")

    assert tournament_id == 3
    mock_loader._mock_conn.commit.assert_called()


def test_load_tournament_passes_correct_value(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (1,)

    mock_loader.load_tournament("Copa America")

    args = mock_loader._mock_cursor.execute.call_args[0][1]
    assert args == ("Copa America",)


# ---------------------------------------------------------------------------
# load_matches
# ---------------------------------------------------------------------------

SAMPLE_MATCH = {
    "date": "2022-07-10",
    "home_team_id": 1,
    "away_team_id": 2,
    "home_score": 3,
    "away_score": 1,
    "tournament_id": 5,
    "city": "Berlin",
    "country": "Germany",
    "neutral": False,
}


def test_load_matches_returns_id(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (99,)

    match_id = mock_loader.load_matches(SAMPLE_MATCH)

    assert match_id == 99
    mock_loader._mock_conn.commit.assert_called()


def test_load_matches_passes_all_fields(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (1,)

    mock_loader.load_matches(SAMPLE_MATCH)

    args = mock_loader._mock_cursor.execute.call_args[0][1]
    assert args[0] == "2022-07-10"   # date
    assert args[1] == 1              # home_team_id
    assert args[2] == 2              # away_team_id
    assert args[3] == 3              # home_score
    assert args[4] == 1              # away_score
    assert args[5] == 5              # tournament_id


def test_load_matches_handles_optional_fields_missing(mock_loader):
    """city / country / neutral are optional (.get); should not raise if absent."""
    mock_loader._mock_cursor.fetchone.return_value = (10,)

    minimal_match = {
        "date": "2022-01-01",
        "home_team_id": 1,
        "away_team_id": 2,
        "home_score": 0,
        "away_score": 0,
        "tournament_id": 1,
    }
    match_id = mock_loader.load_matches(minimal_match)
    assert match_id == 10


# ---------------------------------------------------------------------------
# load_players
# ---------------------------------------------------------------------------

def test_load_players_returns_id(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (55,)

    player_id = mock_loader.load_players({"player_name": "Messi", "nation_id": 7})

    assert player_id == 55
    mock_loader._mock_conn.commit.assert_called()


def test_load_players_passes_correct_values(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (1,)

    mock_loader.load_players({"player_name": "Ronaldo", "nation_id": 3})

    args = mock_loader._mock_cursor.execute.call_args[0][1]
    assert args == ("Ronaldo", 3)


# ---------------------------------------------------------------------------
# load_goals
# ---------------------------------------------------------------------------

SAMPLE_GOAL = {
    "match_id": 10,
    "player_id": 5,
    "minute_scored": 67,
    "is_penalty": False,
}


def test_load_goals_returns_id(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (200,)

    goal_id = mock_loader.load_goals(SAMPLE_GOAL)

    assert goal_id == 200
    mock_loader._mock_conn.commit.assert_called()


def test_load_goals_passes_correct_values(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (1,)

    mock_loader.load_goals(SAMPLE_GOAL)

    args = mock_loader._mock_cursor.execute.call_args[0][1]
    assert args == (10, 5, 67, False)


def test_load_goals_penalty_flag_true(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (2,)

    mock_loader.load_goals({**SAMPLE_GOAL, "is_penalty": True})

    args = mock_loader._mock_cursor.execute.call_args[0][1]
    assert args[3] is True


# ---------------------------------------------------------------------------
# load_shootout
# ---------------------------------------------------------------------------

SAMPLE_SHOOTOUT = {
    "match_id": 10,
    "winner_team_id": 1,
    "first_shooting_team_id": 2,
}


def test_load_shootout_returns_id(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (300,)

    shootout_id = mock_loader.load_shootout(SAMPLE_SHOOTOUT)

    assert shootout_id == 300
    mock_loader._mock_conn.commit.assert_called()


def test_load_shootout_passes_correct_values(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (1,)

    mock_loader.load_shootout(SAMPLE_SHOOTOUT)

    args = mock_loader._mock_cursor.execute.call_args[0][1]
    assert args == (10, 1, 2)


# ---------------------------------------------------------------------------
# load_stg_rejects
# ---------------------------------------------------------------------------

def test_load_stg_rejects_executes_insert(mock_loader):
    mock_loader.load_stg_rejects(
        record={"home_team": "Brazil"},
        reason="Duplicate key",
        src="matches",
    )

    mock_loader._mock_cursor.execute.assert_called_once()
    sql = mock_loader._mock_cursor.execute.call_args[0][0]
    assert "football.stg_rejects" in sql


def test_load_stg_rejects_serialises_record_to_json(mock_loader):
    record = {"home_team": "Brazil", "away_team": "Germany"}

    mock_loader.load_stg_rejects(record=record, reason="error", src="test_src")

    args = mock_loader._mock_cursor.execute.call_args[0][1]
    # Second positional arg is the json.dumps'd record
    assert args[0] == "test_src"
    assert json.loads(args[1]) == record
    assert args[2] == "error"


def test_load_stg_rejects_with_string_record(mock_loader):
    """load_stg_rejects is also called with plain strings in etl.py."""
    mock_loader.load_stg_rejects(
        record="some nation",
        reason="Nation insert failed",
        src="nations",
    )
    mock_loader._mock_cursor.execute.assert_called_once()


# ---------------------------------------------------------------------------
# SQL keyword spot-checks (ensures the right tables are targeted)
# ---------------------------------------------------------------------------

def test_load_nation_targets_correct_table(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (1,)
    mock_loader.load_nation("Test")
    sql = mock_loader._mock_cursor.execute.call_args[0][0]
    assert "football.nation" in sql


def test_load_tournament_targets_correct_table(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (1,)
    mock_loader.load_tournament("Test Cup")
    sql = mock_loader._mock_cursor.execute.call_args[0][0]
    assert "football.tournament" in sql


def test_load_matches_targets_correct_table(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (1,)
    mock_loader.load_matches(SAMPLE_MATCH)
    sql = mock_loader._mock_cursor.execute.call_args[0][0]
    assert "football.matches" in sql


def test_load_players_targets_correct_table(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (1,)
    mock_loader.load_players({"player_name": "X", "nation_id": 1})
    sql = mock_loader._mock_cursor.execute.call_args[0][0]
    assert "football.players" in sql


def test_load_goals_targets_correct_table(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (1,)
    mock_loader.load_goals(SAMPLE_GOAL)
    sql = mock_loader._mock_cursor.execute.call_args[0][0]
    assert "football.goals" in sql


def test_load_shootout_targets_correct_table(mock_loader):
    mock_loader._mock_cursor.fetchone.return_value = (1,)
    mock_loader.load_shootout(SAMPLE_SHOOTOUT)
    sql = mock_loader._mock_cursor.execute.call_args[0][0]
    assert "football.shootout" in sql
