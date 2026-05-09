import mysql.connector
from datetime import date, datetime
import os
import time
import getpass
import readchar

# ================= RICH UI =================
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.align import Align
from rich import box

console = Console()

# ================= SAFE DB CONNECTION (WITH RETRY) =================
import time

MAX_RETRIES = 3
attempt = 0

while attempt < MAX_RETRIES:
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sqlwordpass18",
            database="editvault"
        )

        cursor = conn.cursor()

        console.print(Align.center("[green]Database Connected Successfully[/green]"))
        break

    except mysql.connector.Error as e:
        attempt += 1
        console.print(Align.center(f"[red]DB Connection Failed (Attempt {attempt}/{MAX_RETRIES})[/red]"))
        console.print(Align.center(f"[yellow]{e}[/yellow]"))

        time.sleep(2)

else:
    console.print(Align.center("[bold red]Could not connect to database. Exiting...[/bold red]"))
    exit()
    
# ================= SCREEN CLEAR (FASTER + CLEANER) =================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# ================= HEADER (PRO STYLING) =================
def header(title):
    console.print(Panel.fit(
        Align.center(f"[bold cyan]{title}[/bold cyan]"),
        border_style="cyan",
        padding=(1, 2)
    ))


# ================= PAUSE (MORE CONTROLLED UX) =================
def pause():
    console.print(Align.center("[dim]Press Enter to continue...[/dim]"))
    input()


# ================= LOADING SPINNER (PRO VERSION) =================
def spinner(msg="Loading"):
    with Progress(transient=True) as progress:
        task = progress.add_task(f"[cyan]{msg}...", total=100)

        for _ in range(100):
            time.sleep(0.01)
            progress.update(task, advance=1)
    
# ================= STATUS COLOR (SCALABLE) =================
def color_status(status):
    colors = {
        "pending": "yellow",
        "completed": "green",
        "in progress": "cyan",
        "cancelled": "red",
    }

    status = str(status).strip().lower()
    color = colors.get(status, "red")

    return f"[{color}]{status}[/{color}]"         
            
# ================= TABLE (PRO VERSION) =================
def print_table(data, headers):
    if not data:
        console.print(Align.center("[red]No data available[/red]"))
        return

    table = Table(
        box=box.ROUNDED,
        show_lines=True,
        header_style="bold cyan"
    )

    table.add_column("S.No", style="cyan", justify="center")

    headers_lower = [str(h).strip().lower() for h in headers]

    for h in headers:
        table.add_column(str(h), style="white")

    for i, row in enumerate(data, 1):
        new_row = [str(i)]

        for j, val in enumerate(row):
            if j < len(headers_lower) and headers_lower[j] == "status":
                val = color_status(val)

            new_row.append(str(val))

        table.add_row(*new_row)

    console.print(Align.center(table))
    
# ================= LOGIN (PRO VERSION) =================
def login():
    attempts = 3

    while attempts > 0:
        try:
            clear()
            header("LOGIN SYSTEM")

            console.print(Align.center(f"[yellow]Attempts left: {attempts}[/yellow]"))

            username = input("Username: ").strip()
            password = getpass.getpass("Password: ").strip()

            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password)
            )

            if cursor.fetchone():
                console.print(Align.center("[green]Login Successful[/green]"))
                time.sleep(1)
                return True

            else:
                attempts -= 1
                console.print(Align.center("[red]Invalid Credentials[/red]"))
                time.sleep(1)

        except Exception as e:
            console.print(Align.center(f"[red]Login Error: {e}[/red]"))
            pause()

    console.print(Align.center("[bold red]Too many failed attempts. Exiting...[/bold red]"))
    time.sleep(1)
    return False

# ================= AUTO ALERT POPUP (PRO VERSION) =================
def auto_alert_popup():
    clear()
    header("URGENT & OVERDUE ALERTS")

    try:
        cursor.execute("""
        SELECT c.name, p.project_type, p.description, p.deadline
        FROM projects p 
        JOIN clients c ON p.client_id = c.client_id
        WHERE p.status != 'completed'
        ORDER BY p.deadline
        """)

        rows = cursor.fetchall()
        today = date.today()

        data = []

        for name, ptype, desc, dl in rows:

            if not dl:
                continue

            days = (dl - today).days

            alert = None
            if days < 0:
                alert = f"OVERDUE ({abs(days)} days)"
            elif days <= 2:
                alert = f"URGENT ({days} days left)"

            if alert:
                data.append([name, ptype, desc, dl, alert])

        if data:
            print_table(
                data,
                ["Client", "Project", "Description", "Deadline", "Alert"]
            )
        else:
            console.print(Align.center("[green]All projects are on track 🎉[/green]"))

    except Exception as e:
        console.print(Align.center(f"[red]Alert Error: {e}[/red]"))

    pause()
    
