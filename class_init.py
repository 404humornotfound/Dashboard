import pandas as pd
from datetime import datetime, timedelta, date
import plotly.express as px
import streamlit as st
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os


# Allowlist pattern for table names — only alphanumeric and underscores allowed.
# This prevents SQL injection when table names are interpolated into queries,
# since parameterized queries (? placeholders) don't work for table/column names in SQL.
TABLE_NAME_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def _validate_table_name(name: str) -> str:
    """Validate and return a safe table name, or raise ValueError."""
    if not name or not TABLE_NAME_PATTERN.match(name):
        raise ValueError(f"Invalid table name: {name!r}")
    return name


# Module-level cached engine. The module is imported once per process, so this
# is shared across Streamlit reruns within a session instead of opening a brand
# new connection pool on every page interaction.
_engine = None


def get_engine():
    """Return a cached SQLAlchemy engine for the Postgres database.

    The connection string comes from the DATABASE_URL environment variable
    (set in .env locally, or as a secret in the deployment environment), e.g.
    postgresql://user:pass@host/dbname?sslmode=require
    """
    global _engine
    if _engine is None:
        load_credentials()
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL not set -- cannot connect to the database")
        # pool_pre_ping recycles connections dropped by serverless Postgres (e.g.
        # Neon scaling to zero) instead of handing out a dead connection.
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def connect_db():
    """Open a new connection to the Postgres database.

    Returns a SQLAlchemy Connection, which works with pandas read_sql/to_sql and
    supports .commit()/.close() just like the old sqlite3 connection did.
    """
    return get_engine().connect()


# All participant registrations live in a single table with a race_name column,
# instead of one table per race. The race name is a *value* we filter on (bound
# parameter), not a table identifier, which removes the SQL-injection surface that
# per-race table names used to create.
PARTICIPANT_TABLE = "participants"


def load_race_participants(race_name: str) -> pd.DataFrame:
    """Return all participant rows for one race from the participants table.

    The race name is passed as a bound parameter (never interpolated as an
    identifier), so it does not need table-name validation. The race_name column
    is dropped from the result so callers see the same shape the old per-race
    tables had.
    """
    conn = connect_db()
    try:
        df = pd.read_sql(
            text(f'SELECT * FROM "{PARTICIPANT_TABLE}" WHERE race_name = :race'),
            conn,
            params={"race": race_name},
        )
    finally:
        conn.close()
    return df.drop(columns=["race_name"], errors="ignore")


def append_new_participants(race_name: str, df: pd.DataFrame) -> int:
    """Insert only rows whose 'Participant ID' is not already stored for this race.

    Returns the number of rows actually inserted. Existing rows are never modified
    (insert-only dedup keyed on Participant ID, scoped to the race).
    """
    existing = load_race_participants(race_name)
    existing_ids = set(existing["Participant ID"]) if "Participant ID" in existing else set()

    to_add = df.copy()
    # Drop intra-CSV duplicate IDs defensively, then anything already stored.
    to_add = to_add.drop_duplicates(subset=["Participant ID"])
    to_add = to_add[~to_add["Participant ID"].isin(existing_ids)]
    if to_add.empty:
        return 0

    to_add = to_add.copy()
    to_add["race_name"] = race_name
    conn = connect_db()
    try:
        to_add.to_sql(PARTICIPANT_TABLE, conn, if_exists="append", index=False)
        conn.commit()
    finally:
        conn.close()
    return len(to_add)


def check_requirements_installed():
    if not os.path.exists(".env") and not os.path.exists("../.env"):
        st.error(".env file not found -- for this website to work, it must be copied over -- stopping website")
        st.stop()

    load_credentials()
    if not os.getenv("DATABASE_URL"):
        st.error("DATABASE_URL not configured -- stopping website (required to connect to the database)")
        st.stop()


def load_credentials():
    if os.path.exists("../.env"):
        load_dotenv(dotenv_path="../.env", override=True)
    elif os.path.exists(".env"):
        load_dotenv(override=True)


