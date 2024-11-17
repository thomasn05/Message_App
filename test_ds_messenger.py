import unittest as u
from ds_messenger import DirectMessenger

IP = '168.235.86.101'

user = DirectMessenger(IP, 'daivd', 'asdasd')

class test_ds_messenger(u.TestCase):

    def test_send(self):
        response = user.send('testcase testing','timmothy')
        self.assertEqual(response, True)

    def test_retrieve_all(self):
        msgs = user.retrieve_all()
        self.assertEqual(type(msgs), list)

    def test_retrieve_new(self):
        msgs = user.retrieve_new()
        self.assertEqual(type(msgs), list)

if __name__ == '__main__':
    u.main()