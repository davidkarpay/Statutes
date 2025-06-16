import os
import sqlite3
import pytest
from unittest import mock
from Statutes_at_5 import main

def test_resumability(tmp_path):
    db_file = tmp_path / "test_statutes.db"
    # Set up config.ini for test
    with open("config.ini", "w") as f:
        f.write(f"""[DEFAULT]
db_file = {db_file}
rate_limit_seconds = 0
user_agent = test-agent
index_url = http://www.leg.state.fl.us/Statutes/index.cfm?Mode=View%20Statutes&Submenu=1&Tab=statutes
""")
    # Patch required_titles to only process one title for speed
    with mock.patch("Statutes_at_5.required_titles", ["TITLE I"]):
        main()
        # Simulate interruption: mark one statute as incomplete
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("UPDATE Statutes SET completed=0 WHERE id=(SELECT id FROM Statutes LIMIT 1)")
        conn.commit()
        conn.close()
        # Run main() again (should resume and complete the incomplete statute)
        main()
        # Check all statutes are completed
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Statutes WHERE completed=0")
        incomplete = cur.fetchone()[0]
        conn.close()
        assert incomplete == 0, "All statutes should be marked as completed after resuming."

if __name__ == "__main__":
    pytest.main([__file__])
