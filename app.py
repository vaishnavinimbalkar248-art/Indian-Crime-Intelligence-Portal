import os
import sqlite3
import io
import base64
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'crime_analytics_secret_key_2026'

DB_PATH = os.path.join('database', 'crime.db')
CSV_PATH = 'indian_crime_data_2021_2026_with_names.csv'
if not os.path.exists(CSV_PATH) and os.path.exists(os.path.join('data', CSV_PATH)):
    CSV_PATH = os.path.join('data', CSV_PATH)

sns.set_theme(style="whitegrid")

def generate_matplotlib_chart(plot_func):
    """Encodes Matplotlib plots directly to base64 string for HTML img rendering."""
    img = io.BytesIO()
    plt.figure(figsize=(6, 4))
    plot_func()
    plt.tight_layout()
    plt.savefig(img, format='png', dpi=110)
    plt.close()
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf-8')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs('database', exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crime_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT UNIQUE,
            name TEXT,
            age INTEGER,
            gender TEXT,
            state TEXT,
            city TEXT,
            crime_type TEXT,
            location TEXT,
            arrest TEXT,
            arrest_made INTEGER,
            date TEXT,
            year INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS officers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            badge_id TEXT UNIQUE,
            name TEXT,
            password_hash TEXT,
            role TEXT
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM officers")
    if cursor.fetchone()[0] == 0:
        default_hash = generate_password_hash('Officer@123')
        cursor.execute("INSERT INTO officers (badge_id, name, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('OFF-1001', 'Senior Inspector Sharma', default_hash, 'Admin'))
    
    cursor.execute("SELECT COUNT(*) FROM crime_records")
    if cursor.fetchone()[0] == 0 and os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df.columns = [c.lower() for c in df.columns]
        
        # Parse date and extract year
        df['parsed_date'] = pd.to_datetime(df['date'], format='%d-%m-%Y %H:%M', errors='coerce')
        df['year'] = df['parsed_date'].dt.year.fillna(2023).astype(int)
        df['arrest_made'] = df['arrest'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)
        
        for idx, row in df.iterrows():
            inc_id = f"INC-{2021+idx:05d}"
            cursor.execute("""
                INSERT OR IGNORE INTO crime_records 
                (incident_id, name, age, gender, state, city, crime_type, location, arrest, arrest_made, date, year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                inc_id, str(row.get('name', 'N/A')), int(row.get('age', 0)),
                str(row.get('gender', 'Other')), str(row.get('state', 'Unknown')),
                str(row.get('city', 'Unknown')), str(row.get('crime_type', 'General')),
                str(row.get('location', 'Public')), str(row.get('arrest', 'No')),
                int(row.get('arrest_made', 0)), str(row.get('date', '')), int(row.get('year', 2023))
            ))
            
    conn.commit()
    conn.close()

def get_filtered_df(state=None, crime_type=None, year=None, arrest=None):
    conn = get_db_connection()
    query = "SELECT * FROM crime_records WHERE 1=1"
    params = []
    
    if state and state != 'All':
        query += " AND state = ?"
        params.append(state)
    if crime_type and crime_type != 'All':
        query += " AND crime_type = ?"
        params.append(crime_type)
    if year and year != 'All':
        query += " AND year = ?"
        params.append(int(year))
    if arrest and arrest != 'All':
        query += " AND arrest = ?"
        params.append(arrest)
        
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

init_db()

@app.route('/')
def dashboard():
    df = get_filtered_df()
    total_crimes = len(df)
    top_crime_type = df['crime_type'].mode()[0] if not df.empty else 'N/A'
    arrest_rate = round((df['arrest_made'].sum() / total_crimes * 100), 1) if total_crimes > 0 else 0
    active_states = df['state'].nunique() if not df.empty else 0
    
    def chart_type():
        counts = df['crime_type'].value_counts()
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=sns.color_palette("Set2"))
        plt.title("Crimes by Type")

    def chart_state():
        counts = df['state'].value_counts()
        sns.barplot(x=counts.values, y=counts.index, palette="viridis")
        plt.title("Incidents by State")
        plt.xlabel("Count")

    def chart_year():
        counts = df['year'].value_counts().sort_index()
        plt.plot(counts.index.astype(str), counts.values, marker='o', color='crimson', linewidth=2)
        plt.title("Yearly Trend (2021-2026)")
        plt.ylabel("Incidents")

    plot_type_url = generate_matplotlib_chart(chart_type) if not df.empty else None
    plot_state_url = generate_matplotlib_chart(chart_state) if not df.empty else None
    plot_year_url = generate_matplotlib_chart(chart_year) if not df.empty else None

    return render_template('index.html',
                           total_crimes=total_crimes,
                           top_crime_type=top_crime_type,
                           arrest_rate=arrest_rate,
                           active_states=active_states,
                           plot_type_url=plot_type_url,
                           plot_state_url=plot_state_url,
                           plot_year_url=plot_year_url)

@app.route('/crime-records')
def crime_records():
    df = get_filtered_df()
    records = df.to_dict(orient='records')
    return render_template('crime_records.html', records=records)

@app.route('/search')
def search():
    state = request.args.get('state', 'All')
    crime_type = request.args.get('crime_type', 'All')
    year = request.args.get('year', 'All')
    arrest = request.args.get('arrest', 'All')
    
    df = get_filtered_df(state, crime_type, year, arrest)
    records = df.to_dict(orient='records')
    
    conn = get_db_connection()
    states = [r[0] for r in conn.execute("SELECT DISTINCT state FROM crime_records ORDER BY state").fetchall()]
    crime_types = [r[0] for r in conn.execute("SELECT DISTINCT crime_type FROM crime_records ORDER BY crime_type").fetchall()]
    years = [str(r[0]) for r in conn.execute("SELECT DISTINCT year FROM crime_records ORDER BY year DESC").fetchall()]
    conn.close()
    
    return render_template('search.html', records=records, states=states, crime_types=crime_types,
                           years=years, sel_state=state, sel_crime=crime_type,
                           sel_year=year, sel_arrest=arrest)

@app.route('/analytics')
def analytics():
    df = get_filtered_df()

    def chart_type():
        counts = df['crime_type'].value_counts()
        sns.barplot(x=counts.index, y=counts.values, palette="mako")
        plt.title("Distribution by Crime Type")
        plt.xticks(rotation=30)

    def chart_arrest():
        counts = df['arrest'].value_counts()
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'])
        plt.title("Arrest Status (Yes vs No)")

    def chart_gender():
        counts = df['gender'].value_counts()
        sns.barplot(x=counts.index, y=counts.values, palette="Set1")
        plt.title("Gender Demographics")

    plot_type = generate_matplotlib_chart(chart_type) if not df.empty else None
    plot_arrest = generate_matplotlib_chart(chart_arrest) if not df.empty else None
    plot_gender = generate_matplotlib_chart(chart_gender) if not df.empty else None

    return render_template('analytics.html', plot_type=plot_type, plot_arrest=plot_arrest, plot_gender=plot_gender)

@app.route('/state-analysis')
def state_analysis():
    df = get_filtered_df()
    if not df.empty:
        state_summary = df.groupby('state').agg(
            Total_Incidents=('id', 'count'),
            Arrests=('arrest_made', 'sum'),
            Top_Crime=('crime_type', lambda x: x.mode()[0] if not x.empty else 'N/A')
        ).reset_index().to_dict(orient='records')
    else:
        state_summary = []
    return render_template('state_analysis.html', state_summary=state_summary)

@app.route('/trends')
def trends():
    df = get_filtered_df()

    def chart_trend():
        counts = df['year'].value_counts().sort_index()
        sns.lineplot(x=counts.index.astype(str), y=counts.values, marker="s", color="darkblue", linewidth=2.5)
        plt.title("Yearly Incident Trend (2021 - 2026)")
        plt.xlabel("Year")
        plt.ylabel("Number of Cases")

    plot_trend = generate_matplotlib_chart(chart_trend) if not df.empty else None
    return render_template('trends.html', plot_trend=plot_trend)

@app.route('/reports')
def reports():
    state = request.args.get('state', 'All')
    crime_type = request.args.get('crime_type', 'All')
    year = request.args.get('year', 'All')
    arrest = request.args.get('arrest', 'All')
    
    df = get_filtered_df(state, crime_type, year, arrest)
    
    summary = {
        'total_records': len(df),
        'arrests_made': int(df['arrest_made'].sum()) if not df.empty else 0,
        'unique_states': df['state'].nunique() if not df.empty else 0,
        'unique_crime_types': df['crime_type'].nunique() if not df.empty else 0
    }
    
    conn = get_db_connection()
    states = [r[0] for r in conn.execute("SELECT DISTINCT state FROM crime_records ORDER BY state").fetchall()]
    crime_types = [r[0] for r in conn.execute("SELECT DISTINCT crime_type FROM crime_records ORDER BY crime_type").fetchall()]
    years = [str(r[0]) for r in conn.execute("SELECT DISTINCT year FROM crime_records ORDER BY year DESC").fetchall()]
    conn.close()
    
    return render_template('reports.html', summary=summary, records=df.to_dict(orient='records'),
                           states=states, crime_types=crime_types, years=years,
                           sel_state=state, sel_crime=crime_type, sel_year=year, sel_arrest=arrest)

@app.route('/export-csv')
def export_csv():
    state = request.args.get('state', 'All')
    crime_type = request.args.get('crime_type', 'All')
    year = request.args.get('year', 'All')
    arrest = request.args.get('arrest', 'All')
    
    df = get_filtered_df(state, crime_type, year, arrest)
    csv_data = df.to_csv(index=False)
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=filtered_crime_report.csv"}
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/officer-login', methods=['GET', 'POST'])
def officer_login():
    if request.method == 'POST':
        badge_id = request.form.get('badge_id')
        password = request.form.get('password')
        
        conn = get_db_connection()
        officer = conn.execute("SELECT * FROM officers WHERE badge_id = ?", (badge_id,)).fetchone()
        conn.close()
        
        if officer and check_password_hash(officer['password_hash'], password):
            session['officer_logged_in'] = True
            session['officer_name'] = officer['name']
            session['badge_id'] = officer['badge_id']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('officer_dashboard'))
        else:
            flash('Invalid Badge ID or Password.', 'danger')
            
    return render_template('officer_login.html')

@app.route('/officer-dashboard')
def officer_dashboard():
    if not session.get('officer_logged_in'):
        flash('Unauthorized access. Please login first.', 'warning')
        return redirect(url_for('officer_login'))
    return render_template('officer_dashboard.html')

@app.route('/add-crime-record', methods=['POST'])
def add_crime_record():
    if not session.get('officer_logged_in'):
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('officer_login'))
        
    incident_id = request.form.get('incident_id')
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    state = request.form.get('state')
    city = request.form.get('city')
    crime_type = request.form.get('crime_type')
    location = request.form.get('location')
    arrest = request.form.get('arrest')
    date = request.form.get('date')
    
    arrest_made = 1 if arrest.lower() == 'yes' else 0
    try:
        parsed_dt = pd.to_datetime(date)
        year = parsed_dt.year
    except Exception:
        year = 2023
    
    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO crime_records 
            (incident_id, name, age, gender, state, city, crime_type, location, arrest, arrest_made, date, year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (incident_id, name, int(age), gender, state, city, crime_type, location, arrest, arrest_made, date, int(year)))
        conn.commit()
        flash(f'Record {incident_id} registered successfully.', 'success')
    except sqlite3.IntegrityError:
        flash(f'Error: Incident ID {incident_id} already exists.', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('officer_dashboard'))

@app.route('/officer-logout')
def officer_logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('dashboard'))

@app.route("/gps")
def gps():
    return render_template("gps.html")

if __name__ == '__main__':
    app.run(debug=True, port=5000)