# ================= SAFE INPUT SYSTEM (PRO VERSION) =================
def safe_int(msg):
    while True:
        val = input(f"{msg} (0 = cancel): ").strip()

        if val == "0":
            return None

        try:
            return int(val)
        except ValueError:
            console.print(Align.center("[red]Invalid integer![/red]"))


def safe_float(msg):
    while True:
        val = input(f"{msg} (0 = cancel): ").strip()

        if val == "0":
            return None

        try:
            return float(val)
        except ValueError:
            console.print(Align.center("[red]Invalid number![/red]"))


def get_name(msg):
    while True:
        val = input(f"{msg} (0 = cancel): ").strip()

        if val == "0":
            return None

        if len(val) >= 2:
            return val

        console.print(Align.center("[red]Must be at least 2 characters![/red]"))
        
# ================= DATE (PRO VERSION) =================
def parse_date(x):
    formats = ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y")

    x = x.strip()

    for f in formats:
        try:
            return datetime.strptime(x, f).date()
        except ValueError:
            continue

    return None


def get_date():
    while True:
        val = input("Date (DD-MM-YYYY or YYYY-MM-DD, 0 cancel): ").strip()

        if val == "0":
            return None

        d = parse_date(val)

        if d:
            return d

        console.print(Align.center("[red]Invalid date format![/red]"))

# ================= CLIENT =================

def view_clients():
    clear()
    header("CLIENTS")
    spinner()

    cursor.execute("SELECT * FROM clients")
    data = cursor.fetchall()

    print_table(data, ["ID", "Name", "Phone", "Email"])
    pause()


def add_client():
    clear()
    header("ADD CLIENT")

    name = get_name("Name")
    if not name:
        return

    phone = get_name("Phone")
    if not phone:
        return

    email = get_name("Email")
    if not email:
        return

    try:
        cursor.execute(
            "INSERT INTO clients(name, phone, email) VALUES(%s, %s, %s)",
            (name, phone, email)
        )
        conn.commit()

        console.print(Align.center("[green]Client Added[/green]"))

    except Exception as e:
        console.print(Align.center(f"[red]Error adding client: {e}[/red]"))

    pause()


def search_client():
    clear()
    header("SEARCH CLIENT")

    key = input("Search (Name/Phone/Email): ").strip()

    cursor.execute("""
        SELECT * FROM clients
        WHERE name LIKE %s OR phone LIKE %s OR email LIKE %s
    """, (f"%{key}%", f"%{key}%", f"%{key}%"))

    data = cursor.fetchall()

    print_table(data, ["ID", "Name", "Phone", "Email"])
    pause()


def update_client():
    view_clients()

    cid = safe_int("Client ID")
    if not cid:
        return

    print("1. Name  2. Phone  3. Email")
    ch = input("Choose field: ").strip()

    field_map = {
        "1": ("name", "New Name"),
        "2": ("phone", "New Phone"),
        "3": ("email", "New Email")
    }

    if ch not in field_map:
        console.print(Align.center("[red]Invalid option![/red]"))
        pause()
        return

    field, prompt = field_map[ch]
    val = get_name(prompt)

    if not val:
        return

    try:
        cursor.execute(
            f"UPDATE clients SET {field}=%s WHERE client_id=%s",
            (val, cid)
        )
        conn.commit()

        console.print(Align.center("[green]Client Updated[/green]"))

    except Exception as e:
        console.print(Align.center(f"[red]Error updating client: {e}[/red]"))

    pause()


def delete_client():
    view_clients()

    cid = safe_int("Client ID")
    if not cid:
        return

    confirm = input("Are you sure? (y/n): ").strip().lower()
    if confirm != "y":
        console.print(Align.center("[yellow]Cancelled[/yellow]"))
        pause()
        return

    try:
        cursor.execute("DELETE FROM clients WHERE client_id=%s", (cid,))
        conn.commit()

        console.print(Align.center("[red]Client Deleted[/red]"))

    except Exception as e:
        console.print(Align.center(f"[red]Error deleting client: {e}[/red]"))

    pause()

