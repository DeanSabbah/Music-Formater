import defs, logging, concurrent.futures, traceback
from tkinter import W, E, S, N, messagebox, filedialog, ttk, Tk, StringVar, DISABLED, NORMAL, Text
from pathlib import Path

from model import main

defs.logger.disabled = True

executor = None

class user_interface():    
    def __init__(self):
        self.root = Tk()
        self.root.title("Music folder formatter")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        self.mainframe:ttk.Frame = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N + W + E + S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.dir_path = StringVar()
        self.dir_path_entry = ttk.Entry(self.mainframe, width=50, textvariable=self.dir_path)
        self.dir_path_entry.grid(column=2, row=2, sticky=(E + W))
        
        self.dir_button = ttk.Button(self.mainframe, text="Choose Directory", command=get_path)
        self.dir_button.grid(column=4, row=2, sticky=(E))

        self.message_box = Text(self.mainframe, width=60, height=10, state=DISABLED, wrap='none')
        defs.message_box = self.message_box 
        
        self.message_box_check_var = StringVar()
        self.message_box_check = ttk.Checkbutton(self.mainframe, text="Display log", command=switch_message_box, variable=self.message_box_check_var)
        self.message_box_check.grid(column=2, row=3, sticky=(E))

        self.progress_bar = ttk.Progressbar(self.mainframe, orient="horizontal", length=306, mode="determinate", maximum=100)

        self.log_label = ttk.Label(self.mainframe, text="Log level: ")
        self.log_label.grid(column=3, row=3, sticky=(E))

        self.log_choice = StringVar()
        self.log_options = ["Off", "Debug", "Info", "Warning", "Error", "Critical"]
        self.log_select = ttk.OptionMenu(self.mainframe, self.log_choice, "Off", *self.log_options, command=set_log_level)
        self.log_select.grid(column=4, row=3, sticky=(W + E))

        self.json_var = StringVar()
        self.json_check = ttk.Checkbutton(self.mainframe, text="Generate JSON", command=switch_json, variable=self.json_var)
        self.json_check.grid(column=2, row=3, sticky=(W))
       
        self.run_button = ttk.Button(self.mainframe, text="Run", command=start)
        self.run_button.grid(column=2, row=4, sticky=(S + W))

        self.close_button = ttk.Button(self.mainframe, text="Close", command=on_closing)
        self.close_button.grid(column=4, row=4, sticky=(S + E))

        self.mainframe.columnconfigure(2, weight=1)
        self.mainframe.columnconfigure(3, weight=1)
        self.mainframe.columnconfigure(4, weight=1)
        self.mainframe.rowconfigure(1, weight=1)

def switch_json():
    defs.logger.info("Switching json to " + str(not defs.json_out))
    defs.json_out = not defs.json_out

def switch_message_box():
    defs.logger.info("Switching display of message boc to " + str(not defs.display_message_box))
    defs.display_message_box = not defs.display_message_box

def get_path():
    location = filedialog.askdirectory()
    defs.logger.info("Setting basepath to " + location)
    try:
        ui.dir_path.set(location)
    except Exception:
        defs.logger.fatal("Unkown Error, Quitting\n" + traceback.format_exc())
        close()
        return

def set_log_level(level):
    if level == "Off":
        defs.logger.disabled = True
        return
    defs.logger.disabled = False
    match level:
        case "Debug":
            defs.logger.setLevel(logging.DEBUG)
        case "Info":
            defs.logger.setLevel(logging.INFO)
        case "Warning":
            defs.logger.setLevel(logging.WARNING)
        case "Error":
            defs.logger.setLevel(logging.ERROR)
        case "Critical":
            defs.logger.setLevel(logging.CRITICAL)
    defs.logger.info("Setting log level to " + level)

def on_closing():
    defs.logger.info("Confirming quit")
    defs.confiriming_quit = True
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        close()
    defs.confiriming_quit = False

def close():
    defs.logger.info("Quitting")
    defs.cancel_request = True
    if executor is not None:
        executor.shutdown(wait=False, cancel_futures=True)
    ui.root.destroy()

def start():
    try:
        path = ui.dir_path.get()
        if not Path(path).exists() or path == '':
            raise ValueError
        defs.basepath = path

        def run_main():
            try:
                main()
                ui.root.after(0, lambda: messagebox.showinfo("Done", "Formatting complete!"))
            except PermissionError:
                ui.root.after(0, lambda: messagebox.showerror("Insufficient permissions", "Please run with elevated permission level"))
            except FileExistsError:
                ui.root.after(0, lambda: messagebox.showerror("Unable to verify permision level", "Unable to verify permision level, please try again"))
            except SystemExit:
                return
            except Exception:
                ui.root.after(0, lambda: messagebox.showerror("Unknown Error, quitting"))
                ui.root.after(0, close)
                return
            
            defs.logger.info("Formatting completed")
            
            ui.run_button["state"] = NORMAL
            ui.json_check["state"] = NORMAL
            ui.dir_button["state"] = NORMAL
            ui.log_select["state"] = NORMAL
            
            ui.progress_bar.grid_remove()
            if(defs.display_message_box):
                ui.message_box.grid_remove()
            ui.dir_path_entry.grid(column=2, row=2, sticky=(E + W))

        def update_progress_bar():
            ui.progress_bar["value"] = defs.percent_complete * 100
            if defs.percent_complete < 0.999 and not defs.cancel_request:
                ui.root.after(500, update_progress_bar)
        
        ui.run_button["state"] = DISABLED
        ui.json_check["state"] = DISABLED
        ui.dir_button["state"] = DISABLED
        ui.log_select["state"] = DISABLED
        
        ui.dir_path_entry.grid_remove()
        # grid the message box and its scrollbars
        if(defs.display_message_box):
            ui.message_box.grid(column=2, row=1, columnspan=3, sticky=(N + S + E + W))
        ui.progress_bar.grid(column=2, row=2, sticky=(E + W))
        ui.progress_bar["value"] = 0
        
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        executor.submit(run_main)
        update_progress_bar()
    except ValueError:
        defs.logger.warning("Invalid Path")
        messagebox.showerror("Invalid path", "Please enter a valid path")
        return

if __name__ == "__main__":
    #defs.init()
    ui = user_interface()
    ui.dir_path_entry.focus()
    ui.root.mainloop()