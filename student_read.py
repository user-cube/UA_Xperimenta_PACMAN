import argparse
import asyncio
import json
import os

import websockets

from entities import PlayerAgent, RefactoredAgent
from mapa import Map


async def agent_loop(server_address="localhost:8000", agent_name="student", player_agent=None):
    if player_agent is None:
        raise ValueError("You must provide an agent class!")
        return
    async with websockets.connect("ws://{}/player".format(server_address)) as websocket:
        # Receive information about static game properties 
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)
        mapa = Map(game_properties['map'])

        # Our running agent(s)
        agent = player_agent(level=mapa, game_settings=game_properties)
        game_score = 0
        while not agent.dead:
            r = await websocket.recv()
            state = json.loads(r)  # receive game state
            game_score = state.get("score")
            curr_lives = state.get("lives", None)
            if curr_lives is None or curr_lives == 0:
                file = open("results.txt", "a")
                s_file = open("scores.txt", "a")
                if curr_lives is None:
                    print("WON | Turns:{0.step} | Score:{1}\n".format(agent, game_score))
                    file.write("WON | Turns:{0.step} | Score:{1}\n".format(agent, game_score))
                    file.close()
                    s_file.write("{}\n".format(game_score))
                    s_file.close()
                else:
                    print("LOSE | Turns:{0.step} | Score:{1}\n".format(agent, game_score))
                    file.write("LOSE | Turns:{0.step} | Score:{1}\n".format(agent, game_score))
                    file.close()
                    s_file.write("{}\n".format(game_score))
                    s_file.close()
                break

            # we update our agents state
            agent.update_state(new_state=state)
            # and get the next move
            next_move = agent.next_move()
            # send new key
            await websocket.send(json.dumps({"cmd": "key", "key": next_move}))
            print(
                "Lives remaining:{0.lives}\nTurns:{0.step}\nScore:{1}".format(agent, game_score))
            print("----------------------------------------------------------")


# We're going to use these by default
# If someone wants to execute the script through command line, we'll still
# have the ability to parse arguments

SERVER_DEFAULT = os.environ.get('SERVER', 'localhost')
PORT_DEFAULT = os.environ.get('PORT', '8000')
NAME_DEFAULT = os.environ.get('NAME', 'student')
AGENT_TYPE = 1
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="IP address of the server", default=SERVER_DEFAULT)
    parser.add_argument("--port", help="TCP port", type=int, default=PORT_DEFAULT)
    parser.add_argument("--name", help="Name of client running.", default=NAME_DEFAULT)
    parser.add_argument("--mode",
                        help="Type of agent to use. Options are: 1 - Naive, 2 - Refactored Agent",
                        type=int,
                        default=2)
    args = parser.parse_args()
    NAME = args.name
    SERVER = args.server
    PORT = args.port
    AGENT_TYPE = args.mode
else:
    SERVER, PORT, NAME = SERVER_DEFAULT, PORT_DEFAULT, NAME_DEFAULT

SERVER_ADDRESS = "{}:{}".format(SERVER, PORT)

LOOP = asyncio.get_event_loop()
try:
    AGENT = None
    if AGENT_TYPE == 1:
        AGENT = PlayerAgent
    elif AGENT_TYPE == 2:
        AGENT = RefactoredAgent
    else:
        raise NotImplementedError("Agent of type {} isn't implemented yet!".format(AGENT_TYPE))
    LOOP.run_until_complete(agent_loop(SERVER_ADDRESS, NAME, player_agent=AGENT))
finally:
    LOOP.stop()
