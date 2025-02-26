import os
import threading
import time

def worker_func(label, parent_thread_name):
    pid = os.getpid()
    current_name = threading.current_thread().name
    current_tid = threading.get_native_id()

    print(f"[Child '{label}'] PID={pid}, TID={current_tid}, "
          f"ThreadName={current_name}, spawned by {parent_thread_name}")

    for i in range(2):
        print(f"[Child '{label}'] iteration {i}")
        time.sleep(1)

    print(f"[Child '{label}'] finished.")

def main():
    main_pid = os.getpid()
    main_thread_name = threading.current_thread().name
    main_tid = threading.get_native_id()

    print(f"MAIN START: PID={main_pid}, TID={main_tid}, ThreadName={main_thread_name}")

    t1 = threading.Thread(
        target=worker_func,
        args=("ChildA", main_thread_name),
        name="MyWorker-1"
    )
    t1.start()
    t1.join()

    print("MAIN END")


if __name__ == "__main__":
    main()
