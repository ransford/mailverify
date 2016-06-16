Tests whether an email address is deliverable without actually sending mail to
that address.  Recipient is not notified.

Prerequisites: `click` and `twisted`.

    $ pip install -r requirements.txt

Usage:

    $ python -m mailverify --help
    Usage: mailverify.py [OPTIONS] HOST ADDRESS

    Options:
      -p, --port INTEGER   Connect to port (default 25)
      -e, --ehlo HOST      Say EHLO as HOST
      -f, --fromaddr TEXT  Sender address
      --help               Show this message and exit.

For example, say you're wondering whether ben@ransford.org is deliverable:

    $ host -t mx ransford.org
    ransford.org mail is handled by 30 ASPMX4.GOOGLEMAIL.COM.
    ransford.org mail is handled by 10 ASPMX.L.GOOGLE.COM.
    ransford.org mail is handled by 30 ASPMX2.GOOGLEMAIL.COM.
    ransford.org mail is handled by 30 ASPMX3.GOOGLEMAIL.COM.
    ransford.org mail is handled by 20 ALT2.ASPMX.L.GOOGLE.COM.
    ransford.org mail is handled by 30 ASPMX5.GOOGLEMAIL.COM.
    ransford.org mail is handled by 20 ALT1.ASPMX.L.GOOGLE.COM.

Choose one of the hosts in the list and test delivery with `mailverify`:

    $ python -m mailverify aspmx.l.google.com ben@ransford.org
    connected!
    < 220 mx.google.com ESMTP r88si6832467pfa.128 - gsmtp
    > EHLO foo.com
    < 250-mx.google.com at your service, [205.175.118.110]
    < 250-SIZE 157286400
    < 250-8BITMIME
    < 250-STARTTLS
    < 250-ENHANCEDSTATUSCODES
    < 250-PIPELINING
    < 250-CHUNKING
    < 250 SMTPUTF8
    > MAIL FROM:<foo.com@foo.com>
    < 250 2.1.0 OK r88si6832467pfa.128 - gsmtp
    > RCPT TO:<ben@ransford.org>
    < 250 2.1.5 OK r88si6832467pfa.128 - gsmtp
    ADDRESS WAS VALID!
    > RSET
    < 250 2.1.5 Flushed r88si6832467pfa.128 - gsmtp
    > QUIT
    < 221 2.0.0 closing connection r88si6832467pfa.128 - gsmtp
    Error: Disconnecting cleanly
