import json
import socket
from threading import Thread

from game_field import GameField
from server_game_engine import ServerGameEngine

connected_clients_number = 0


def player_data_exchange(conn, player_id, game_engine):
    """Thread function: exchange data with one client."""
    while True:
        try:
            player_actions_data = conn.recv(4096)
            if not player_actions_data:
                print(f"[Server] Player {player_id} disconnected")
                break

            player_actions = json.loads(player_actions_data.decode())
            game_engine.set_player_actions(player_id, player_actions)

            # Get current game state and tag with this player's id
            game_state_data = game_engine.get_game_state_data()
            game_state_data["self"] = player_id

            response = json.dumps(game_state_data).encode()
            conn.sendall(response)

        except Exception as e:
            print(f"[Server] Error with player {player_id}: {e}")
            break

    game_engine.remove_player(player_id)
    conn.close()


def connection_listener(game_engine):
    """Thread function: accept new client connections."""
    global connected_clients_number

    HOST = "0.0.0.0"
    PORT = 21001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    print(f"[Server] Listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        connected_clients_number += 1
        player_id = connected_clients_number
        print(f"[Server] Player {player_id} connected from {addr}")

        game_engine.add_player(player_id)

        client_thread = Thread(
            target=player_data_exchange,
            args=(conn, player_id, game_engine),
            daemon=True,
        )
        client_thread.start()


if __name__ == "__main__":
    # Same field and zones as game_iter_0.py
    game_field = GameField(0, 150, 500, 350)
    start_zone = (0, 150, 80, 200)
    end_zone = (420, 150, 80, 200)

    game_engine = ServerGameEngine(
        game_field,
        start_zone,
        end_zone,
        fps=60,
    )

    # Start connection listener in a background thread
    listener_thread = Thread(
        target=connection_listener,
        args=(game_engine,),
        daemon=True,
    )
    listener_thread.start()

    # Run game loop in main thread
    game_engine.run_game()
