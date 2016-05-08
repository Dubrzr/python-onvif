import base64
import hashlib
import datetime

from suds.sax.element import Element
from suds.sax.date import DateTime
from suds.wsse import UsernameToken, wssens, wsuns

wspassd = ('Type',
           'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest')
wsenctype = ('EncodingType',
             'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary')


class UTC(DateTime):
    """
    Represents current UTC time.
    """

    def __init__(self, date=None):
        if date is None:
            date = datetime.datetime.utcnow()
        DateTime.__init__(self, date)

class UsernameDigestToken(UsernameToken):

    def setcreated(self, *args, **kwargs):
        UsernameToken.setcreated(self, *args, **kwargs)
        self.created = str(UTC(self.created))

    def reset(self):
        self.nonce = None
        self.created = None

    def generate_digest(self):
        # Password_Digest = Base64 ( SHA-1 ( nonce + created + password ) )
        if self.nonce is None:
            self.setnonce()
        if self.created is None:
            self.setcreated()

        if isinstance(self.nonce, str):
            self.nonce = self.nonce.encode('ascii')

        m = hashlib.sha1()
        m.update(self.nonce)
        m.update(self.created.encode('ascii'))
        m.update(self.password.encode('ascii'))

        digest = base64.encodebytes(m.digest())[:-1]
        return digest

    def xml(self):
        """
        Get xml representation of the object.
        @return: The root node.
        @rtype: L{Element}
        """
        root = Element('UsernameToken', ns=wssens)

        u = Element('Username', ns=wssens)
        u.setText(self.username)
        root.append(u)

        p = Element('Password', ns=wssens)
        p.setText(self.generate_digest())
        p.set(wspassd[0], wspassd[1])
        root.append(p)

        n = Element('Nonce', ns=wssens)
        n.setText(base64.encodebytes(self.nonce)[:-1])
        n.set(wsenctype[0], wsenctype[1])
        root.append(n)

        n = Element('Created', ns=wsuns)
        n.setText(self.created)
        root.append(n)

        self.reset()
        return root