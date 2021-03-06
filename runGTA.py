from multiprocessing import Process
import subprocess
import time
import das_game_settings

TIME_REDUCE = 100000000
LIFETIME_REDUCE = 10
TIME_CONSTANT = 0.1 #add this st time.sleep() is not there for nothing
ID = 0 # change this for each node 0,1,2,3,4

class GTAClient():

    def __init__(self,id,timestamp,lifetime):
        self.id = id
        self.timestamp = timestamp
        self.lifetime = lifetime

    def __repr__(self):
        return repr((self.id, self.timestamp, self.lifetime))


def parseLine(line):
    line = line.strip().split(',')
    if len(line) == 6:
        id = int(line[0])
        timestamp = float(line[1])
        lifetime = float(line[2])
    return GTAClient(id,timestamp,lifetime)

processes = []

def new_command(args, index):
    print('START', index)
    subprocess.check_output(args)
    print('END', index)

def new_process(args, t=0):
    assert isinstance(args, list)
    index = len(processes)
    time.sleep(t+TIME_CONSTANT)
    p = Process(target=new_command, args=(args,index))
    p.start()
    processes.append(p)
    return p

def join_all(kill=False):
    if kill:
        for p in processes:
            p.terminate()
    for p in processes:
        p.join()
    print('killed')


def server_start_args(server_id, starter=False):
    assert 0 <= server_id <= das_game_settings.num_server_addresses
    assert isinstance(server_id, int)
    assert isinstance(starter, bool)
    return ['python', './server_start.py', str(server_id), str(starter)]


def client_start_args(player_type_arg='bot'):
    assert player_type_arg in {'bot', 'ticker', 'human'}
    return ['python', './client_start.py', player_type_arg]

def check_timeout(data, kill=False):
    while True:
        for proc,startTime,lifeTime in data:
            if time.time() - startTime >= lifeTime:
                proc.terminate()
                print('Client disconnect')
                data = filter(lambda x: x[0] != proc, data)
            if not data:
                for p in processes:
                    p.terminate()
                print('No more clients, done!')
		return
            if kill:
                for p in processes:
                    p.terminate()
                print('Killed integrated from join_all')
                break
        time.sleep(5)


if __name__ == '__main__':
    # we start servers ourselves.
    #new_process(server_start_args(0, starter=True))
    #new_process(server_start_args(1))
    #new_process(server_start_args(2))
    #new_process(server_start_args(3))
    #new_process(server_start_args(4))

    file = open('WoT_Edge_Detailed','r') #alternative SC2
    #file = open('SC2_Edge_Detailed','r')
    lines = file.readlines()
    clientList = []
    c=6 #skip first lines as there is no data
    while(c<1006): # 0-99
        clientGTA = parseLine(lines[c])
        if (clientGTA.id % 5 == ID):
            clientList.append(clientGTA)
        c += 1

    clientList = sorted(clientList, key = lambda client: client.timestamp)
    timestampCounter = clientList[0].timestamp #1354482240.312 WoT;1305559358.0 SC
    clientProcesses = []
    clientTimeAlive = []
    clientStartTime = []
    for sortedClient in clientList:
        clProcess = new_process(client_start_args(), (sortedClient.timestamp - timestampCounter)/TIME_REDUCE)
        clientStartTime.append(time.time())
        timestampCounter = sortedClient.timestamp
        clientProcesses.append(clProcess)
        clientTimeAlive.append(sortedClient.lifetime/LIFETIME_REDUCE)
    checkTimeoutData = zip(clientProcesses, clientStartTime, clientTimeAlive)
    check_timeout(checkTimeoutData)
