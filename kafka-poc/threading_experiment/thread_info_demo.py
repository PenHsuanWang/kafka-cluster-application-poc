import os
import threading
import time


def worker_func(thread_label):
    """
    Worker function that prints the current process ID, the current
    thread's name, and native thread ID (if available in Python 3.8+).
    """
    # The same process ID for all threads in this Python process
    pid = os.getpid()

    # The Python-level name for the current thread
    current_thread_name = threading.current_thread().name

    # The OS-level native thread ID (Python 3.8+).
    # If you're on older Python, you can comment this out or use threading.get_ident().
    native_tid = threading.get_native_id()

    for i in range(3):
        print(f"[PID={pid}, NativeTID={native_tid}, ThreadName={current_thread_name}] "
              f"{thread_label} iteration {i}")
        time.sleep(1)

    print(f"[PID={pid}, NativeTID={native_tid}, ThreadName={current_thread_name}] "
          f"{thread_label} finished.")


def main():
    # Print info about the main thread
    pid = os.getpid()
    main_thread_name = threading.current_thread().name
    native_tid_main = threading.get_native_id()
    print(f"MAIN START: [PID={pid}, NativeTID={native_tid_main}, ThreadName={main_thread_name}]")

    # Create two worker threads
    t1 = threading.Thread(
        target=worker_func,
        args=("ChildThread-1",),
        name="MyWorker-1"  # We can explicitly name the thread if we wish
    )
    t2 = threading.Thread(
        target=worker_func,
        args=("ChildThread-2",),
        name="MyWorker-2"
    )

    # Start the threads
    t1.start()
    t2.start()

    # Wait for them to finish
    t1.join()
    t2.join()

    print(f"MAIN END: [PID={pid}, NativeTID={native_tid_main}, ThreadName={main_thread_name}] "
          "All child threads have finished.")


if __name__ == "__main__":
    main()