# ================= PROJECT =================

def add_project():
    clear()
    header("ADD PROJECT")

    view_clients()

    cid = safe_int("Client ID")
    if not cid:
        return

    typ = get_name("Type")
    if not typ:
        return

    desc = input("Description: ").strip()

    dl = get_date()
    if not dl:
        return

    try:
        cursor.execute("""
            INSERT INTO projects(client_id, project_type, description, deadline, status)
            VALUES(%s, %s, %s, %s, 'Pending')
        """, (cid, typ, desc, dl))

        conn.commit()
        console.print(Align.center("[green]Project Added[/green]"))

    except Exception as e:
        console.print(Align.center(f"[red]Error adding project: {e}[/red]"))

    pause()


def view_projects():
    clear()
    header("PROJECTS")
    spinner()

    cursor.execute("""
        SELECT p.project_id, c.name, p.project_type, p.description, p.deadline, p.status
        FROM projects p
        JOIN clients c ON p.client_id = c.client_id
    """)

    data = cursor.fetchall()
    print_table(data, ["ID", "Client", "Type", "Desc", "Deadline", "Status"])

    pause()


def search_project():
    clear()
    header("SEARCH PROJECT")

    key = input("Search (Client/Type/Status): ").strip()

    cursor.execute("""
        SELECT p.project_id, c.name, p.project_type, p.description, p.deadline, p.status
        FROM projects p
        JOIN clients c ON p.client_id = c.client_id
        WHERE c.name LIKE %s OR p.project_type LIKE %s OR p.status LIKE %s
    """, (f"%{key}%", f"%{key}%", f"%{key}%"))

    data = cursor.fetchall()
    print_table(data, ["ID", "Client", "Type", "Desc", "Deadline", "Status"])

    pause()


def update_project():
    view_projects()

    pid = safe_int("Project ID")
    if not pid:
        return

    print("1. Type  2. Description  3. Date  4. Status")
    ch = input("Choose option: ").strip()

    try:
        if ch == "1":
            val = get_name("New Type")
            field = "project_type"

        elif ch == "2":
            val = input("New Desc: ").strip()
            field = "description"

        elif ch == "3":
            val = get_date()
            field = "deadline"

        elif ch == "4":
            val = get_name("Status")
            field = "status"

            if val.lower() == "completed":
                cursor.execute("""
                    UPDATE projects 
                    SET status=%s, completed_date=%s
                    WHERE project_id=%s
                """, (val, date.today(), pid))
            else:
                cursor.execute("""
                    UPDATE projects 
                    SET status=%s, completed_date=NULL
                    WHERE project_id=%s
                """, (val, pid))

            conn.commit()
            console.print(Align.center("[green]Project Updated[/green]"))
            pause()
            return

        else:
            console.print(Align.center("[red]Invalid option![/red]"))
            pause()
            return

        if not val:
            return

        cursor.execute(
            f"UPDATE projects SET {field}=%s WHERE project_id=%s",
            (val, pid)
        )
        conn.commit()

        console.print(Align.center("[green]Project Updated[/green]"))

    except Exception as e:
        console.print(Align.center(f"[red]Error updating project: {e}[/red]"))

    pause()


def delete_project():
    view_projects()

    pid = safe_int("Project ID")
    if not pid:
        return

    confirm = input("Are you sure? (y/n): ").strip().lower()
    if confirm != "y":
        console.print(Align.center("[yellow]Cancelled[/yellow]"))
        pause()
        return

    try:
        cursor.execute("DELETE FROM projects WHERE project_id=%s", (pid,))
        conn.commit()

        console.print(Align.center("[red]Project Deleted[/red]"))

    except Exception as e:
        console.print(Align.center(f"[red]Error deleting project: {e}[/red]"))

    pause()

# ================= PAYMENT =================

