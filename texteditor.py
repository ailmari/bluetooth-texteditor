import hashlib
import tkinter as tk
from time import gmtime, strftime
from bluetooth import *
import _thread


def now():
    return strftime('%H:%M:%S', gmtime())


class Text_editor_program(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        _thread.start_new_thread(Bluetooth, (self,))
        self.set_text_window()

    def set_text_window(self):
        self.text_window = Text_window(self)
        self.text_window.grid()
        self.text_window.start()


class Text_window(tk.Text):
    def __init__(self, parent):
        tk.Text.__init__(self, parent)
        self.parent = parent
        self.last_hash = self.get_hash()

    def start(self):
        self.set_last()
        self.last_written()

    def set_last(self):
        self.mark_set('last', 'insert')
        self.mark_gravity('last', 'left')

    def print_out(func):
        def wrapped_function(self, *args, **kwargs):
            text = func(self, *args, **kwargs)
            if text:
                print('{}: {} @ {}'.format(now(), text[0], text[1]))
        return wrapped_function

    def get_hash(self):
        return hashlib.md5(self.get('1.0', 'end').encode('utf-8')).digest()

    def has_changed(self):
        if self.last_hash != self.get_hash():
            return True
        else:
            return False

    @print_out
    def last_written(self):
        last_text = self.get('last', 'insert')
        last_index = self.index('last')
        if last_text and self.has_changed():
            out = (last_text, last_index)
            self.last_hash = self.get_hash()
        else:
            out = None
        self.parent.after(10, self.last_written)
        self.set_last()
        return out

def Bluetooth(texteditor):
    server_sock=BluetoothSocket( RFCOMM )
    server_sock.bind(("",PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    advertise_service( server_sock, "SampleServer",
                       service_id = uuid,
                       service_classes = [ uuid, SERIAL_PORT_CLASS ],
                       profiles = [ SERIAL_PORT_PROFILE ],
    #                   protocols = [ OBEX_UUID ]
                        )

    print("Waiting for connection on RFCOMM channel %d" % port)

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

    try:
        while True:
            data = client_sock.recv(1024)
            if len(data) == 0: break
            print("received [%s]" % data)
            print('{}'.format(texteditor.text_window.insert('last', data)))
    except IOError:
        pass

    print("disconnected")

    client_sock.close()
    server_sock.close()
    print("all done")

if __name__ == '__main__':
    program = Text_editor_program()
    program.mainloop()
