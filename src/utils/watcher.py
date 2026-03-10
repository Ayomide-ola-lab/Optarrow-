import logging
import multiprocessing
import time

def monitor_processes(processes_dict,):
    """Watches for status of a series of subprocesses

    Args:
        processes_dict (dict): a dict holding processes and their names.
        is_end (bool): is the procedure terminated
        format like this:
        {
            "name": (<proc object>, <worker object>, is_daemon)
        }
    """
    logger = logging.getLogger("monitor")
    logger.info(f"[Monitor] Monitor started.")
    while True:
        for name, item in list(processes_dict.items()):
            proc, worker, is_daemon = item
            if proc.exitcode is not None and proc.exitcode != 0:
                logger.info(f"[Monitor] Process {name} (PID {proc.pid}) died. Restarting...")
                new_proc = multiprocessing.Process(target=worker, daemon=is_daemon)
                new_proc.start()
                processes_dict[name] = (new_proc, worker, is_daemon)
        time.sleep(2)  # check every 2 seconds