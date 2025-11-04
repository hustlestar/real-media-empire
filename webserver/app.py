import os
import sqlite3
import subprocess
import threading
from flask import Flask, request, jsonify, redirect, url_for
from flask_swagger_ui import get_swaggerui_blueprint
from subprocess import TimeoutExpired

from _config import prepare_swagger_json

MEDIA_EMPIRE_SRC = "G:\\OLD_DISK_D_LOL\\Projects\\media-empire\\src"

app = Flask(__name__)
db_name = "commands_status.db"

# Swagger UI setup
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "Lightweight Webserver API"
    }
)
app.register_blueprint(swaggerui_blueprint)

prepare_swagger_json()


def init_db():
    if not os.path.exists(db_name):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE commands (
                id INTEGER PRIMARY KEY,
                command TEXT,
                status TEXT,
                stdout TEXT,
                stderr TEXT
            )"""
        )
        conn.commit()
        conn.close()


def call_api_and_check_status(task_id):
    # Replace with your REST API URL
    api_url = 'https://your-api-url.com/some/endpoint'

    while True:
        response = requests.get(api_url)
        status = response.json().get('status')

        if status in ('success', 'failed', 'error'):
            print(f"Task {task_id}: API call status: {status}")
            return status
        elif status == 'running':
            sleep(60)  # Wait 1 minute before checking again
        else:
            raise ValueError(f"Unexpected status: {status}")


@app.errorhandler(404)
def not_found(e):
    print(f"Route is not found redirecting to swagger {e}")
    return redirect(url_for('swagger_ui.show'))


@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    task_id = data.get('task_id')
    interval = data.get('interval')

    if not task_id or not interval:
        return jsonify({"error": "Task ID and interval are required"}), 400

    scheduler.add_job(id=task_id, func=call_api_and_check_status, args=(task_id,), trigger='interval', seconds=interval)
    return jsonify({"success": True, "task_id": task_id, "interval": interval})


@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        scheduler.remove_job(task_id)
        return jsonify({"success": True, "task_id": task_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/tasks', methods=['GET'])
def list_tasks():
    jobs = scheduler.get_jobs()
    tasks = [{'task_id': job.id, 'interval': job.trigger.interval.total_seconds()} for job in jobs]
    return jsonify(tasks)


@app.route("/commands", methods=["POST"])
def command():
    data = request.get_json()
    command = data.get("command")
    cwd = data.get("cwd")
    timeout = data.get("timeout")
    print(f"Received cwd: {cwd} \ntimeout : {timeout} \ncommand:\n{command}")
    if command:
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO commands (command, status) VALUES (?, ?)", (command, "running"))
            conn.commit()
            command_id = cursor.lastrowid
            conn.close()

            command_thread = threading.Thread(target=run_command_in_background, args=(command_id, command), kwargs={'cwd': cwd, 'timeout': timeout})
            command_thread.start()

            return jsonify({"request_status": "success", "command_id": command_id})

        except Exception as e:
            return jsonify({"request_status": "error", "message": str(e)})
    else:
        return jsonify({"request_status": "error", "message": "Command not provided"})


def run_command_in_background(command_id, command, timeout=None, cwd=None):
    process = None
    try:
        cwd = MEDIA_EMPIRE_SRC if not cwd else cwd
        print(f"Will run command:\n{command}\nin directory:\n{cwd}")
        process = subprocess.Popen(command,
                                   shell=True,
                                   cwd=cwd,
                                   text=True,
                                   encoding='utf-8',
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        stdout, stderr = process.communicate(timeout=timeout)

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        if process.returncode == 0:
            print(f"Command {command_id} finished successfully")
            cursor.execute("UPDATE commands SET status=?, stdout=?, stderr=? WHERE id=?", ("success", stdout, stderr, command_id))
        else:
            print(f"Command {command_id} finished with error:\n{stdout}\n{stderr}")
            cursor.execute("UPDATE commands SET status=?, stdout=?, stderr=? WHERE id=?", ("failed", stdout, stderr, command_id))
        conn.commit()
        conn.close()
    except TimeoutExpired as x:
        print(f"Command {command_id} timeout: {x}")
        if process:
            process.kill()
            stdout, stderr = process.communicate()
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE commands SET status=?, stdout=?, stderr=? WHERE id=?", ("timeout", stdout, stderr, command_id))
            conn.commit()
            conn.close()


@app.route("/commands/<int:command_id>", methods=["GET"])
def command_status(command_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT status, command, stdout, stderr FROM commands WHERE id=?", (command_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        status, cmd, stdout, stderr = result
        return jsonify({"request_status": "success", "command": cmd, "command_status": status, "stdout": stdout, "stderr": stderr})
    else:
        return jsonify({"request_status": "error", "message": f"Command {command_id} not found"})


@app.route("/commands", methods=["GET"])
def list_commands():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, command, status, stdout, stderr FROM commands ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
    results = cursor.fetchall()
    conn.close()

    commands = []
    for result in results:
        command_id, command, status, stdout, stderr = result
        commands.append({
            "command_id": command_id,
            "command": command,
            "command_status": status,
            "stdout": stdout,
            "stderr": stderr
        })

    return jsonify(commands)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10101)
