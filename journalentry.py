from timestamp import TimeStamp

class JournalEntry:
    def __init__(self, entry, time=None):
        self.entry = self.encrypt(entry)
        if time:
            self.title=time
        else:
            self.title = TimeStamp().timestamp()

    def keytoindex(self,k,decrypt=False):
        qey = ord(k) - ord('A')
        if decrypt:
            qey = -1 * qey
        return qey

    def encrypt(self, w):
        if w[0:2] == '[[':
            key = self.keytoindex(w[2])
            txt = w[3:]
            valence = self.encrypt_str(txt, key)
        elif w[0:2] == ']]':
            key = w[2]
            txt = w[3:]
            valence = self.Decode(txt, key)
        elif w[0:2] == '{{':
            key = w[2:w.find("}}")]
            plaintext = w[w.find("}}")+2:]
            valence = self.encryptWithKey(key, plaintext)
        elif w[0:2] == '_{':
            key = w[2:w.find("}}")]
            plaintext = w[w.find("}}")+2:]
            valence = self.encryptWithKey(key, plaintext, decode=True)
        else:
            valence = w
        return valence

    def encrypt_char(self, string, key):
        if key is not None:
            if string.isalpha():
                if string.islower():
                    q = ord('a')
                else:
                    q = ord('A')
                x = ord(string) - q
                y = (x + key) % 26
                c = chr(q + y)
                return str(c)
            else:
                return string
        else:
            return string

    def encrypt_str(self, string, key):
        a = ""
        if type(key) is int:
            for letter in string:
                enc = self.encrypt_char(letter, key)
                a += enc
        return a

    def Decode(self, string, key):
        a = ""
        dekey = (ord(key) - ord('A')) * -1
        return self.encrypt_str(string, dekey)

    def nextKeyChar(self, keystr, keystrnx):
        nxkeystrnx = (keystrnx + 1) % len(keystr)
        nxkc = keystr[keystrnx]
        return (nxkc, nxkeystrnx)

    def encryptWithKey(self, keystr, plaintext, decode=False):
        a = ""
        c = 0
        for letter in plaintext:
            (key, c) = self.nextKeyChar(keystr, c)
            enc = self.encrypt_char(letter,self.keytoindex(key,decrypt=decode))
            a += enc
        return a
