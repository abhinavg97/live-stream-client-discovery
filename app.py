from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

peers = {}  # Dictionary to track connected peers

@app.route('/')
def index():
    return "WebSocket signaling and peer discovery server is running."

@socketio.on('join')
def on_join(data):
    """
    Handle a new peer joining.
    """
    peer_id = data['peerId']
    peers[peer_id] = request.sid  # Store the peer's session ID
    print(f"Peer joined: {peer_id}")
    # Notify all peers about the updated list of connected peers
    emit('peer_list', list(peers.keys()), broadcast=True)

@socketio.on('leave')
def on_leave(data):
    """
    Handle a peer leaving.
    """
    peer_id = data['peerId']
    if peer_id in peers:
        del peers[peer_id]
        print(f"Peer left: {peer_id}")
        # Notify all peers about the updated list of connected peers
        emit('peer_list', list(peers.keys()), broadcast=True)

@socketio.on('signal')
def on_signal(data):
    """
    Relay WebRTC signaling messages.
    """
    source_peer_id = data['sourcePeerId']
    target_peer_id = data['targetPeerId']

    if target_peer_id in peers:
        print(f"Relaying signal from {source_peer_id} to {target_peer_id}: {data['type']}")
        emit('signal', data, room=peers[target_peer_id])  # Send signal to the target peer
    else:
        print(f"Target peer {target_peer_id} not found")

@socketio.on('disconnect')
def on_disconnect():
    for peer_id, sid in list(peers.items()):
        if sid == request.sid:
            del peers[peer_id]
            print(f"Peer disconnected: {peer_id}")
            emit('peer_list', list(peers.keys()), broadcast=True)
            break


if __name__ == "__main__":
    # Run the server on port 9030
    socketio.run(app, host="0.0.0.0", port=9030)
