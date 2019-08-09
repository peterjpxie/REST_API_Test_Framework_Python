# module imports - omitted
# Global variables - omitted

# event flag to set and check test time is up.
event_time_up = threading.Event()

# def test_mock_service(): - omitted
def loop_test(loop_wait=0, loop_times=sys.maxsize):
    looped_times = 0        
    while (looped_times < loop_times 
        and not event_time_up.is_set()):          
        test_result, elapsed_time = test_mock_service()           
        queue_results.put(['test_mock_service', test_result, elapsed_time])
        looped_times += 1
        time.sleep(loop_wait)
        
#def stats(): - omitted   
def set_event_time_up():
    if not event_time_up.is_set():
        event_time_up.set()
        
if __name__ == '__main__':        
    ### Test Settings ###
    concurrent_users = 2
    loop_times = 100
    test_time = 5 # time in seconds, e.g. 36000
    
    workers = []
    start_time = time.time()
    print('Tests started at %s.' % start_time ) 
    
    # start concurrent user threads
    for i in range(concurrent_users):
        thread = threading.Thread(target=loop_test, kwargs={'loop_times': loop_times}, daemon=True)         
        thread.start()
        workers.append(thread)
    
    # set a timer to stop testing
    timer = threading.Timer(test_time, set_event_time_up)
    timer.start()

    # Block until all threads finish.
    for w in workers:
        w.join()       
        
    # stop timer if loop_times is reached first.
    if not event_time_up.is_set():
        timer.cancel()
    
    end_time = time.time()
    stats()
    print('\nTests ended at %s.' % end_time )
    print('Total test time: %s seconds.' %  (end_time - start_time) )