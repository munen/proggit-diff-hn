# -*- coding: utf-8 -*-

from email.Header import Header
from email.MIMEText import MIMEText
from email.Utils import parseaddr, formataddr
from smtplib import SMTP
import ConfigParser
import cgi
import difflib
import simplejson
import smtplib
import urllib

class Config:

  def __init__(self):
    ini_file = "config.ini"

    config = ConfigParser.ConfigParser()
    config.readfp(open(ini_file))
    self.from_addr    = config.get("GENERAL", "FROM")
    self.to_addr      = config.get("GENERAL", "TO")
    self.gmail_user   = config.get("GENERAL", "GMAIL_USER")
    self.gmail_pwd    = config.get("GENERAL", "GMAIL_PWD")

class ProggitSubmissions(Config):

  def compare(self):
    """
      Read proggit's frontpage, check each submission against HN database.
    """
  
    proggit_api = "http://open.dapper.net/transform.php?dappName=Proggit&transformer=JSON&applyToUrl=http%3A%2F%2Fwww.reddit.com%2Fr%2Fprogramming%2F"
    ihn_api = "http://api.ihackernews.com/getid?url=%s"
    
    json = simplejson.loads(urllib.urlopen(proggit_api).readline())
    on_hn = []
    off_hn = []
    
    # Loading submissions from proggit's front page
    for submission in json['groups']['submission']:
      title = submission['title'][0]['value'].encode("utf-8")
      url = submission['title'][0]['href']
      points = submission['points'][0]['value']
      try:
        comments_no = submission['comments'][0]['value']
        comments_link = submission['comments'][0]['href']
      except:
        comments_no = '0 comments'
        comments_link = ''

      is_on_hn = simplejson.loads(urllib.urlopen(ihn_api %\
          cgi.escape(url)).readline())
   
      if is_on_hn:
        on_hn.append({'title':title})
      else:
        off_hn.append({'title':title, 'url':url, 'points':points,
          'comments_no':comments_no, 'comments_link':comments_link})

    return on_hn, off_hn


  def main(self):
    """ Get proggit/hn diff. Then mail this information. """

    on_hn, off_hn = self.compare()

    mail_body = "Ratio on hn/off hn: %s/%s" % (len(on_hn), len(off_hn))

    for submission in off_hn:
      try:
        mail_body += u"\n\n" +\
          submission['title'].encode("utf-8") + u"\n\t" +\
          submission['url'] + u"\n\t" +\
          submission['points'] + " points" + u"\n\t" +\
          submission['comments_no'] + u"\n\t" +\
          submission['comments_link']
      except:
        mail_body += "Submission omitted due to exception"

    #print mail_body.encode("utf-8")
    Mail.send_mail(self.from_addr,
        self.to_addr,
        "Automated Proggit/HN diff", mail_body, self.gmail_user, self.gmail_pwd)

class Mail:

  @staticmethod
  def send_mail(sender, recipient, subject, body, gmail_user, gmail_pwd):
    """ Send e-mail. All input should be utf-8 encoded. """

    header_charset = 'ISO-8859-1'
  
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
      try:
        body.encode(body_charset)
      except UnicodeError:
        pass
      else:
        break
  
    # Split real name (which is optional) and email address parts
    sender_name, sender_addr = parseaddr(sender)
    recipient_name, recipient_addr = parseaddr(recipient)
  
    # We must always pass Unicode strings to Header, otherwise it will
    # use RFC 2047 encoding even on plain ASCII strings.
    sender_name = str(Header(unicode(sender_name), header_charset))
    recipient_name = str(Header(unicode(recipient_name), header_charset))
  
    # Make sure email addresses do not contain non-ASCII characters
    sender_addr = sender_addr.encode('ascii')
    recipient_addr = recipient_addr.encode('ascii')
  
    # Create the message ('plain' stands for Content-Type: text/plain)
    msg = MIMEText(body.encode(body_charset), 'plain', body_charset)
    msg['From'] = formataddr((sender_name, sender_addr))
    msg['To'] = formataddr((recipient_name, recipient_addr))
    msg['Subject'] = Header(unicode(subject), header_charset)
  
    server = smtplib.SMTP('smtp.gmail.com',587) #port 465 or 587
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(gmail_user,gmail_pwd)
    server.sendmail(sender, recipient, msg.as_string())
    server.close()


if __name__ == "__main__":
  prog = ProggitSubmissions()
  prog.main()

