#  -*- coding: utf-8  -*-


import os
import sys
import sys
import socket
import threading
import getopt
import subprocess

#グローバル変数の定義
listen                    = False
command             = False
upload                  = False
execute                 = ""
target                    = ""
upload_destination = ""
port                      = 0

def usage():
    print "BHP Net Tool"
    print
    print "Usage: Netcat.py -t target_host -p port"
    print "-l listen                           - listen on [host]  : [port] for incoming connection"
    print "-e execution                    - execute the given file upon receiving connection"
    print "-c --command                 - initialize a command shell"
    print "-u --upload=destination   -upon receving connection upload a file and write to [destination]"
    print 
    print
    print "Examples: "
    print "Netcat.py -t 192.168.0.1 -p 5555 -l -c"
    print "Netcat.py -t 192.168.0.1 -p 5555 -l -c -u c:\\target.exe"
    print "Netcat.py -t 192.168.0.1 -p 5555 -l -c \"cat /etc/passwd""
    print "echo 'ABCDEFGHI' | ./Netcat.py -t 192.168.11.12 -p 135"
    sys.exit(0)

def main():
    global listen
    global port 
    global execute
    global command
    global target
    global upload_destination

    if not len(sys.argv[1:]):
        usage()

    #コマンドラインオプションの読み込み
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port=", "command", "upload="])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        if 0 in ("-l", "--listen"):
            listen = True
        if o in ("-c", "--command"):
            command = True
        if 0 in ("-u", "--upload"):
            upload_destination = a
        if o in ("-t", "--target"):
            target = a
        if o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
    #接続を待機する？　それとも標準入力からデータを受け取って送信する？
    if  not listen and len(target) and port >0:

        #コマンドラインからの入力を'Buffer'に格納する。
        #入力がこないと接続が確立されないので標準入力でデータを送らない場合はCtrl-Dを入力すること。
        buffer = sys.stdin.read()

        #データ送信
        client_sender(buffer) 

    #接続待機を開始。
    #コマンドラインオプションに応じてファイルをアップロード、
    #コマンド実行、コマンドシェルの実行を行う。
    if  listen:
        server_loop()

main()

def client_sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STEREAM)

    try:
        #標的ホストへの接続
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:
            #標的ホストからのデータの待機
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response,

            #追加の入力を待機
            buffer = raw_input("")
            buffer += "\n"

           #データの送信
            client.send(buffer)

        except:
            print "    [*]   Exception: Existing. "
            
            #接続の終了
            client.close()
    
def server_loop():
    global target

    #待機するIPアドレスが指定されていない場合はすべてのインターフェースで待機する。
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accpt()

        #クライエントからの新しい接続を処理するスレッドの起動
        client_thread = threading.Thread(target=client_handler, args=(client_socket, ))
        client_thread.start()

def run_command(command):
    #文字列の末尾の改行を削除
    command = command.rstrip()

    #コマンドを実行し出力結果を取得
    try:
        output = subprocess.check_output(command, err=subproces.STDOUT, shell=True)
    except:
        output = "Fauiled to execute command.\r\n"
    
    #出力結果をクライエントに送信
    return output

def client_handler(client_socket):
    global upload
    global command
    global execute

    #ファイルアップロードを指定されているかどうか
    if len(upload_destination):
        
        #すべてのデータを読み取り、指定されたファイルにデータを書き込み。
        file_buffer = ""

        #受信データがなくなるまでデータ受信を接続
        while True:
            data = client_socket.recv(1024)

            if len(data) == 0:
                break
            
            else:
                file_buffer += data
        
        #受信したデータをファイルに書き込み
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            #ファイルの書き込みの成否を通知
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)

        except:
            client_socket.send("Failed to save file to &s\r\n" % upload_destination)
    
#コマンドを実行しているかどうかの確認
if len(execute):

    #コマンドを実行
    output = run_command(execute)

    client_socket.send(output)

#コマンド実行をされているかどうかの確認
if command:

    #プロンプトの表示
    prompt = <"BHP:#">
    client_socket.send(prompt)

    while True:

        #改行（エンターキー）を受け取るまでデータを受信
        cmd_buffer = ""
        while "\n" in cmd_buffer:
            cmd_buffer += client_socket.recv(1024)
            
        #コマンドの実行結果を取得
        response = run_command(cmd_buffer)
        response += prompt

        #コマンドの実行結果を送信
        client_socket.send(response)

#EOF


