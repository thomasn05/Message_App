from ds_messenger import DirectMessenger
IP = '168.235.86.101'

p = DirectMessenger(IP, 'david', 'asdasd')

k = DirectMessenger(IP, 'kody', 'hello')

k.send('testing', 'paul')