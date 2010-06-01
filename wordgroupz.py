## Copyright (C) 2010 Ratnadeep Debnath <rtnpro@fedoraproject.org>

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import pygtk
import gtk
import sqlite3
import os

usr_home = os.environ['HOME']
wordgroupz_dir = usr_home+'/.wordgroupz'
db_file_path = wordgroupz_dir+'/wordz'

def db_init():
    if not os.path.exists(wordgroupz_dir):
        os.mkdir(wordgroupz_dir, 0755)
    #if not os.path.exists(db_file_path):
    conn = sqlite3.connect(db_file_path)
    c =  conn.cursor()
    tables = []
    for x in c.execute('''select name from sqlite_master'''):
        tables.append(x[0])
    if not 'word_groups' in tables:
        c.execute('''create table word_groups
        (word text, grp text)''')
        #c.execute('''insert into word_groups
        #values('dummy', 'dummy')''')
    if not 'groups' in tables:
        c.execute('''create table groups
        (grp text)''')
        #c.execute('''insert into groups
        #values('dummy')''')
    conn.commit()
    c.close()
    conn.close()

def list_groups():
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    groups = []
    for row in c.execute("""select grp from groups order by grp"""):
        if row[0] is not 'dummy':
            groups.append(row[0])
    c.close()
    return groups

def list_words_per_group(grp):
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    words = []
    t = (grp,)
    for row in c.execute("""select word from word_groups where grp=?""",t):
        if row[0] != '' and row[0]!='dummy':
            words.append(row[0])
    c.close()
    return words


def add_to_db(word, grp):
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    t = (grp,)
    if grp not in list_groups():
        c.execute("""insert into groups values (?)""",t)
        conn.commit()
    if word is not '':
        t = (word, grp)
        c.execute('''insert into word_groups
            values(?,?)''', t)
        conn.commit()
    c.close()


class wordzGui:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("wordgroupz.glade")
        self.window = self.builder.get_object("MainWindow")
        self.window.set_icon_from_file("./icons/wordgroupz.png")
        self.window.set_title("wordGroupz")
        self.builder.connect_signals(self)
        self.get_word = self.builder.get_object("get_word")
        self.get_group = gtk.combo_box_entry_new_text()
        self.get_group.child.connect('key-press-event', self.item_list_changed)
        for x in list_groups():
            self.get_group.append_text(x)
        self.table1 = self.builder.get_object("table1")
        self.get_group.show()
        self.table1.attach(self.get_group, 1,2,1,2)

        self.treestore = gtk.TreeStore(str)
        for group in list_groups():
            piter = self.treestore.append(None, [group])
            for word in list_words_per_group(group):
                self.treestore.append(piter, [word])
        self.treeview = gtk.TreeView(self.treestore)
        self.tvcolumn = gtk.TreeViewColumn('Word Groups')
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.treeview.set_reorderable(True)
        self.scrolledwindow1 = self.builder.get_object("scrolledwindow1")
        self.scrolledwindow1.add_with_viewport(self.treeview)

    def item_list_changed(self, widget=None, event=None):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == "Return":
            self.get_group.append_text(widget.get_text())
            widget.set_text("")

    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()

    def on_add_clicked(self, widget, data=None):
        word = self.get_word.get_text()
        get_group_ch = self.get_group.child
        group = get_group_ch.get_text()
        #print group
        add_to_db(word, group)
        self.refresh_groups(group)
        self.treestore.clear()
        for group in list_groups():
            piter = self.treestore.append(None, [group])
            for word in list_words_per_group(group):
                self.treestore.append(piter, [word])

    def item_list_changed(self, widget=None, event=None):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == "Return":
            self.item_list.append_text(widget.get_text())
            widget.set_text('')

    def refresh_groups(self, grp):
        self.get_group.append_text(grp)

    def on_about_clicked(self, widget, data=None):
        dialog = gtk.AboutDialog()
        dialog.set_name('wordz')
        dialog.set_copyright('(c) 2010 Ratnadeep Debnath')
        dialog.set_website('http://gitorious.org/wordGroupz/wordgroupz')
        dialog.set_authors(['Ratnadeep Debnath <rtnpro@gmail.com>'])
        dialog.set_program_name('wordGroupz')
        dialog.run()
        dialog.destroy()

    def on_find_clicked(self, widget, data=None):
        search = self.builder.get_object("search")
        search_txt = search.get_text()
        groups = list_groups()
        words = list
        self.treestore.clear()
        for group in groups:
            if search_txt in list_words_per_group(group):
                piter = self.treestore.append(None, [group])
                for word in list_words_per_group(group):
                    self.treestore.append(piter, [word])

    def on_back_clicked(self, widget, data=None):
        self.treestore.clear()
        for group in list_groups():
            piter = self.treestore.append(None, [group])
            for word in list_words_per_group(group):
                self.treestore.append(piter, [word])


if __name__ == "__main__":
    db_init()
    win = wordzGui()
    win.window.show_all()
    gtk.main()