# user auth code
def creds_entered():
    load_credentials()
    expected_user = os.getenv("user")
    expected_pass = os.getenv("password")
    if expected_user is None or expected_pass is None:
        st.error("Credentials not configured in .env file")
        st.session_state["authenticated"] = False
        return
    if st.session_state["user"].strip() == expected_user and st.session_state["passwd"].strip() == expected_pass:
        st.session_state["authenticated"] = True
    else:
        st.session_state["authenticated"] = False
        st.error("Invalid username/password")


def authenticate_user():
    if "authenticated" not in st.session_state:
        st.text_input(label="username :", value="", key="user", on_change=creds_entered)
        st.text_input(label="password :", value="", key="passwd", type="password", on_change=creds_entered)
        return False
    else:
        if st.session_state["authenticated"]:
            return True
        else:
            st.text_input(label="username :", value="", key="user", on_change=creds_entered)
            st.text_input(label="password :", value="", key="passwd", type="password", on_change=creds_entered)
            return False




class Information:
    def __init__(self) -> None:
        conn = connect_db()
        try:
            self.dataframe = pd.read_sql("SELECT * FROM info", conn)
        finally:
            conn.close()

    def get_race_by_table_name(self, race_name: str) -> pd.DataFrame:
        return load_race_participants(race_name)

        



class Race:
    def __init__(self, start_date: datetime, end_date: datetime, race_name: str) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.race_name = _validate_table_name(race_name)
        self.dataframe = load_race_participants(self.race_name)
        # Convert date strings to date objects using vectorized pandas parsing
        # (much faster than row-by-row loop for large datasets)
        self.dataframe['Date'] = pd.to_datetime(self.dataframe['Date']).dt.date


    # returns dataframe of events participants by a certian day and total
    def get_accumulated_unique_by_day(self, days_until_race:int) -> pd.DataFrame:
        df = self.dataframe
        day = pd.Timestamp(self.end_date-timedelta(days=days_until_race-1)).date()
        unique_events = sorted(df['event'].unique())
        nums = []
        overall_nums = []
        for event in unique_events:
            nums.append(len(df[(df.event == event) & (df.Date < day)]))
            overall_nums.append(len(df[(df.event == event)]))
        unique_events.append("all")
        nums.append(len(df[(df.Date < day)]))
        overall_nums.append(len(df))
        return pd.DataFrame({"events":unique_events,f"{days_until_race} days left": nums, "total":overall_nums})




    def to_frequency(self):
        frequency = []

        for i in range((self.end_date - self.start_date).days + 1):
            day = pd.Timestamp(self.start_date + timedelta(days=i)).date()
            frequency.append(len(self.dataframe[self.dataframe.Date == day]))
        return frequency
    


    def to_frequency_unique(self, eventt:str):
        frequency = []
        for i in range((self.end_date - self.start_date).days+1):
            day = pd.Timestamp(self.start_date + timedelta(days=i)).date()
            frequency.append(len(self.dataframe[(self.dataframe.event == eventt) & (self.dataframe.Date == day)]))
        return frequency
    
def get_races() -> list:
    info = Information()
    info_df = info.dataframe
    races = []
    for i in range(len(info_df.index)):
        start_date = datetime.strptime(info_df['Registration start date'].iloc[i], "%Y-%m-%d").date()
        end_date = datetime.strptime(info_df['Registration end date'].iloc[i], "%Y-%m-%d").date()
        name = info_df['Name'].iloc[i]
        races.append(Race(start_date, end_date, name))
    return races


# ---------------------------------------------------------------------------
# Finance data — stored remotely in the 'finance' table (wide format: one row
# per race, one column per line item). These constants are the single source of
# truth for which line items exist and how they group, shared by the finance
# tool (which displays them) and the uploader (which edits them).
#
# Only RAW line items are stored. Derived totals (Total income less sponsorship,
# Total Fixed expense, Total Variable expense) are computed in code so they can
# never drift out of sync with the line items.
# ---------------------------------------------------------------------------

