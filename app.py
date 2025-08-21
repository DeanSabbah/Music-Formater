import defs, logging, concurrent.futures, traceback, time
from tkinter import W, E, S, N, messagebox, filedialog, ttk, Tk, StringVar, DISABLED, NORMAL
from pathlib import Path
from model import main

defs.logger.disabled = True

executor = None

def switch_json():
    defs.logger.info("Switching json to " + str(not defs.json))
    defs.json = not defs.json

def get_path():
    location = filedialog.askdirectory()
    defs.logger.info("Setting basepath to " + location)
    try:
        dir_path.set(location)
    except Exception:
        defs.logger.fatal("Unkown Error, Quitting\n" + traceback.format_exc())
        root.destroy()
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
    root.destroy()

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
            except SystemExit:
                return
            except Exception:
                defs.logger.fatal("Unknown error, quitting\n" + traceback.format_exc())
                root.after(0, lambda: messagebox.showerror("Unknown Error, quitting"))
                root.after(0, close)
            run_button["state"] = NORMAL
            json_check["state"] = NORMAL
            dir_button["state"] = NORMAL
            progress_bar.grid_remove()
            dir_path_entry.grid(column=2, row=1, sticky=(E + W))

        def update_progress_bar():
            while True:
                if defs.percent_complete == 1.0 or defs.cancel_request:
                    return
                progress_bar.step(defs.percent_complete * 100)
                time.sleep(0.5)
            
        
        run_button["state"] = DISABLED
        json_check["state"] = DISABLED
        dir_button["state"] = DISABLED
        dir_path_entry.grid_remove()
        progress_bar.grid(column=2, row=1, sticky=(E + W))
        progress_bar.step(0)
        
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        executor.submit(run_main)
        executor.submit(update_progress_bar)
    except ValueError:
        defs.logger.warning("Invalid Path")
        messagebox.showerror("Invalid path", "Please enter a valid path")
        return

defs.init()

root = Tk()
root.title("Music folder formatter")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_closing)

mainframe:ttk.Frame = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N + W + E + S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

dir_path = StringVar()
dir_path_entry = ttk.Entry(mainframe, width=50, textvariable=dir_path)
dir_path_entry.grid(column=2, row=1, sticky=(E + W))

progress_bar = ttk.Progressbar(mainframe, orient="horizontal", length=306, mode="determinate")

dir_button = ttk.Button(mainframe, text="Choose Directory", command=get_path)
dir_button.grid(column=4, row=1, sticky=(E))

log_label = ttk.Label(mainframe, text="Log level: ")
log_label.grid(column=3, row=2, sticky=(E))

log_choice = StringVar()
log_options = ["Off", "Debug", "Info", "Warning", "Error", "Critical"]
log_select = ttk.OptionMenu(mainframe, log_choice, "Off", *log_options, command=set_log_level)
log_select.grid(column=4, row=2, sticky=(W + E))

json_var = StringVar()
json_check = ttk.Checkbutton(mainframe, text="Generate JSON", command=switch_json, variable=json_var)
json_check.grid(column=2, row=2, sticky=(W))

run_button = ttk.Button(mainframe, text="Run", command=start)
run_button.grid(column=2, row=3, sticky=(S + W))

close_button = ttk.Button(mainframe, text="Close", command=on_closing)
close_button.grid(column=4, row=3, sticky=(S + E))

dir_path_entry.focus()

root.mainloop()