"""Hidden console entry only. Never falls back to echoed stdin."""
from java.lang import System, String
from java.util import Arrays
from com.moneydance.security import SecretKeyCallback

class LocalPassword(SecretKeyCallback):
    def __init__(self, console=None):
        self.console = console if console is not None else System.console()
        self.secret = None
        if self.console is None:
            raise RuntimeError('No private terminal available. Run the launcher in a local PowerShell window.')

    def read(self):
        self.console.printf('Moneydance password: ')
        chars = self.console.readPassword()
        if chars is None:
            raise RuntimeError('Password entry cancelled')
        confirmation = None
        try:
            self.console.printf('Confirm Moneydance password: ')
            confirmation = self.console.readPassword()
            if confirmation is None:
                raise RuntimeError('Password entry cancelled')
            if len(chars) != len(confirmation) or any(chars[i] != confirmation[i] for i in range(len(chars))):
                raise RuntimeError('PASSWORD_MISMATCH: Passwords do not match. No file opened; run again.')
            # Moneydance requires an immutable Java String. This cannot be
            # reliably erased; keep only in this short-lived local JVM.
            self.secret = String(chars)
        finally:
            Arrays.fill(chars, u'\x00')
            if confirmation is not None:
                Arrays.fill(confirmation, u'\x00')
        return self

    def getPassphrase(self, *args):
        if self.secret is None:
            raise RuntimeError('Password not entered')
        return self.secret

    def setVerifier(self, verifier):
        pass

    def clear(self):
        self.secret = None