FINANCE_INCOME_COLS = ["Race income", "Sponsorship", "Donations", "Total income"]
FINANCE_FIXED_COLS = [
    "BTB (Cost / Consulting)", "BTB (Rentals)", "EMS", "Timing services",
    "Portable", "Facebook/Signs", "RRCA (insurance)", "Other", "Photography",
]
FINANCE_VARIABLE_COLS = ["Shirts", "Medals", "Bandana", "EMEDIA (Bibs)"]
FINANCE_TOTAL_COLS = ["Total expense", "Net (all in)", "Net (w/o Sponsorship)"]

# Canonical ordered list of every raw category persisted to the finance table.
FINANCE_CATEGORIES = (
    FINANCE_INCOME_COLS + FINANCE_FIXED_COLS + FINANCE_VARIABLE_COLS + FINANCE_TOTAL_COLS
)

# Not a line item: the field size the rest of the row was budgeted against.
# Every per-registrant figure divides this row by a headcount, and the only
# headcount that makes the division honest is the one the budget assumed --
# a $37,858 income line written for 1,100 racers describes 1,100 racers, no
# matter how many have signed up so far. Kept out of FINANCE_CATEGORIES so the
# uploader's line-item groups and seed_finance's completeness check are
# unaffected.
FINANCE_PLANNING_COLS = ["Assumed registrants"]

FINANCE_PERSISTED_COLS = FINANCE_CATEGORIES + FINANCE_PLANNING_COLS


def ensure_finance_table():
    """Create the finance table (one row per race, one column per line item) if
    it does not already exist."""
    # Category names come from the trusted FINANCE_CATEGORIES constant, so it is
    # safe to interpolate them as quoted column identifiers.
    col_defs = ", ".join(f'"{c}" DOUBLE PRECISION' for c in FINANCE_PERSISTED_COLS)
    conn = connect_db()
    try:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS finance ("
            f"race_name TEXT PRIMARY KEY, {col_defs})"
        ))
        # Additive migration for tables created before a column existed.
        for c in FINANCE_PERSISTED_COLS:
            conn.execute(text(
                f'ALTER TABLE finance ADD COLUMN IF NOT EXISTS "{c}" DOUBLE PRECISION'
            ))
        conn.commit()
    finally:
        conn.close()


def load_all_finance() -> dict:
    """Return all finance data as {race_name: {category: amount}}.

    Returns an empty dict if the finance table holds no rows yet.
    """
    ensure_finance_table()
    conn = connect_db()
    try:
        df = pd.read_sql("SELECT * FROM finance", conn)
    finally:
        conn.close()
    data: dict = {}
    # to_dict preserves the exact column names (which contain spaces / symbols),
    # unlike itertuples which would mangle them into positional identifiers.
    for rec in df.to_dict(orient="records"):
        race = rec.pop("race_name")
        data[race] = {k: v for k, v in rec.items() if pd.notna(v)}
    return data


