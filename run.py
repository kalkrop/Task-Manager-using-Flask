from todo_project import app

if __name__ == '__main__':
    app.config['TESTING'] = False  # Ensure testing mode is disabled in production
    app.run(host='0.0.0.0', port=5000, debug=True)
