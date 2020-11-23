# encoding: utf-8
import os
import sys
import time
import logging

from PyQt4.QtGui import QApplication, QIcon, QAction
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from systray import SysTray

PWD = os.path.split(os.path.realpath(__file__))[0]
logging.basicConfig(filename=PWD + "/log/todo.log",
                    format="%(asctime)s " + logging.BASIC_FORMAT,
                    level=logging.DEBUG
                    )


def setIcon(ti):
    ti.icon = QIcon(PWD + '/icon/todo.png')
    ti.setIcon(ti.icon)


def editTodo():
    os.system("/usr/bin/io.elementary.code {}/todo.list".format(PWD))


def addSeparator(ti):
    ti.menu.addSeparator()  # 添加分割线


def addTodoAction(ti, key, msg):
    ti.__setattr__(key, QAction('✨' + msg.strip(), ti, triggered=ti.doNothing))
    ti.menu.addAction(ti.__getattribute__(key))

def addTodos(ti):
    filename = PWD + "/todo.list"
    if not os.path.isfile(filename):
        os.system(f"touch {filename}")
    with open(filename, 'r') as f:
        for i, msg in enumerate(f):
            key = 'i' + str(i)
            addTodoAction(ti, key, msg)


def reloadTodos(ti):
    logging.warning("run reload todos")
    with open(PWD + '/todo.list', 'r') as f:
        current_item_num = len(ti.menu.actions())- 4
        file_item_num = 0
        for i, msg in enumerate(f):
            file_item_num += 1
            key = 'i' + str(i)
            try:
                # 如果存在key，则修改显示的文本内容
                ti.__getattribute__(key).setText('✨' + msg.strip())
            except AttributeError as ex:
                logging.exception(ex)
                logging.warning("add action {key}: {msg}")
                # 如果不存在key，则新增对应key和内容
                addTodoAction(ti, key, '✨' + msg.strip())

        logging.warning(f"current_item_num: {current_item_num}, file_item_num: {file_item_num}")
        #如果删除了部分行，则删除原有的多余key
        if current_item_num > file_item_num:
            for i in range(file_item_num, current_item_num):
                key = 'i' + str(i)
                ti.menu.removeAction(ti.__getattribute__(key))
                ti.__delattr__(key)


def addEditAction(ti):
    ti.editTodo = editTodo
    ti.editAction = QAction(u'编辑todo', ti, triggered=ti.editTodo)
    ti.menu.addAction(ti.editAction)


def addExitAction(ti):
    ti.quitAction = QAction(u"退出", ti, triggered=ti.exitApp)
    ti.menu.addAction(ti.quitAction)


class reloadTodoHandler(FileSystemEventHandler):
    def on_created(self, event):
        logging.warning(f'event type: {event.event_type} path: {event.src_path}')

    def on_modified(self, event):
        logging.warning(f'event type: {event.event_type} path: {event.src_path}')
        reloadTodos(ti)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ti = SysTray()
    setIcon(ti)

    addExitAction(ti)
    addSeparator(ti)
    addEditAction(ti)
    addSeparator(ti)
    # todo的内容
    addTodos(ti)
    ti.show()
    ti.showMessage(u"提示", u"程序启动", 2)

#    import pdb;pdb.set_trace()

    event_handler = reloadTodoHandler()
    event_handler.ti = ti
    observer = Observer()
    observer.schedule(event_handler, path=PWD, recursive=False)
    observer.start()

    logging.warning("started")

    sys.exit(app.exec_())
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

