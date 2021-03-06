import client
import client_player
import sys

if __name__ == '__main__':
    def make_player():
        if len(sys.argv) == 2:
            if sys.argv[1] == "human":
                print('starting human client')
                return client_player.HumanPlayer()
            elif sys.argv[1] == "bot":
                print('starting bot client')
                return client_player.BotPlayer()
            elif sys.argv[1] == "ticking":
                print('starting ticking client')
                return client_player.TickingPlayer()
        raise RuntimeError(
            "Please run with 1 arg from {'bot', 'human', 'ticking'}")

    client_0 = client.Client(make_player())
    client_0.main_loop()
