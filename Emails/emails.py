import smtplib


class Email:
    def send_email(self, to, subject, text):
        body = '\r\n'.join(('From: %s' % self.__login,
                            'To: %s' % to,
                            'Subject: %s' % subject,
                            '', text)).encode('utf-8').strip()
        self.__server.sendmail(self.__login, [to], body)

    def __auth_email(self):
        self.__server = smtplib.SMTP_SSL(host=self.__host, port=self.__port)
        self.__server.login(self.__login, self.__password)

    def __init__(self, login, password, host, port):
        self.__login = login
        self.__password = password
        self.__host = host
        self.__port = port
        self.__auth_email()
