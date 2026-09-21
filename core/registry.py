import sqlite3
import os
from datetime import datetime


DB_PATH = "/opt/deploy-manager/registry/deploy-manager.db"


def get_connection():
    return sqlite3.connect(DB_PATH)





def deactivate_image_versions(app_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE image_versions
        SET status='available'
        WHERE app_id=?
        """,
        (app_id,)
    )

    conn.commit()

    conn.close()




def image_version_exists(full_image):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM image_versions
        WHERE full_image=?
        """,
        (full_image,)
    )

    row = cursor.fetchone()

    conn.close()

    return row[0] if row else None





def set_active_image_version(app_id, version_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE image_versions
        SET status='available'
        WHERE app_id=?
        """,
        (app_id,)
    )


    cursor.execute(
        """
        UPDATE image_versions
        SET status='active'
        WHERE id=?
        """,
        (version_id,)
    )


    conn.commit()

    conn.close()



def activate_image_version(version_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE image_versions
        SET status='active'
        WHERE id=?
        """,
        (version_id,)
    )

    conn.commit()

    conn.close()



def add_image_version(
    app_id,
    image_name,
    image_tag,
    full_image,
    status="available"
):

    conn = get_connection()

    cursor = conn.cursor()

    now = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO image_versions
        (
            app_id,
            image_name,
            image_tag,
            full_image,
            status,
            created_at
        )
        VALUES (?,?,?,?,?,?)
        """,
        (
            app_id,
            image_name,
            image_tag,
            full_image,
            status,
            now
        )
    )

    conn.commit()
    conn.close()




def get_image_version_by_tag(app_id, tag):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            full_image,
            image_tag
        FROM image_versions
        WHERE app_id=? AND image_tag=?
        """,
        (
            app_id,
            tag
        )
    )

    row = cursor.fetchone()

    conn.close()

    return row



def get_image_versions(app_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            image_tag,
            full_image,
            status,
            created_at
        FROM image_versions
        WHERE app_id=?
        ORDER BY id DESC
        """,
        (app_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows




def get_cleanup_versions(app_id, keep=3):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            full_image,
            status
        FROM image_versions
        WHERE app_id=?
        ORDER BY id DESC
        """,
        (app_id,)
    )

    rows = cursor.fetchall()

    conn.close()


    result = []

    kept = 0

    for row in rows:

        if row[2] == "active":

            continue

        if kept < keep:

            kept += 1

        else:

            result.append(row)


    return result




def delete_image_version(version_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM image_versions
        WHERE id=?
        """,
        (version_id,)
    )

    conn.commit()

    conn.close()



def update_image_version_status(
    version_id,
    status
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE image_versions
        SET status=?
        WHERE id=?
        """,
        (
            status,
            version_id
        )
    )

    conn.commit()
    conn.close()



