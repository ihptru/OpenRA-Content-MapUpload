#!/usr/bin/env python

import urllib2
import hashlib
import httplib
import mimetypes
import urlparse
import os
import json
import getpass

class RemoteUpload:
    
    def __init__(self):
        self.url = "http://content.open-ra.org"
        self.loginname = ""
        self.password = ""
        self.login_return = "-1"
        self.map_file = ""
        self.p_id = 0
        try:
            urllib2.urlopen(self.url)
        except urllib.error.URLError as e:
            print(e)
            exit(1)

    def start(self):
        if not self.login():
            exit(1)
        
        self.map_file = raw_input("Enter full path to your map file: ").strip()
        if not os.path.isfile(self.map_file):
            print("No such file!")
            exit(1)
        print("File is found!")
        version = raw_input("Is it a new version of some other of your maps? yes/no: ")
        if version == "no":
            print("Then I'll just upload it for you!...")
            print("...")
            result = self.upload_map()
            if result == "0":
                print("Done!!!")
            else:
                print("FAILED!!!")
        else:
            print("Fetching list of your maps......\n")
            try:
                request = urllib2.urlopen(self.url + "/api/editor.php?list&vlogin="+self.loginname+"&vpass="+self.password).read().decode()
                if request == "-1":
                    print("Authenticated: no\nAbort operation!\n")
                    exit(1)
            except:
                print("Fetching list of maps FAILED!")
                exit(1)
            y = json.loads(request)
            for item in y:
                print(("ID: "+item['id']).ljust(9)+" | "+("Title: "+item['title']).ljust(45)[0:45]+" | "+("Hash: "+item['hash']).ljust(20))
            self.p_id = raw_input("Enter ID of the previous version of this map: ").strip()
            print("Uploading and linking map......")
            result = self.upload_map()
            if result == "0":
                print("Done!!!")
            else:
                print(result)
                print("FAILED!!!")

    def login(self):
        self.loginname = raw_input("Enter login name: ")
        password = getpass.getpass("Enter password: ")
        self.password = hashlib.md5(password.encode()).hexdigest()
        try:
            self.login_return = urllib2.urlopen(self.url + "/api/editor.php?login=" + self.loginname +"&pass=" + self.password).read().decode()
        except:
            pass
        if self.login_return != "0":
            print("Login failed!")
            return False
        print("Logged in!")
        return True

    def upload_map(self):
        fields = [["login", self.loginname], ["pass", self.password]]
        if self.p_id != 0:
            fields.append(['p_id', self.p_id])
        files = [["map_upload", os.path.basename(self.map_file), open(self.map_file, 'r').read()]]
        return self.posturl( "http://content.open-ra.org/api/editor.php", fields, files )

    def posturl(self, url, fields, files):
        urlparts = urlparse.urlsplit(url)
        return self.post_multipart(urlparts[1], urlparts[2], fields, files)

    def post_multipart(self, host, selector, fields, files):
        """
        Post fields and files to an http host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return the server's response page.
        """
        content_type, body = self.encode_multipart_formdata(fields, files)
        h = httplib.HTTP(host)
        h.putrequest('POST', selector)
        h.putheader('content-type', content_type)
        h.putheader('content-length', str(len(body)))
        h.endheaders()
        h.send(body)
        errcode, errmsg, headers = h.getreply()
        return h.file.read()

    def encode_multipart_formdata(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % self.get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body
    
    def get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

if __name__ == "__main__":
    remoteupload = RemoteUpload()

    remoteupload.start()
   
