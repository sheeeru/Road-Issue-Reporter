from flask import Flask, render_template, request, redirect, url_for, session
from functions import register, login, report_issue, view_issues, get_leaderboard, mark_as_solved
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_fixed_secret_key")  # Set this in your environment variables

# Home Page (Login page)
@app.route('/')
def home():
    return render_template('login.html')

# User Login
@app.route('/login', methods=['POST'])
def user_login():
    username = request.form['username']
    password = request.form['password']

    user, error = login(username, password)
    if user:
        session['user_id'] = user[0]
        session['role'] = user[1]
        return redirect(url_for('user_dashboard' if user[1] == 'user' else 'admin_dashboard'))
    else:
        return render_template('login.html', error=error)

# User Dashboard
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('home'))
    return "User  Dashboard"  # Replace with actual rendering logic

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    return "Admin Dashboard"  # Replace with actual rendering logic

# User Registration
@app.route('/register', methods=['POST'])
def user_register():
    username = request.form['username']
    password = request.form['password']
    is_admin = request.form.get('is_admin', False)

    result = register(username, password, is_admin)
    return render_template('register.html', message=result)

# Report Issue
@app.route('/report_issue', methods=['POST'])
def report_issue_page():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    issue_type = request.form['issue_type']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    description = request.form['description']

    # Validate latitude and longitude
    try:
        latitude = float(latitude)
        longitude = float(longitude)
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return render_template('report_issue.html', error="Invalid latitude or longitude.")
    except ValueError:
        return render_template('report_issue.html', error="Latitude and longitude must be numbers.")

    report_issue(session['user_id'], issue_type, latitude, longitude, description)
    return redirect(url_for('user_dashboard'))

# View Issues
@app.route('/view_issues')
def view_issues_page():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    issues = view_issues()
    return render_template('view_issues.html', issues=issues)

# Leaderboard
@app.route('/leaderboard')
def leaderboard_page():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    leaderboard = get_leaderboard()
    return render_template('leaderboard.html', leaderboard=leaderboard)

# Mark Issue as Solved
@app.route('/mark_as_solved/<int:issue_id>')
def mark_issue_as_solved(issue_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    mark_as_solved(issue_id)
    return redirect(url_for('view_issues_page'))

# Error Handling for Template Not Found
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)