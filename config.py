import os
from fire import * 
_VERSION_ = "1.0.7"
_PORT_ = 9097
_PORT_CFG_ = "port.cfg"
_STATIC_DIR_ = "static/"
_ROOT_DIR_ = "/Users/jeffreybryant/jefe/"
def version():
    return _VERSION_
def port(portNum=None):
    jc = JournalConfig()
    if portNum==None:
        return jc.port
    else:
        return jc.setPort(portNum)
def default_port():
    os.remove(_PORT_CFG_)

class JournalConfig:
    def __init__(self, port=_PORT_):
        if os.path.exists(_PORT_CFG_):
            with open(_PORT_CFG_,"rt") as fop:
                portString=fop.readline()
                try:
                    P=int(portString)
                except ValueError as ve:
                    P=port
        else:
            P=port
        self.port = P
    def setPort(self, newPortStr):
        try:
            P=int(newPortStr)
        except ValueError as ve:
            #print(ve.value)
            P=_PORT_
        with open(_PORT_CFG_,"wt") as fop:
            fop.write(str(newPortStr))
        return P

if __name__=="__main__":
    Fire()
