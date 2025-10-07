import os
import argparse
import secrets
import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYSQL_PORT", "3307")),
        user=os.environ.get("MYSQL_USER", "lab"),
        password=os.environ.get("MYSQL_PASSWORD", "labpass"),
        database=os.environ.get("MYSQL_DB", "puny"),
    )


def seed_info(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT email, COLLATION(email) FROM users LIMIT 1")
        row = cur.fetchone()
        if row:
            print(f"Stored victim email in DB: {row[0]}  (COLLATION={row[1]})")


def vulnerable_reset_flow(conn, input_email: str) -> None:
    """
    Simulates a vulnerable reset flow:
      1) Look up by user-supplied email (collation equates accented letters)
      2) Issue token in DB for matched user
      3) 'Send' reset link to the user-supplied email (attacker-controlled)
    """
    print("\n[ Vulnerable flow ]")
    print(f"User supplied email (attacker-controlled): {input_email}")

    with conn.cursor() as cur:
        cur.execute("SELECT id, email FROM users WHERE email = %s", (input_email,))
        row = cur.fetchone()
        if not row:
            print("Lookup: NOT FOUND in DB (no token issued)")
            return

        user_id, canonical_email = row
        print(f"Lookup: MATCHED DB row for canonical email: {canonical_email}")

        token = secrets.token_urlsafe(24)
        cur.execute("UPDATE users SET reset_token = %s WHERE id = %s", (token, user_id))
        conn.commit()

        print("DB: reset token issued for the real account")
        print(f"Would email reset link to: {input_email}")
        print("NOTE: Because MySQL matched on collation, the attacker address was used for 'sending'.")


def safe_reset_flow(conn, input_email: str) -> None:
    """
    Demonstrates the safe pattern:
      - Lookup by user input
      - BUT send to the email fetched from DB, not the input
    """
    print("\n[ Safe flow ]")
    print(f"User supplied email: {input_email}")

    with conn.cursor() as cur:
        cur.execute("SELECT id, email FROM users WHERE email = %s", (input_email,))
        row = cur.fetchone()
        if not row:
            print("Lookup: NOT FOUND in DB (no token issued)")
            return

        user_id, canonical_email = row
        token = secrets.token_urlsafe(24)
        cur.execute("UPDATE users SET reset_token = %s WHERE id = %s", (token, user_id))
        conn.commit()

        print(f"Would email reset link to: {canonical_email}")
        print("Safe: The email used for sending comes from DB, not the input.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--attack-email",
        "-a",
        default="victdm@gmail.com",  # 'victím' (i with acute)
        help="Attacker-controlled email to submit in reset form",
    )
    args = parser.parse_args()

    print("Connecting to MySQL ...")
    conn = get_db_connection()
    try:
        seed_info(conn)
        vulnerable_reset_flow(conn, args.attack_email)
        safe_reset_flow(conn, args.attack_email)
    finally:
        conn.close()


if __name__ == "__main__":
    main()


