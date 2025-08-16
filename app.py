import defs, logging, concurrent.futures
from tkinter import W, E, S, N, messagebox, filedialog, ttk, Tk, StringVar, DISABLED, ACTIVE, NORMAL
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

        def run_main():
            try:
                main()
                root.after(0, lambda: messagebox.showinfo("Done", "Formatting complete!"))
            except PermissionError:
                root.after(0, lambda: messagebox.showerror("Insufficient permissions", "Please run with elevated permission level"))
            except Exception:
                logger.fatal("Unknown error, quitting")
                root.after(0, lambda: messagebox.showerror("Unknown Error, quitting"))
                root.after(0, root.destroy)
            run_button["state"] = NORMAL
            json_check["state"] = NORMAL
            dir_button["state"] = NORMAL
            dir_path_entry["state"] = NORMAL

        run_button["state"] = DISABLED
        json_check["state"] = DISABLED
        dir_button["state"] = DISABLED
        dir_path_entry["state"] = DISABLED
        
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        executor.submit(run_main)
    except ValueError:
        logger.error("Invalid Path")
        messagebox.showerror("Invalid path", "Please enter a valid path")
        return

defs.init()
if defs.log_out != "":
    logging.basicConfig(filename=defs.log_out, level=logging.INFO)

root = Tk()
root.title("Music folder formatter")
root.resizable(False, False)

mainframe:ttk.Frame = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N + W + E + S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

dir_path = StringVar()
dir_path_entry = ttk.Entry(mainframe, width=50, textvariable=dir_path)
dir_path_entry.grid(column=2, row=1, sticky=(W + E))

dir_button = ttk.Button(mainframe, text="Choose Directory", command=get_path)
dir_button.grid(column=3, row=1, sticky=(W + E))

log_check = ttk.Checkbutton(mainframe, text="Output logs")

json_var = StringVar()
json_check = ttk.Checkbutton(mainframe, text="Generate JSON", command=switch_json, variable=json_var)
json_check.grid(column=2, row=2, sticky=(W))

run_button = ttk.Button(mainframe, text="Run", command=start)
run_button.grid(column=2, row=3, sticky=(S + W))

close_button = ttk.Button(mainframe, text="Close", command=root.destroy)
close_button.grid(column=3, row=3, sticky=(S + E))

dir_path_entry.focus()

root.mainloop()