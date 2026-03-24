import random, uuid
from datetime import date, timedelta
from faker import Faker
from database import init_db, get_connection

fake = Faker("en_IN")
random.seed(42)

STATES = ["Maharashtra","Tamil Nadu","Karnataka","Uttar Pradesh","Gujarat",
          "Rajasthan","West Bengal","Telangana","Madhya Pradesh","Punjab"]
PRODUCTS = ["personal","business","gold","vehicle"]
STATUSES = ["active","closed","npa","written_off"]
STATUS_W = [0.55, 0.25, 0.15, 0.05]

def rand_date(start, end):
    return (start + timedelta(days=random.randint(0,(end-start).days))).isoformat()

def seed():
    init_db()
    conn = get_connection()

    borrower_ids = []
    for _ in range(600):
        bid = f"B{uuid.uuid4().hex[:8].upper()}"
        borrower_ids.append(bid)
        conn.execute("INSERT OR IGNORE INTO borrowers VALUES (?,?,?,?,?,?)",
            (bid, random.randint(22,65), random.choice(["male","female","other"]),
             random.choice(["salaried","self_employed","farmer","business_owner"]),
             random.randint(1,3), random.choice(STATES)))

    loan_ids = []
    for _ in range(800):
        lid = f"L{uuid.uuid4().hex[:8].upper()}"
        loan_ids.append(lid)
        status = random.choices(STATUSES, STATUS_W)[0]
        amount = round(random.uniform(50000, 2000000), 2)
        outstanding = 0.0 if status=="closed" else round(amount*random.uniform(0.1,0.95),2)
        conn.execute("INSERT OR IGNORE INTO loans VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (lid, random.choice(borrower_ids), random.choice(PRODUCTS),
             rand_date(date(2023,1,1), date(2024,12,31)),
             amount, outstanding, random.choice(STATES),
             f"BR{random.randint(1,50):03d}", status,
             round(random.uniform(8.5,24.0),2), random.choice([12,24,36,48,60])))

    for lid in loan_ids:
        due = date(2024,1,1) + timedelta(days=random.randint(0,60))
        for _ in range(random.randint(3,12)):
            rid = f"R{uuid.uuid4().hex[:8].upper()}"
            amount_due = round(random.uniform(3000,50000),2)
            paid = random.random() > 0.2
            if paid:
                delay = random.randint(-5,30)
                paid_date = (due+timedelta(days=delay)).isoformat()
                conn.execute("INSERT OR IGNORE INTO repayments VALUES (?,?,?,?,?,?,?)",
                    (rid,lid,due.isoformat(),paid_date,amount_due,amount_due,max(0,delay)))
            else:
                conn.execute("INSERT OR IGNORE INTO repayments VALUES (?,?,?,?,?,?,?)",
                    (rid,lid,due.isoformat(),None,amount_due,0.0,random.randint(30,180)))
            due += timedelta(days=30)

    conn.commit()
    conn.close()
    print("Seeded: 600 borrowers, 800 loans, repayments done.")

if __name__ == "__main__":
    seed()