def init_db():

    os.makedirs(
        os.path.dirname(DB_PATH),
        exist_ok=True
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        path TEXT NOT NULL,
        type TEXT,
        container_name TEXT,
        image_name TEXT,
        compose_file TEXT,
        docker_network TEXT,
        status TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS domains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER,
        domain TEXT,
        nginx_config TEXT,
        ssl_enabled INTEGER DEFAULT 0,
        UNIQUE(app_id, domain),
        FOREIGN KEY(app_id)
        REFERENCES applications(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER UNIQUE,
        type TEXT,
        method TEXT,
        remote_url TEXT,
        branch TEXT,
        FOREIGN KEY(app_id)
        REFERENCES applications(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS databases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER UNIQUE,
        engine TEXT,
        host TEXT,
        database_name TEXT,
        username TEXT,
        FOREIGN KEY(app_id)
        REFERENCES applications(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER,
        backup_type TEXT,
        path TEXT,
        status TEXT,
        created_at TEXT,
        FOREIGN KEY(app_id)
        REFERENCES applications(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS image_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER,
        image_name TEXT,
        image_tag TEXT,
        full_image TEXT,
        status TEXT,
        created_at TEXT,
        FOREIGN KEY(app_id)
        REFERENCES applications(id)
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deployments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id INTEGER,
        action TEXT,
        status TEXT,
        image_before TEXT,
        image_after TEXT,
        env_backup TEXT,
        message TEXT,
        created_at TEXT,
        FOREIGN KEY(app_id)
        REFERENCES applications(id)
    )
    """)

    conn.commit()
    conn.close()



def upsert_application(data):

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
    INSERT INTO applications
    (
        name,path,type,
        container_name,image_name,
        compose_file,docker_network,
        status,created_at,updated_at
    )
    VALUES (?,?,?,?,?,?,?,?,?,?)

    ON CONFLICT(name)
    DO UPDATE SET

    path=excluded.path,
    type=excluded.type,
    container_name=excluded.container_name,
    image_name=excluded.image_name,
    compose_file=excluded.compose_file,
    docker_network=excluded.docker_network,
    status=excluded.status,
    updated_at=excluded.updated_at
    """,
    (
        data["name"],
        data["path"],
        data.get("type"),
        data.get("container_name"),
        data.get("image_name"),
        data.get("compose_file"),
        ",".join(data.get("docker_network", [])),
        data.get("status"),
        now,
        now
    ))

    conn.commit()

    cursor.execute(
        "SELECT id FROM applications WHERE name=?",
        (data["name"],)
    )

    app_id = cursor.fetchone()[0]

    conn.close()

    return app_id



def add_domain(app_id, domain_data):

    conn = get_connection()
    cursor = conn.cursor()

    for domain in domain_data.get("domains", []):

        cursor.execute("""
        INSERT INTO domains
        (
            app_id,
            domain,
            nginx_config
        )
        VALUES (?,?,?)

        ON CONFLICT(app_id,domain)
        DO UPDATE SET
        nginx_config=excluded.nginx_config
        """,
        (
            app_id,
            domain,
            domain_data.get("config")
        ))

    conn.commit()
    conn.close()



def add_source(app_id, source):

    if not source:
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO sources
    (
        app_id,type,method,
        remote_url,branch
    )
    VALUES (?,?,?,?,?)

    ON CONFLICT(app_id)
    DO UPDATE SET

    type=excluded.type,
    method=excluded.method,
    remote_url=excluded.remote_url,
    branch=excluded.branch
    """,
    (
        app_id,
        source.get("type"),
        source.get("method"),
        source.get("remote"),
        source.get("branch")
    ))

    conn.commit()
    conn.close()



def add_database(app_id, database):

    if not database:
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO databases
    (
        app_id,engine,
        host,database_name,
        username
    )
    VALUES (?,?,?,?,?)

    ON CONFLICT(app_id)
    DO UPDATE SET

    engine=excluded.engine,
    host=excluded.host,
    database_name=excluded.database_name,
    username=excluded.username
    """,
    (
        app_id,
        database.get("engine"),
        database.get("host"),
        database.get("database"),
        database.get("username")
    ))

    conn.commit()
    conn.close()



def get_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """
    )

    tables = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return tables


def add_deployment(
    app_id,
    action,
    status,
    image_before=None,
    image_after=None,
    env_backup=None,
    message=None
):

    conn = get_connection()

    cursor = conn.cursor()


    now = datetime.now().isoformat()


    cursor.execute(
        """
        INSERT INTO deployments
        (
            app_id,
            action,
            status,
            image_before,
            image_after,
            env_backup,
            message,
            created_at
        )
        VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            app_id,
            action,
            status,
            image_before,
            image_after,
            env_backup,
            message,
            now
        )
    )


    conn.commit()

    deployment_id = cursor.lastrowid

    conn.close()

    return deployment_id



def get_deployments(app_id=None):

    conn = get_connection()

    cursor = conn.cursor()


    if app_id:

        cursor.execute(
            """
            SELECT *
            FROM deployments
            WHERE app_id=?
            ORDER BY id DESC
            """,
            (app_id,)
        )

    else:

        cursor.execute(
            """
            SELECT *
            FROM deployments
            ORDER BY id DESC
            """
        )


    result = cursor.fetchall()


    conn.close()


    return result


def get_application_by_path(path):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id,name
        FROM applications
        WHERE path=?
        """,
        (path,)
    )

    result = cursor.fetchone()

    conn.close()

    return result


def update_deployment_status(
    deployment_id,
    status,
    message=None,
    image_after=None
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE deployments
        SET status=?,
            message=?,
            image_after=?
        WHERE id=?
        """,
        (
            status,
            message,
            image_after,
            deployment_id
        )
    )


    conn.commit()
    conn.close()


def get_last_successful_deployment(app_id):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM deployments
        WHERE app_id=?
        AND status='success'
        AND action='rebuild'
        ORDER BY id DESC
        LIMIT 1
        """,
        (app_id,)
    )


    result = cursor.fetchone()


    conn.close()


    return result


def update_deployment_full(
    deployment_id,
    status,
    message=None,
    image_after=None
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE deployments
        SET status=?,
            message=?,
            image_after=?
        WHERE id=?
        """,
        (
            status,
            message,
            image_after,
            deployment_id
        )
    )

    conn.commit()
    conn.close()


def get_previous_rebuild(app_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM deployments
        WHERE app_id=?
        AND status='success'
        AND action='rebuild'
        ORDER BY id DESC
        LIMIT 1 OFFSET 1
        """,
        (app_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result


def mark_running_deployments_failed():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE deployments
        SET status='failed',
            message='Interrupted deployment'
        WHERE status='running'
        """
    )

    conn.commit()

    conn.close()

def add_backup(app_id, backup_type, path, status="success"):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO backups
        (
            app_id,
            backup_type,
            path,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            app_id,
            backup_type,
            path,
            status,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_backups(app_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM backups
        WHERE app_id=?
        ORDER BY id DESC
        """,
        (app_id,)
    )

    result = cursor.fetchall()

    conn.close()

    return result


def get_last_backup(app_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM backups
        WHERE app_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (app_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result

