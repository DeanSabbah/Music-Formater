import defs, logging
from tkinter import W, E, S, N, messagebox, filedialog, ttk, Tk, StringVar
from pathlib import Path
from model import main

logger = logging.getLogger(__name__)

def switch_json():
    defs.json = not defs.json

def get_path():
    try:
        dir_path.set(filedialog.askdirectory())
    except:
        pass
        

def start():
    try:
        path = dir_path.get()
        if not Path(path).exists() or path == '':
            raise ValueError
        path = path.replace('/', '\\')
        defs.basepath = path
        try:
            main()
        except PermissionError:
            messagebox.showerror("Insufficient permissions", "Please run with elevated permission level")
            return
        except Exception:
            messagebox.showerror("Unkown Error, quitting")
            root.destroy()
            return
    except ValueError:
        logger.error("Invalid Path")
        messagebox.showerror("Invalid path", "Please enter a valid path")
        return

defs.init()
if defs.log_out != "":
    logging.basicConfig(filename=defs.log_out, level=logging.INFO)

root = Tk()
root.title("Music folder formatter")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S)) # type: ignore
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

dir_path = StringVar()
dir_path_entry = ttk.Entry(mainframe, width=50, textvariable=dir_path)
dir_path_entry.grid(column=2, row=1, sticky=(W, E)) # type: ignore

dir_button = ttk.Button(mainframe, text="Choose Directory", command=get_path).grid(column=3, row=1, sticky=(W, E)) # type: ignore

log_check = ttk.Checkbutton(mainframe, text="Output logs")

json_check = ttk.Checkbutton(mainframe, text="Generate JSON", command=switch_json).grid(column=2, row=2, sticky=(W))

run_button = ttk.Button(mainframe, text="Run", command=start).grid(column=2, row=3, sticky=(S, W)) # type: ignore

close_button = ttk.Button(mainframe, text="Close", command=root.destroy).grid(column=3, row=3, sticky=(S, E)) # type: ignore

dir_path_entry.focus()

root.mainloop()