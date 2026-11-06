
import sqlite3
from datetime import datetime

import json
from pathlib import Path

import csv
import io

DB_NAME = "herbarium_database.db"


def get_connection():
    """
    Create a database connection.
    """
    return sqlite3.connect(DB_NAME)


def db_init():
    """
    Create tables if they do not exist.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boxes (
            unit_id TEXT PRIMARY KEY,

            current_location TEXT,
            collection_area TEXT,
            material_type TEXT,

            estimated_packet_count TEXT,

            taxonomic_clues TEXT,
            geographic_clues TEXT,
            collector_clues TEXT,

            condition TEXT,
            processing_status TEXT,
            priority TEXT,

            human_notes TEXT,

            ai_summary TEXT,
            ai_confidence_notes TEXT,

            image_paths TEXT,

            date_inventoried TEXT,
            inventoried_by TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_next_unit_id():
    """
    Generates the next unit ID.
    Example:
    HB001
    HB002
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT unit_id
        FROM boxes
        ORDER BY unit_id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return "HB001"

    last_id = result[0]

    try:
        number = int(last_id.replace("HB", ""))
        return f"HB{number + 1:03d}"

    except:
        return "HB001"


def unit_id_exists(unit_id):
    """
    Check whether a unit already exists.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM boxes
        WHERE unit_id = ?
        """,
        (unit_id,)
    )

    exists = cursor.fetchone() is not None

    conn.close()

    return exists


def save_box(data):
    """
    Save a completed herbarium box record.

    data should be a dictionary.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO boxes (
            unit_id,
            current_location,
            collection_area,
            material_type,
            estimated_packet_count,
            taxonomic_clues,
            geographic_clues,
            collector_clues,
            condition,
            processing_status,
            priority,
            human_notes,
            ai_summary,
            ai_confidence_notes,
            image_paths,
            date_inventoried,
            inventoried_by
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        data["unit_id"],
        data["current_location"],
        data["collection_area"],
        data["material_type"],
        data["estimated_packet_count"],
        data["taxonomic_clues"],
        data["geographic_clues"],
        data["collector_clues"],
        data["condition"],
        data["processing_status"],
        data["priority"],
        data["human_notes"],
        data["ai_summary"],
        data["ai_confidence_notes"],
        data["image_paths"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data["inventoried_by"]

    ))

    conn.commit()
    conn.close()


def get_all_boxes():
    """
    Retrieve all inventory records.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM boxes
        ORDER BY date_inventoried DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_box(unit_id):
    """
    Retrieve one box.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM boxes
        WHERE unit_id = ?
    """, (unit_id,))

    row = cursor.fetchone()

    conn.close()

    return row


# Export .json
def export_box_json(unit_id):
    """
    Export the complete saved database record
    for one herbarium box as a JSON file.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM boxes
        WHERE unit_id = ?
    """, (unit_id,))

    row = cursor.fetchone()

    # Get database field names
    columns = [description[0] for description in cursor.description]

    conn.close()

    if row is None:
        return None

    # Convert complete database record into dictionary
    box_data = dict(zip(columns, row))

    # Add export timestamp
    box_data["exported_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    # Create JSON export folder
    export_folder = Path(__file__).resolve().parent / "json_exports"
    export_folder.mkdir(parents=True, exist_ok=True)

    # Create JSON file
    export_path = export_folder / f"{unit_id}.json"

    with open(export_path, "w", encoding="utf-8") as file:
        json.dump(
            box_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    return export_path


def export_boxes_csv():
    """
    Export all saved herbarium box records as CSV.

    Includes every column currently stored in the boxes table.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM boxes
            ORDER BY date_inventoried DESC
        """)

        # Get all database column names
        columns = [
            description[0]
            for description in cursor.description
        ]

        rows = cursor.fetchall()

        # Create CSV in memory
        output = io.StringIO(newline="")

        writer = csv.writer(output)

        # Write column headings
        writer.writerow(columns)

        # Write all saved records
        writer.writerows(rows)

        return output.getvalue()

    finally:
        conn.close()