def add_payment():
    clear()
    header("ADD PAYMENT")

    view_projects()

    pid = safe_int("Project ID")
    if not pid:
        return

    amt = safe_float("Amount")
    if not amt:
        return

    status = get_name("Status")
    if not status:
        return

    try:
        if status.lower() == "completed":
            cursor.execute("""
                INSERT INTO payments(
                    project_id, amount_paid, payment_date, payment_status, completed_date
                )
                VALUES(%s, %s, %s, %s, %s)
            """, (pid, amt, date.today(), status, date.today()))
        else:
            cursor.execute("""
                INSERT INTO payments(
                    project_id, amount_paid, payment_date, payment_status, completed_date
                )
                VALUES(%s, %s, %s, %s, NULL)
            """, (pid, amt, date.today(), status))

        conn.commit()
        console.print(Align.center("[green]Payment Added[/green]"))

    except Exception as e:
        console.print(Align.center(f"[red]Error adding payment: {e}[/red]"))

    pause()


def view_payments():
    clear()
    header("PAYMENTS")
    spinner()

    cursor.execute("""
        SELECT pay.payment_id, c.name, p.project_type,
               pay.amount_paid,
               COALESCE(pay.completed_date, pay.payment_date),
               pay.payment_status
        FROM payments pay
        JOIN projects p ON pay.project_id = p.project_id
        JOIN clients c ON p.client_id = c.client_id
    """)

    data = cursor.fetchall()
    print_table(data, ["ID", "Client", "Project", "Amount", "Date", "Status"])

    pause()


def search_payment():
    clear()
    header("SEARCH PAYMENT")

    key = input("Search (Client/Status): ").strip()

    cursor.execute("""
        SELECT pay.payment_id, c.name, p.project_type,
               pay.amount_paid, pay.payment_date, pay.payment_status
        FROM payments pay
        JOIN projects p ON pay.project_id = p.project_id
        JOIN clients c ON p.client_id = c.client_id
        WHERE c.name LIKE %s OR pay.payment_status LIKE %s
    """, (f"%{key}%", f"%{key}%"))

    print_table(cursor.fetchall(), ["ID", "Client", "Project", "Amount", "Date", "Status"])
    pause()


def update_payment():
    view_payments()

    pid = safe_int("Payment ID")
    if not pid:
        return

    print("1. Amount  2. Status")
    ch = input("Choose option: ").strip()

    try:
        if ch == "1":
            val = safe_float("New Amount")
            if not val:
                return

            cursor.execute("""
                UPDATE payments 
                SET amount_paid=%s 
                WHERE payment_id=%s
            """, (val, pid))

        elif ch == "2":
            val = get_name("New Status")
            if not val:
                return

            if val.lower() == "completed":
                cursor.execute("""
                    UPDATE payments 
                    SET payment_status=%s, completed_date=%s
                    WHERE payment_id=%s
                """, (val, date.today(), pid))
            else:
                cursor.execute("""
                    UPDATE payments 
                    SET payment_status=%s, completed_date=NULL
                    WHERE payment_id=%s
                """, (val, pid))

        else:
            console.print(Align.center("[red]Invalid option![/red]"))
            pause()
            return

        conn.commit()
        console.print(Align.center("[green]Payment Updated[/green]"))

    except Exception as e:
        console.print(Align.center(f"[red]Error updating payment: {e}[/red]"))

    pause()


def delete_payment():
    view_payments()

    pid = safe_int("Payment ID")
    if not pid:
        return

    confirm = input("Are you sure? (y/n): ").strip().lower()
    if confirm != "y":
        console.print(Align.center("[yellow]Cancelled[/yellow]"))
        pause()
        return

    try:
        cursor.execute("DELETE FROM payments WHERE payment_id=%s", (pid,))
        conn.commit()

        console.print(Align.center("[red]Payment Deleted[/red]"))

    except Exception as e:
        console.print(Align.center(f"[red]Error deleting payment: {e}[/red]"))

    pause()

