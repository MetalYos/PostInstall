from tkinter import *
from tkinter import ttk
import os
from subprocess import call


class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """

    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.interior.bind_all("<MouseWheel>", _on_mousewheel)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class AppEntryFrame(Frame):
    def __init__(self, parent, app_name, pack_command='None', description='None'):
        super().__init__(parent)
        self.parent = parent
        self.app_name = app_name
        self.pack_command = pack_command
        self.description = description

        self.is_installed = IntVar()
        self.is_add_to_script = IntVar()
        self.is_add_to_script.set(1)
        self.widgets = []

        self.init_ui()

        self.installed_color = '#00FF06'
        self.installed_active_color = '#8CFF8E'
        self.default_bg_color = self.cget('bg')
        self.default_active_color = self.installed_checkbutton.cget(
            'activebackground')

    def init_ui(self):
        # Create Left Frame
        left_frame = Frame(self)
        left_frame.pack(side=LEFT, expand=YES, fill=X, padx=20)
        self.widgets.append(left_frame)

        # Add the App Name to the left frame
        temp = Label(left_frame, text='Name: ')
        temp.grid(row=0, column=0, sticky=W)
        self.widgets.append(temp)
        temp = Label(left_frame, text=self.app_name,
                     font=('Helvetica', 10, 'bold'))
        temp.grid(row=0, column=1, sticky=W)
        self.widgets.append(temp)
        # Add the Install Command to the left frame
        temp = Label(left_frame, text='Install Command: ')
        temp.grid(row=1, column=0, sticky=W)
        self.widgets.append(temp)
        temp = Entry(left_frame, width=50)
        temp.insert(0, self.pack_command)
        temp.grid(row=1, column=1, sticky=W, ipadx=4, ipady=4, columnspan=2)
        # Add the Description to the left frame
        temp = Label(left_frame, text='Description: ')
        temp.grid(row=2, column=0, sticky=W)
        self.widgets.append(temp)
        temp = Label(left_frame, text=self.description, anchor=W, justify=LEFT)
        temp.grid(row=2, column=1, sticky=W)
        self.widgets.append(temp)

        # Create right frame
        right_frame = Frame(self)
        right_frame.pack(side=RIGHT, padx=20)
        # Add Installed Checkbutton to the right frame
        self.installed_checkbutton = Checkbutton(
            self, text='Installed', variable=self.is_installed, onvalue=1, offvalue=0, command=self.on_installed_changed)
        self.installed_checkbutton.pack(side=TOP, expand=YES, fill=Y)
        self.widgets.append(self.installed_checkbutton)
        # Add 'Add to Script' Checkbutton to the right frame
        self.add_to_script_checkbutton = Checkbutton(
            self, text='Add to Script', variable=self.is_add_to_script, onvalue=1, offvalue=0)
        self.add_to_script_checkbutton.pack(side=TOP, expand=YES, fill=Y)
        self.widgets.append(self.add_to_script_checkbutton)

    def on_installed_changed(self):
        if self.is_installed.get() == 1:
            self.change_background_color(
                self.installed_color, self.installed_active_color)
        else:
            self.change_background_color(
                self.default_bg_color, self.default_active_color)

    def change_background_color(self, color, active_color):
        for widget in self.widgets:
            widget.configure(bg=color)
        self.installed_checkbutton.configure(activebackground=active_color)
        self.add_to_script_checkbutton.configure(activebackground=active_color)
        self.configure(bg=color)


class MainApp(Tk):
    def __init__(self):
        super().__init__()
        self.filename = 'applications.txt'
        if os.path.isfile(self.filename) is False:
            raise Exception(
                f"{filename} was not found! can't continue with program!")
        self.install_script = 'install.sh'
        self.entries = []
        self.init_ui()

    def init_ui(self):
        self.init_ui_from_file()
        # Create the 'Create Installation Script' button
        self.create_script_button = Button(
            self, text="Create Installation Script", command=self.create_installation_script)
        self.create_script_button.pack(side=LEFT, padx=20, pady=20)
        # Create the 'Run Installation Script' button
        self.run_script_button = Button(
            self, text='Run Installation Script', command=self.run_installation_script)
        self.run_script_button.pack(side=LEFT, padx=20, pady=20)
        # Create the 'Ecit Application' button
        self.exit_app_button = Button(
            self, text='Exit Application', command=self.exit_application)
        self.exit_app_button.pack(side=RIGHT, padx=20, pady=20)

    def init_ui_from_file(self):
        self.listview_frame = VerticalScrolledFrame(self)
        self.listview_frame.pack(side=TOP, expand=YES, fill=BOTH)

        name = None
        pack_install = None
        description = None
        with open(self.filename) as app_file:
            for line in app_file:
                if line[0] == '^':
                    name = app_file.readline().rstrip()
                    pack_install = app_file.readline().rstrip()
                    description = app_file.readline().rstrip()

                    entry = AppEntryFrame(
                        self.listview_frame.interior, name, pack_install, description)
                    entry.configure(bd=3, relief=GROOVE)
                    entry.pack(side=TOP, padx=10, pady=5, expand=YES, fill=X)
                    self.entries.append(entry)

    def create_installation_script(self):
        with open(self.install_script, 'w') as inst_file:
            inst_file.write('#!/bin/bash\n\n')
            for entry in self.entries:
                if entry.is_add_to_script.get() == 1 and ("pacman" in entry.pack_command or "yay" in entry.pack_command):
                    inst_file.write(f'\n# Installing {entry.app_name}')
                    if "None" not in entry.description:
                        inst_file.write(f' - {entry.description}\n')
                    inst_file.write(f'{entry.pack_command}\n')
            print('Finished building script')

    def run_installation_script(self):
        if os.path.isfile(self.install_script) is False:
            messagebox.showerror(
                'Error', 'No Installation script was found! Please create an installation script by pressing on the Create button before installing')
        else:
            os.chmod(self.install_script, 0o755)
            call(f'./{self.install_script}', shell=True)

    def exit_application(self):
        self.destroy()


def main():
    top = MainApp()
    top.minsize(500, 500)
    top.mainloop()


if __name__ == "__main__":
    main()
