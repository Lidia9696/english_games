from flask import Flask, render_template, request
from flask_socketio import SocketIO
import os
from shared.database import init_db, save_room_to_db, load_rooms_from_db
from shared.utils import generate_room_code

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'

socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}

# Register Game 1 - Describe & Guess
from games.game_1_describe_and_guess.routes import register_routes
register_routes(app)

from games.game_1_describe_and_guess.socket_handlers import register_handlers
register_handlers(socketio, rooms, save_room_to_db, generate_room_code)

# -------------------- ROUTES --------------------

@app.route('/')
def index():
    """Home page with game selection"""
    return render_template('index.html')

# ---------- Spy in Ithaca ----------
@app.route('/spy-in-ithaca/rules')
def game2_rules():
    return render_template('spy_in_ithaca/rules.html')

@app.route('/spy-in-ithaca/game')
def spy_in_ithaca_game():
    return render_template('spy_in_ithaca/game.html')

@app.route('/spy-in-ithaca/<room_code>')
def spy_in_ithaca_room(room_code):
    return render_template('spy_in_ithaca/game.html')

# -------------------- RUN SERVER --------------------

if __name__ == '__main__':
    # Use environment variable to control debug mode: True locally, False in production
    init_db()
    rooms.update(load_rooms_from_db())
    debug_mode = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=5000)