# ================= EARNINGS DASHBOARD =================
def earnings_dashboard():
    clear()
    header("SMART EARNINGS DASHBOARD")

    try:
        # ================= TOTAL EARNINGS =================
        cursor.execute("""
        SELECT COALESCE(SUM(amount_paid), 0)
        FROM payments
        WHERE payment_status = 'completed'
        """)
        total = cursor.fetchone()[0]

        console.print(Align.center(f"[green]Total Completed Earnings: ₹{total:.2f}[/green]"))

        # ================= MONTH WISE =================
        console.print(Align.center("\n[cyan]Month-wise Earnings[/cyan]\n"))

        cursor.execute("""
        SELECT 
            YEAR(payment_date) AS yr,
            MONTH(payment_date) AS mn,
            DATE_FORMAT(MIN(payment_date), '%M %Y') AS month_name,
            SUM(amount_paid) AS total_amount
        FROM payments
        WHERE payment_status = 'completed'
        GROUP BY yr, mn
        ORDER BY yr, mn
        """)

        rows = cursor.fetchall()

        if rows:
            for i, row in enumerate(rows, 1):
                console.print(
                    Align.center(f"[yellow]{i}. {row[2]} → ₹{row[3]:.2f}[/yellow]")
                )
        else:
            console.print(Align.center("[red]No completed payments[/red]"))

        # ================= YEAR WISE =================
        console.print(Align.center("\n[magenta]Year-wise Earnings[/magenta]\n"))

        cursor.execute("""
        SELECT 
            YEAR(payment_date) AS yr,
            SUM(amount_paid) AS total_amount
        FROM payments
        WHERE payment_status = 'completed'
        GROUP BY yr
        ORDER BY yr
        """)

        rows = cursor.fetchall()

        if rows:
            for i, row in enumerate(rows, 1):
                console.print(
                    Align.center(f"[green]{i}. {row[0]} → ₹{row[1]:.2f}[/green]")
                )
        else:
            console.print(Align.center("[red]No yearly data[/red]"))

        # ================= FULL DETAILS TABLE =================
        console.print(Align.center("\n[cyan]Completed Payment Details[/cyan]\n"))

        cursor.execute("""
        SELECT c.name, p.project_type, pay.amount_paid,
               COALESCE(pay.completed_date, pay.payment_date)
        FROM payments pay
        JOIN projects p ON pay.project_id = p.project_id
        JOIN clients c ON p.client_id = c.client_id
        WHERE pay.payment_status = 'completed'
        ORDER BY COALESCE(pay.completed_date, pay.payment_date) DESC
        """)

        data = cursor.fetchall()

        print_table(data, ["Client", "Project", "Amount", "Completed Date"])

    except Exception as e:
        console.print(Align.center(f"[red]Error: {e}[/red]"))

    pause()
    
# ================= PROJECT DASHBOARD =================
def project_dashboard():
    options = ["Completed Projects", "Ongoing Projects", "Back"]

    while True:
        choice = arrow_menu(options, "PROJECT STATUS DASHBOARD")

        if choice == 0:
            show_completed_projects()
        elif choice == 1:
            show_ongoing_projects()
        elif choice == 2:
            break


def show_completed_projects():
    try:
        clear()
        header("COMPLETED PROJECTS")

        cursor.execute("""
        SELECT 
            p.project_type,
            c.name,
            p.deadline,
            p.completed_date
        FROM projects p
        JOIN clients c ON p.client_id = c.client_id
        WHERE p.status = 'completed'
        ORDER BY p.completed_date DESC
        """)

        data = cursor.fetchall()

        if not data:
            console.print(Align.center("[yellow]No completed projects found[/yellow]"))
        else:
            print_table(
                data,
                ["Project", "Client", "Deadline", "Completed Date"]
            )

    except Exception as e:
        console.print(Align.center(f"[red]Error: {e}[/red]"))

    pause()


def show_ongoing_projects():
    try:
        clear()
        header("ONGOING PROJECTS")

        today = date.today()

        cursor.execute("""
        SELECT p.project_type, c.name, p.deadline, p.status
        FROM projects p
        JOIN clients c ON p.client_id = c.client_id
        WHERE p.status != 'completed'
        ORDER BY p.deadline
        """)

        rows = cursor.fetchall()
        data = []

        for ptype, name, dl, status in rows:
            # safety check (important fix)
            if dl is None:
                continue

            days = (dl - today).days

            if days < 0:
                progress = f"[red]OVERDUE ({abs(days)} days late)[/red]"
            else:
                progress = f"[cyan]{days} days left[/cyan]"

            data.append([ptype, name, dl, status, progress])

        if not data:
            console.print(Align.center("[yellow]No ongoing projects[/yellow]"))
        else:
            print_table(
                data,
                ["Project", "Client", "Deadline", "Status", "Progress"]
            )

    except Exception as e:
        console.print(Align.center(f"[red]Error: {e}[/red]"))

    pause()

