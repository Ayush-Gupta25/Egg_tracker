from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# In-memory storage
entries = []

def get_today():
    return datetime.now().strftime('%Y-%m-%d')

def get_current_month():
    return datetime.now().strftime('%Y-%m')

def get_monthly_total():
    current_month = get_current_month()
    return sum(e['count'] for e in entries if e['date'].startswith(current_month))

# -------------------------
# INDEX PAGE - Log Eggs
# -------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    today = get_today()
    eggs_today = next((e['count'] for e in entries if e['date'] == today), 0)

    if request.method == 'POST':
        count = int(request.form['count'])
        existing = next((e for e in entries if e['date'] == today), None)
        if existing:
            existing['count'] = count
        else:
            entries.append({'date': today, 'count': count})
        return redirect(url_for('index'))

    total_eggs = get_monthly_total()
    return render_template('index.html', today=today, eggs_today=eggs_today, total_eggs=total_eggs)

# -------------------------
# REPORT PAGE - Monthly Summary
# -------------------------
@app.route('/report')
def report():
    current_month = get_current_month()
    monthly_entries = [e for e in entries if e['date'].startswith(current_month)]
    monthly_entries.sort(key=lambda x: x['date'])
    return render_template('report.html', month=current_month, entries=monthly_entries)

# -------------------------
# MANAGE PAGE - Edit / Delete / Add
# -------------------------
@app.route('/manage', methods=['GET', 'POST'])
def manage():
    global entries

    if request.method == 'POST':
        # Add new entry
        if 'add' in request.form:
            new_date = request.form.get('new_date')
            new_count = int(request.form.get('new_count', 0))
            if new_date and not any(e['date'] == new_date for e in entries):
                entries.append({'date': new_date, 'count': new_count})

        # Update entry
        elif 'update' in request.form:
            update_date = request.form.get('update')
            count = int(request.form.get(f'count_{update_date}', 0))
            for entry in entries:
                if entry['date'] == update_date:
                    entry['count'] = count
                    break

        # Delete entry
        elif 'delete' in request.form:
            delete_date = request.form.get('delete')
            entries = [e for e in entries if e['date'] != delete_date]

        return redirect(url_for('manage'))

    sorted_entries = sorted(entries, key=lambda x: x['date'], reverse=True)
    return render_template('manage.html', entries=sorted_entries)

if __name__ == '__main__':
    app.run(debug=True)
