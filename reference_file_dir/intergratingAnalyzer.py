
from threading import Thread
import threading
class intergratingAnalyzer(threading.Thread):
    # client =  MongoClient('localhost:27017', connect=False)
    # db = None
    # dt = datetime.datetime.now()

    def __init__(self, _keyId, _fid, _query, _start, _end, _total):
        threading.Thread.__init__(self)
        self.keyId        = _keyId
        self.fid          = _fid
        self.defaultScore = 0.02
        self.start        = _start
        self.end          = _end
        self.total        = _total
        self.query        = _query

    def run(self):
        print("---------------------")
        print(self.start)
        print(self.end)
        print(self.total)
        print("---------------------")
        """ #3. DB client 생성 """