# ================= ARROW MENU (OPTIMIZED + NO FLICKER) =================
def arrow_menu(options, title="EDITVAULT", subtitle=None):
    index = 0

    big_title = """
███████╗██████╗ ██╗████████╗██╗   ██╗ █████╗ ██╗   ██╗██╗  ████████╗
██╔════╝██╔══██╗██║╚══██╔══╝██║   ██║██╔══██╗██║   ██║██║  ╚══██╔══╝
█████╗  ██║  ██║██║   ██║   ██║   ██║███████║██║   ██║██║     ██║   
██╔══╝  ██║  ██║██║   ██║   ██║   ██║██╔══██║╚██╗ ██╔╝██║     ██║   
███████╗██████╔╝██║   ██║   ╚██████╔╝██║  ██║ ╚████╔╝ ███████╗██║   
╚══════╝╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝   
"""

    def render():
        # Only clear ONCE per render cycle (reduces flicker)
        os.system('cls' if os.name == 'nt' else 'clear')

        header_panel = Panel(
            Align.center(
                f"[bold cyan]{big_title}[/bold cyan]\n"
                f"[white]{title}[/white]"
            ),
            border_style="cyan",
            padding=(1, 2),
            box=box.ROUNDED
        )

        menu_lines = []

        if subtitle:
            menu_lines.append(f"[dim]{subtitle}[/dim]")
            menu_lines.append("")

        for i, option in enumerate(options):
            if i == index:
                menu_lines.append(f"[bold cyan]> {option}[/bold cyan]")
            else:
                menu_lines.append(f"   {option}")

        menu_panel = Panel(
            Align.center("\n".join(menu_lines)),
            border_style="cyan",
            padding=(1, 6),
            box=box.ROUNDED
        )

        console.print(header_panel)
        console.print()
        console.print(menu_panel)

    # first render
    render()

    while True:
        key = readchar.readkey()

        if key == readchar.key.UP:
            index = (index - 1) % len(options)
            render()

        elif key == readchar.key.DOWN:
            index = (index + 1) % len(options)
            render()

        elif key == readchar.key.ENTER:
            return index
        
# ================= MENU =================
def menu():
    options = [
        "Clients",
        "Projects",
        "Payments",
        "Earnings",
        "Project Status",
        "Exit"
    ]

    while True:
        choice = arrow_menu(options, "Main menu")

        if choice == 0:
            client_menu()

        elif choice == 1:
            project_menu()

        elif choice == 2:
            payment_menu()

        elif choice == 3:
            earnings_dashboard()

        elif choice == 4:
            project_dashboard()

        elif choice == 5:
# ================= EXIT CONFIRMATION =================
            clear()
            header("EXIT SYSTEM")

            confirm = input("\nAre you sure you want to exit? (y/n): ").strip().lower()

            if confirm in ["y", "yes"]:
                console.print(Align.center("[green]Goodbye! System Closed[/green]"))
                time.sleep(1)
                break
            else:
                continue

# ================= CLIENT MENU =================
def client_menu():
    options = ["Add", "View", "Search", "Update", "Delete", "Back"]

    while True:
        choice = arrow_menu(
            options,
            "CLIENT MENU",
            
        )

        if choice == 0:
            add_client()
        elif choice == 1:
            view_clients()
        elif choice == 2:
            search_client()
        elif choice == 3:
            update_client()
        elif choice == 4:
            delete_client()
        elif choice == 5:
            break

# ================= PROJECT MENU =================
def project_menu():
    options = ["Add", "View", "Search", "Update", "Delete", "Back"]

    while True:
        choice = arrow_menu(
            options,
            "PROJECT MENU",
            
        )

        if choice == 0:
            add_project()
        elif choice == 1:
            view_projects()
        elif choice == 2:
            search_project()
        elif choice == 3:
            update_project()
        elif choice == 4:
            delete_project()
        elif choice == 5:
            break

# ================= PAYMENT MENU =================
def payment_menu():
    options = ["Add", "View", "Search", "Update", "Delete", "Back"]

    while True:
        choice = arrow_menu(
            options,
            "PAYMENT MENU",
            
        )

        if choice == 0:
            add_payment()
        elif choice == 1:
            view_payments()
        elif choice == 2:
            search_payment()
        elif choice == 3:
            update_payment()
        elif choice == 4:
            delete_payment()
        elif choice == 5:
            break

# ================= START =================
if login():
    auto_alert_popup()
    menu()