def get_registrant_basis() -> dict:
    """Return, per race, the registrant count that per-registrant finance
    figures should be divided by.

    A finance row describes a whole season: the income it records is what the
    full field is expected to bring in, and the shirt/medal/bib totals are a
    full field's order. The participants table, by contrast, is a live count.
    While registration is still open those two describe different groups of
    people, so dividing the finance row by COUNT(*) inflates both income and
    variable cost per registrant -- which in turn halves break-even, the one
    direction it is dangerous to be wrong in.

    For a closed year the basis is simply the real final headcount. For a year
    whose registration is still open, it is "Assumed registrants" -- the field
    size the estimates themselves were built against -- because that is the
    group the rest of the row describes. When no assumption has been recorded,
    the final field is projected instead from the pace of the most recent closed
    year: what fraction of its field had signed up with the same number of days
    left, applied to the count so far.

    This is narrowly scoped on purpose. It belongs only to arithmetic that
    divides a finance amount by a headcount. Registrant counts, demographics,
    city and age breakdowns and sign-up trends must always use the real rows in
    the participants table -- never this number.

    Each entry holds:
      actual     -- registrations recorded so far
      basis      -- count to divide whole-season finance figures by
      projected  -- True when `basis` is an estimate rather than a final count
      note       -- short human-readable explanation of how `basis` was derived
    """
    ensure_finance_table()
    conn = connect_db()
    try:
        info = pd.read_sql("SELECT * FROM info", conn)
        parts = pd.read_sql(
            f'SELECT race_name, "Date" FROM "{PARTICIPANT_TABLE}"', conn
        )
        assumed_df = pd.read_sql(
            'SELECT race_name, "Assumed registrants" FROM finance', conn
        )
    finally:
        conn.close()

    assumed = {
        r.race_name: int(r[1])
        for r in assumed_df.itertuples(index=False)
        if pd.notna(r[1]) and r[1] > 0
    }

    parts["Date"] = pd.to_datetime(parts["Date"]).dt.date
    counts = parts.groupby("race_name").size().to_dict()
    ends = {
        r["Name"]: datetime.strptime(r["Registration end date"], "%Y-%m-%d").date()
        for _, r in info.iterrows()
    }

    today = date.today()
    closed = sorted([n for n, e in ends.items() if today > e], key=lambda n: ends[n])

    basis = {}
    for name, end in ends.items():
        actual = counts.get(name, 0)
        if today > end:
            basis[name] = {
                "actual": actual,
                "basis": actual,
                "projected": False,
                "note": "registration closed; final headcount",
            }
            continue

        days_left = (end - today).days

        # Registration still open. Prefer the field size the budget was built
        # against, so numerator and denominator describe the same group.
        if name in assumed:
            basis[name] = {
                "actual": actual,
                "basis": assumed[name],
                "projected": True,
                "note": (
                    f"registration open ({days_left} days left); using the "
                    f"{assumed[name]:,} registrants the budget was estimated from"
                ),
            }
            continue

        # No recorded assumption -- fall back to the most recent closed year's
        # pace at the same number of days before close.
        ref = closed[-1] if closed else None
        frac = None
        if ref:
            ref_total = counts.get(ref, 0)
            if ref_total:
                cutoff = ends[ref] - timedelta(days=days_left)
                ref_so_far = len(
                    parts[(parts.race_name == ref) & (parts.Date <= cutoff)]
                )
                if ref_so_far:
                    frac = ref_so_far / ref_total

        if frac:
            basis[name] = {
                "actual": actual,
                "basis": int(round(actual / frac)),
                "projected": True,
                "note": (
                    f"registration open ({days_left} days left); projected from "
                    f"{ref}, which had {frac:.0%} of its field at this point"
                ),
            }
        else:
            basis[name] = {
                "actual": actual,
                "basis": actual,
                "projected": False,
                "note": "registration open; no closed year to project from",
            }
    return basis


def save_finance(race_name: str, values: dict) -> None:
    """Upsert one race's finance row. `values` maps category -> amount."""
    safe_name = _validate_table_name(race_name)
    # Only persist known categories; this also keeps the interpolated column
    # identifiers below restricted to a trusted allowlist.
    cols = [c for c in values if c in FINANCE_PERSISTED_COLS]
    if not cols:
        return

    ensure_finance_table()
    col_idents = ", ".join(f'"{c}"' for c in cols)
    placeholders = ", ".join(f":v{i}" for i in range(len(cols)))
    updates = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in cols)
    sql = (
        f"INSERT INTO finance (race_name, {col_idents}) "
        f"VALUES (:race, {placeholders}) "
        f"ON CONFLICT (race_name) DO UPDATE SET {updates}"
    )
    params = {"race": safe_name}
    for i, c in enumerate(cols):
        params[f"v{i}"] = float(values[c])

    conn = connect_db()
    try:
        conn.execute(text(sql), params)
        conn.commit()
    finally:
        conn.close()

