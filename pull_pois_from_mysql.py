import os
import sqlite3
import mysql.connector
from mysql.connector import errorcode
import POIsDB_pb2 as POIsDB

POIS_QUERY = """select
	                poi.name,
	                wpp.obj_Cell_Id,
	                wpp.origin_X,
	                wpp.origin_Y,
	                wpp.origin_Z
                from
	                ace_world.points_of_interest poi
                join ace_world.weenie_properties_position wpp on
	                poi.weenie_Class_Id = wpp.object_Id
                where (wpp.obj_Cell_Id & 0xFFFF) >= 0x100 = 0 /* Outside */"""

CREATE_TABLE_POIS_QUERY = """CREATE TABLE IF NOT EXISTS pois (
                                name TEXT,
                                obj_cell_id INTEGER,
                                origin_x REAL,
                                origin_y REAL,
                                origin_z REAL
                            )"""

INSERT_POI_QUERY = """INSERT INTO pois
                        (name, obj_cell_id, origin_x, origin_y, origin_z)
                      VALUES
                        (:name, :obj_cell_id, :origin_x, :origin_y, :origin_z)"""

ENVIRONMENT_VARIABLES = {
    "MYSQL_USER",
    "MYSQL_PASS",
    "MYSQL_HOST",
    "MYSQL_PORT",
    "MYSQL_DB",
}
if unset_environment_variables := ENVIRONMENT_VARIABLES.difference(os.environ):
    raise EnvironmentError(
        f"Failed because {unset_environment_variables} is/are not set."
    )


def create_sqlite_connection(db_filename):
    try:
        conn = sqlite3.connect(db_filename)
    except sqlite3.Error as err:
        print(err)

    return conn


def insert_pois_into_sqlite(pois_db, conn):
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_POIS_QUERY)

    pois = [
        {
            "name": poi.name,
            "obj_cell_id": poi.obj_cell_id,
            "origin_x": poi.origin_x,
            "origin_y": poi.origin_y,
            "origin_z": poi.origin_z,
        }
        for poi in pois_db.pois
    ]

    cursor.executemany(INSERT_POI_QUERY, pois)
    conn.commit()

    print(f"Wrote {len(pois)} POIs to SQLite.")


def query_for_pois(cursor) -> POIsDB:
    cursor.execute(POIS_QUERY)

    pois_db = POIsDB.POIsDB()

    for name, cell, x, y, z in cursor:
        print(name, cell, x, y, z)
        poi = pois_db.pois.add()
        poi.name = name
        poi.obj_cell_id = cell
        poi.origin_x = float(x)
        poi.origin_y = y
        poi.origin_z = z
        print(poi)

    return pois_db


def connect_to_mysql_and_get_pois() -> POIsDB:
    pois_db: POIsDB = None

    try:
        conn = mysql.connector.connect(
            user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASS"],
            host=os.environ["MYSQL_HOST"],
            database=os.environ["MYSQL_DB"],
            port=int(os.environ["MYSQL_PORT"]),
        )
        cursor = conn.cursor()

        pois_db = query_for_pois(cursor)

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
        else:
            print(err)
    else:
        conn.close()

    return pois_db


if __name__ == "__main__":
    pois_db = connect_to_mysql_and_get_pois()
    print(f"Found {len(pois_db.pois)} POIs in the database.")

    with open("pois_db.binpb", "wb") as f:
        f.write(pois_db.SerializeToString())
        print(f"Wrote {len(pois_db.pois)} POIs to Protobuf file.")

    check = POIsDB.POIsDB()
    with open("pois_db.binpb", "rb") as f:
        check.ParseFromString(f.read())
        print(f"Read {len(check.pois)} POIs from Protobuf file.")

    for poi in check.pois:
        print(poi)

    assert len(check.pois) == len(pois_db.pois)

    try:
        os.remove("pois.db")
    except OSError:
        pass

    conn = create_sqlite_connection("pois.db")
    insert_pois_into_sqlite(pois_db, conn)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pois")
    row = cursor.fetchone()
    print(f"Read {row[0]} POIs from SQLite.")
    assert row[0] == len(pois_db.pois)
