from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# In-memory storage: list of dicts {id, title, done, x, y}
todos = []
next_id = 1


@app.route("/")
def index():
    return render_template("index.html", todos=todos)


@socketio.on("add_todo")
def handle_add(data):
    global next_id
    title = data.get("title", "").strip()
    if not title:
        return
    todo = {
        "id": next_id,
        "title": title,
        "done": False,
        "x": 30 + (next_id * 20) % 400,
        "y": 80 + (next_id * 15) % 300,
    }
    todos.append(todo)
    next_id += 1
    emit("todo_added", todo, broadcast=True)


@socketio.on("edit_todo")
def handle_edit(data):
    todo_id = data.get("id")
    title = data.get("title", "").strip()
    todo = next((t for t in todos if t["id"] == todo_id), None)
    if todo and title:
        todo["title"] = title
        emit("todo_updated", todo, broadcast=True)


@socketio.on("delete_todo")
def handle_delete(data):
    global todos
    todo_id = data.get("id")
    todos = [t for t in todos if t["id"] != todo_id]
    emit("todo_deleted", {"id": todo_id}, broadcast=True)


@socketio.on("toggle_todo")
def handle_toggle(data):
    todo_id = data.get("id")
    todo = next((t for t in todos if t["id"] == todo_id), None)
    if todo:
        todo["done"] = not todo["done"]
        emit("todo_updated", todo, broadcast=True)


@socketio.on("move_todo")
def handle_move(data):
    todo_id = data.get("id")
    todo = next((t for t in todos if t["id"] == todo_id), None)
    if todo:
        todo["x"] = data.get("x", todo["x"])
        todo["y"] = data.get("y", todo["y"])
        emit("todo_moved", {"id": todo_id, "x": todo["x"], "y": todo["y"]}, broadcast=True, include_self=False)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
