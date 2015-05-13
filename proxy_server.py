# -*- coding: cp1252 -*-
# <PythonProxy.py>
#
#Copyright (c) <2009> <Fábio Domingues - fnds3000 in gmail.com>
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation
#files (the "Software"), to deal in the Software without
#restriction, including without limitation the rights to use,
#copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following
#conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.

"""\
Copyright (c) <2009> <Fábio Domingues - fnds3000 in gmail.com> <MIT Licence>

                  **************************************
                 *** Python Proxy - A Fast HTTP proxy ***
                  **************************************

Neste momento este proxy é um Elie Proxy.

Suporta os métodos HTTP:
 - OPTIONS;
 - GET;
 - HEAD;
 - POST;
 - PUT;
 - DELETE;
 - TRACE;
 - CONENCT.

Suporta:
 - Conexões dos cliente em IPv4 ou IPv6;
 - Conexões ao alvo em IPv4 e IPv6;
 - Conexões todo o tipo de transmissão de dados TCP (CONNECT tunneling),
     p.e. ligações SSL, como é o caso do HTTPS.

A fazer:
 - Verificar se o input vindo do cliente está correcto;
   - Enviar os devidos HTTP erros se não, ou simplesmente quebrar a ligação;
 - Criar um gestor de erros;
 - Criar ficheiro log de erros;
 - Colocar excepções nos sítios onde é previsível a ocorrência de erros,
     p.e.sockets e ficheiros;
 - Rever tudo e melhorar a estrutura do programar e colocar nomes adequados nas
     variáveis e métodos;
 - Comentar o programa decentemente;
 - Doc Strings.

Funcionalidades futuras:
 - Adiconar a funcionalidade de proxy anónimo e transparente;
 - Suportar FTP?.


(!) Atenção o que se segue só tem efeito em conexões não CONNECT, para estas o
 proxy é sempre Elite.

Qual a diferença entre um proxy Elite, Anónimo e Transparente?
 - Um proxy elite é totalmente anónimo, o servidor que o recebe não consegue ter
     conhecimento da existência do proxy e não recebe o endereço IP do cliente;
 - Quando é usado um proxy anónimo o servidor sabe que o cliente está a usar um
     proxy mas não sabe o endereço IP do cliente;
     É enviado o cabeçalho HTTP "Proxy-agent".
 - Um proxy transparente fornece ao servidor o IP do cliente e um informação que
     se está a usar um proxy.
     São enviados os cabeçalhos HTTP "Proxy-agent" e "HTTP_X_FORWARDED_FOR".

"""

import socket, thread, select
import json
from pprint import pprint
import time,os

__version__ = '0.1.0 Draft 1'
BUFLEN = 8192
VERSION = 'Python Proxy/'+__version__
HTTPVER = 'HTTP/1.1'

class ConnectionHandler:
    def __init__(self, connection, address, timeout):
        self.client = connection
        self.client_buffer = ''
        self.data = ''
        self.timeout = timeout
        self.method, self.path, self.protocol = self.get_base_header()
        if self.method=='CONNECT':
            self.method_CONNECT()
        elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT',
                             'DELETE', 'TRACE'):
            self.method_others()
        self.client.close()
        self.target.close()
        data=self.data.split('svdata=')[-1]
        self.data=json.loads(data)
        if self.path:# == "/kcsapi/api_start2":
            path=self.path[1:]+'.txt'
            if not os.path.exists(os.path.split(path)[0]):
                os.makedirs(os.path.split(path)[0])
            str_data=json.dumps(self.data, indent=4, skipkeys=True)
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    f.write(str_data)
            else:
                with open(path,'r') as f:
                    old_data = f.read()
                
                if old_data!=str_data:
                    # print "update api_data of " + self.path
                    with open(path, 'w') as f:
                        f.write(str_data)
        # pprint(self.data)
        # print self.path

    def get_base_header(self):
        while 1:
            self.client_buffer += self.client.recv(BUFLEN)
            end = self.client_buffer.find('\n')
            if end!=-1:
                break
        print 'POST %s'%self.client_buffer[35:end-9]#debug
        data = (self.client_buffer[:end+1]).split()
        self.client_buffer = self.client_buffer[end+1:]
        return data

    def method_CONNECT(self):
        self._connect_target(self.path)
        self.client.send(HTTPVER+' 200 Connection established\n'+
                         'Proxy-agent: %s\n\n'%VERSION)
        self.client_buffer = ''
        self._read_write()        

    def method_others(self):
        self.path = self.path[7:]
        i = self.path.find('/')
        host = self.path[:i]        
        self.path = self.path[i:]
        self._connect_target(host)
        self.target.send('%s %s %s\n'%(self.method, self.path, self.protocol)+
                         self.client_buffer)
        # print self.client_buffer
        self.client_buffer = ''
        self._read_write()

    def _connect_target(self, host):
        i = host.find(':')
        if i!=-1:
            port = int(host[i+1:])
            host = host[:i]
            if host=='localhost.':
                host="127.0.0.1"
                # print host
        else:
            port = 80

        port = 8888
        host = "127.0.0.1"
        (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
        self.target = socket.socket(soc_family)
        self.target.connect(address)

    def _read_write(self):
        time_out_max = self.timeout/3
        socs = [self.client, self.target]
        count = 0
        while 1:
            count += 1
            (recv, _, error) = select.select(socs, [], socs, 3)
            if error:
                break
            if recv:
                for in_ in recv:
                    data = in_.recv(BUFLEN)
                    if in_ is self.client:
                        out = self.target
                    else:
                        out = self.client
                    if data:
                        self.data+=data
                        out.send(data)
                        count = 0
            if count == time_out_max:
                break
class Server(object):
    """start a server,and save data"""
    def __init__(self,host='localhost', port=8887, IPv6=False, timeout=60):
        if IPv6==True:
            soc_type=socket.AF_INET6
        else:
            soc_type=socket.AF_INET
        self.soc = socket.socket(soc_type)
        self.soc.bind((host, port))
        self.data={}
        self.path=''
        self.time=0
        self.read_path('kcsapi')
        print "Serving on %s:%d."%(host, port)#debug
        self.soc.listen(0)

    def read_path(self,path):
        for i in os.listdir(path):
            if i[0]=='.':
                continue
            path_temp=path+'/'+i
            if os.path.isdir(path_temp):
                self.read_path(path_temp)
            elif os.path.isfile(path_temp):
                with open(path_temp) as f:
                    data=f.read()
                    self.data[('/'+path_temp)[:-4]]=json.loads(data)
    def start(self):
        while 1:
            thread.start_new_thread(self.handler, self.soc.accept())
    def handler(self, conn, addr):
        ch=ConnectionHandler(conn, addr, 60)
        self.data[ch.path]=ch.data
        self.path=ch.path
        self.time=time.time()
        # print self.data[1]

if __name__ == '__main__':
    s=Server()