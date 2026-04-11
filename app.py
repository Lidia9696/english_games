# app.py - Main Flask application for English Games

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import string

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'

# Enable WebSockets with CORS (allows connections from any origin)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store all active game rooms
# Structure: { room_code: { 'players': {'name': score}, 'game_started': False } }
rooms = {}


def generate_room_code():
    """Generate random 4-character room code (letters + digits)"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=4))


# -------------------- ROUTES (Page URLs) --------------------

@app.route('/')
def index():
    """Home page with game selection"""
    return render_template('index.html')


@app.route('/game1/rules')
def game1_rules():
    """Rules page for Describe & Guess game"""
    return render_template('game_1_describe_and_guess/rules.html')

@app.route('/game1/game')
def game1_game():
    return render_template('game_1_describe_and_guess/game.html')

# -------------------- WEBSOCKET EVENTS --------------------

@socketio.on('create_room')
def handle_create_room(data):
    """
    Create a new game room.
    Expects: { 'name': player_name }
    """
    player_name = data.get('name')
    room_code = generate_room_code()

    # Create room with one player (score 0)
    rooms[room_code] = {
        'players': {player_name: 0},
        'game_started': False
    }

    # Add player to SocketIO room
    join_room(room_code)

    # Notify the creator
    emit('room_created', {
        'room_code': room_code,
        'players': list(rooms[room_code]['players'].keys())
    }, to=room_code)


@socketio.on('join_room')
def handle_join_room(data):
    """
    Join existing game room.
    Expects: { 'name': player_name, 'room_code': room_code }
    """
    player_name = data.get('name')
    room_code = data.get('room_code')

    # Check if room exists
    if room_code not in rooms:
        emit('error', {'message': 'Room not found'})
        return

    # Add player with score 0
    rooms[room_code]['players'][player_name] = 0
    join_room(room_code)

    # Notify everyone in the room
    emit('player_joined', {
        'players': list(rooms[room_code]['players'].keys())
    }, to=room_code)


@socketio.on('start_game')
def handle_start_game(data):
    """
    Start the game (only host can do this).
    Expects: { 'room_code': room_code }
    """
    room_code = data.get('room_code')

    if room_code in rooms:
        rooms[room_code]['game_started'] = True
        emit('game_started', to=room_code)


@socketio.on('disconnect')
def handle_disconnect():
    """Clean up when a player leaves (optional, can be extended)"""
    print('Client disconnected')


# Check if a room exists before the player tries to join
@socketio.on('check_room')
def handle_check_room(data):
    """
    Verify room existence and send appropriate response.
    Expected input: { 'room_code': 'AB12' }
    """
    room_code = data.get('room_code')

    # If room doesn't exist, notify the player
    if room_code not in rooms:
        emit('error', {'message': 'Room not found'})
    else:
        # Room exists — confirm it so the player can proceed
        emit('room_exists', {'exists': True})


# -------------------- RUN SERVER --------------------

if __name__ == '__main__':
    # debug=True auto-restarts when code changes
    socketio.run(app, debug=True)