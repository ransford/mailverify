from twisted.internet import reactor, protocol
from twisted.protocols import basic
import click
import re

class VerifyClient(basic.LineReceiver):
    CONNECTING = 1
    SENDING_EHLO = 2
    SENDING_MAIL = 3
    SENDING_RCPT = 4
    SENDING_RSET = 5
    SENDING_QUIT = 6

    def __init__(self, factory):
        self.state = self.CONNECTING
        self.email = factory.address
        self.ehlo = factory.ehlo
        self.fromaddr = factory.fromaddr

    def connectionMade(self):
        print "connected!"

    def bail(self, msg):
        print "Error: {}".format(msg)
        self.transport.loseConnection()
        reactor.callFromThread(reactor.stop)

    def lineReceived(self, line):
        print "< {:s}".format(line)
        status = None
        message = None
        expect_more = False
        try:
            status, continuing, message = \
                re.match(r'(\d+)([ -])(.*)', line).groups()
            status = int(status)
            if continuing == '-':
                expect_more = True
        except Exception as e:
            self.bail(str(e))

        #print "status: {}; message: {}; expecting more? ".format(status,
        #        message, expect_more)
        if expect_more:
            return

        if self.state == self.CONNECTING:
            if status == 220:
                self.state = self.SENDING_EHLO
                self.send("EHLO {:s}".format(self.ehlo))
            else:
                self.bail("Got {:d} when connecting".format(status))

        elif self.state == self.SENDING_EHLO:
            if status == 250:
                self.state = self.SENDING_MAIL
                self.send("MAIL FROM:<{:s}>".format(self.fromaddr))
            else:
                self.bail("Got {:d} when sending EHLO".format(status))

        elif self.state == self.SENDING_MAIL:
            if status == 250:
                self.state = self.SENDING_RCPT
                self.send("RCPT TO:<{:s}>".format(self.email))
            else:
                self.bail("Got {:d} when sending MAIL".format(status))

        elif self.state == self.SENDING_RCPT:
            if status == 250:
                print "ADDRESS WAS VALID!"
                self.state = self.SENDING_RSET
                self.send("RSET")
            elif status > 500:
                print "ADDRESS WAS INVALID!"
                self.state = self.SENDING_RSET
                self.send("RSET")
            else:
                self.bail("Got {:d} when sending RCPT".format(status))

        elif self.state == self.SENDING_RSET:
            if status == 250:
                self.state = self.SENDING_QUIT
                self.send("QUIT")
            else:
                self.bail("Got {:d} when sending RSET".format(status))

        elif self.state == self.SENDING_QUIT:
            if status == 221:
                self.bail("Disconnecting cleanly".format(status))

    def send(self, msg):
        print "> {:s}".format(msg)
        self.transport.write(msg + '\n')

def default_ehlo():
    # TODO get local hostname
    return 'foo.com'

def default_fromaddr():
    e = default_ehlo()
    return '{}@{}'.format(e, e)

class VerifyFactory(protocol.ClientFactory):
    def __init__(self, address, ehlo=None, fromaddr=None):
        self.address = address
        self.ehlo = ehlo and ehlo or default_ehlo()
        self.fromaddr = fromaddr and fromaddr or default_fromaddr()
    def buildProtocol(self, addr):
        return VerifyClient(self)

@click.command()
@click.argument('host', type=str)
@click.argument('address', type=str)
# TODO look up MX host
#@click.option('-h', '--host', help='Connect to HOST instead of MX',
#              metavar='HOST')
@click.option('-p', '--port', help='Connect to port (default 25)', default=25)
@click.option('-e', '--ehlo', help='Say EHLO as HOST', metavar='HOST')
@click.option('-f', '--fromaddr', help='Sender address')
def main(host, address, port, ehlo, fromaddr):
    f = VerifyFactory(address, ehlo, fromaddr)
    reactor.connectTCP(host, port, f)
    reactor.run()

if __name__ == '__main__':
    main()
