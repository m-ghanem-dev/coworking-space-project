import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from flask import jsonify
from sqlalchemy import and_, text
from random import randint

from config import app, db


port_number = int(os.environ.get("APP_PORT", 5153))
sql_files = [ "db/1_create_tables.sql", "db/2_seed_users.sql","db/3_seed_tokens.sql"]

def run_sql_files_once(file_paths, marker_path=".init_sql_applied"):
    if os.path.exists(marker_path):
        app.logger.info("Init SQL already applied. Skipping.")
        return

    with app.app_context():
        try:
            for path in file_paths:
                with open(path, "r") as f:
                    sql = f.read()
                db.session.execute(text(sql))
                app.logger.info(f"Executed SQL file: {path}")

            db.session.commit()

            # Create the marker file
            with open(marker_path, "w") as marker:
                marker.write("applied\n")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed during SQL execution: {e}")


@app.route("/health_check")
def health_check():
    return "ok"


@app.route("/readiness_check")
def readiness_check():
    try:
        count = db.session.execute(text("SELECT COUNT(*) FROM tokens")).scalar()
    except Exception as e:
        app.logger.error(e)
        return "failed", 500
    else:
        return "ok"


def get_daily_visits():
    with app.app_context():
        result = db.session.execute(text("""
        SELECT Date(created_at) AS date,
            Count(*)         AS visits
        FROM   tokens
        WHERE  used_at IS NOT NULL
        GROUP  BY Date(created_at)
        """))

        response = {}
        for row in result:
            response[str(row[0])] = row[1]

        app.logger.info(response)

    return response


@app.route("/api/reports/daily_usage", methods=["GET"])
def daily_visits():
    return jsonify(get_daily_visits())


@app.route("/api/reports/user_visits", methods=["GET"])
def all_user_visits():
    result = db.session.execute(text("""
    SELECT t.user_id,
        t.visits,
        users.joined_at
    FROM   (SELECT tokens.user_id,
                Count(*) AS visits
            FROM   tokens
            GROUP  BY user_id) AS t
        LEFT JOIN users
                ON t.user_id = users.id;
    """))

    response = {}
    for row in result:
        response[row[0]] = {
            "visits": row[1],
            "joined_at": str(row[2])
        }
    
    return jsonify(response)


scheduler = BackgroundScheduler()
job = scheduler.add_job(get_daily_visits, 'interval', seconds=30)
scheduler.start()

if __name__ == "__main__":
    run_sql_files_once(sql_files)
    app.run(host="0.0.0.0", port=port_number)
