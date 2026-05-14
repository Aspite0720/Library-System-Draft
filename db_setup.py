import mysql.connector
from mysql.connector import Error
import hashlib
from db_config import DB_CONFIG

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    """Creates the database, tables, and seeds default data."""
    cfg = dict(DB_CONFIG)
    db_name = cfg.pop("database")

    try:
        # Connect without specifying the database first
        conn = mysql.connector.connect(**cfg)
        cur = conn.cursor()

        # ── Create Database ──────────────────────────
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        cur.execute(f"USE `{db_name}`")

        # ── Tables ───────────────────────────────────

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Admin (
                AdminID   INT AUTO_INCREMENT PRIMARY KEY,
                Name      VARCHAR(100) NOT NULL,
                Username  VARCHAR(50)  NOT NULL UNIQUE,
                Password  VARCHAR(255) NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Student (
                StudentID  INT AUTO_INCREMENT PRIMARY KEY,
                Name       VARCHAR(100) NOT NULL,
                Username   VARCHAR(50)  NOT NULL UNIQUE,
                Password   VARCHAR(255) NOT NULL,
                Course     VARCHAR(100),
                Email      VARCHAR(100),
                ContactNum VARCHAR(20),
                Status     ENUM('active','inactive') DEFAULT 'active'
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Laptop (
                LaptopID    INT AUTO_INCREMENT PRIMARY KEY,
                LaptopModel VARCHAR(100) NOT NULL,
                SerialNo    VARCHAR(100) NOT NULL UNIQUE,
                Status      ENUM('Available','Borrowed','Under Repair','Lost') DEFAULT 'Available',
                AdminID     INT,
                FOREIGN KEY (AdminID) REFERENCES Admin(AdminID)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Borrow (
                BorrowID   INT AUTO_INCREMENT PRIMARY KEY,
                StudentID  INT NOT NULL,
                LaptopID   INT NOT NULL,
                AdminID    INT,
                BorrowDate DATETIME,
                DueDate    DATETIME,
                ReturnDate DATETIME,
                Status     ENUM('Pending','Approved','Rejected','Returned','Overdue') DEFAULT 'Pending',
                Notes      TEXT,
                FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
                FOREIGN KEY (LaptopID)  REFERENCES Laptop(LaptopID),
                FOREIGN KEY (AdminID)   REFERENCES Admin(AdminID)
            )
        """)

        # ── Seed: Default Admin ───────────────────────
        cur.execute("""
            INSERT IGNORE INTO Admin (Name, Username, Password)
            VALUES ('Administrator', 'admin', %s)
        """, (hash_pw("admin123"),))

        # ── Seed: Sample Laptops ─────────────────────
        cur.execute("SELECT COUNT(*) FROM Laptop")
        if cur.fetchone()[0] == 0:
            laptops = [
                ("Dell Inspiron 15",  "SN-DELL-001"),
                ("HP Pavilion 14",    "SN-HP-001"),
                ("Lenovo IdeaPad 3",  "SN-LEN-001"),
                ("Acer Aspire 5",     "SN-ACER-001"),
                ("ASUS VivoBook 15",  "SN-ASUS-001"),
            ]
            cur.executemany(
                "INSERT INTO Laptop (LaptopModel, SerialNo) VALUES (%s, %s)", laptops
            )

        conn.commit()
        cur.close()
        conn.close()
        print("✔ Database setup complete.")

    except Error as e:
        print(f"✘ DB Setup Error: {e}")
        raise


# Run directly to set up DB without launching the app
if __name__ == "__main__":
    setup_database()
    print("You can now run elibrary_system.py")
