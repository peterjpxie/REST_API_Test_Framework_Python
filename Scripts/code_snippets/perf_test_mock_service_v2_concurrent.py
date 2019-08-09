import requests
import threading
import queue
import sys
import time

# Global variables
queue_results = queue.Queue()
start_time = 0

# 
# # request per seconds
# rps_mean = 0
# total_tested_requests = 0 
# total_tested_time = 0 
# total_pass_requests = 0
# 
# # time per request
# tpr_min = 999
# tpr_mean = 0
# tpr_max = 0
# sum_response_time = 0
# 
# # failures
# total_fail_requests = 0      
# total_exception_requests = 0  
# 
# # event flag to set and check test time is up.
# event_time_up = threading.Event()
# 
# timer = None

def test_mock_service():
    url = 'http://127.0.0.1:5000/json'    
    resp = requests.get(url)
    # Convert assert for functional tests to validate for performance tests so it won't stop on a test failure. 
    # assert resp.status_code == 200
    # assert resp.json()["code"] == 1
    if resp.status_code != 200:
        print('Test failed with response status code %s.' % resp.status_code )
        return 'fail', resp.elapsed.total_seconds()
    elif resp.json()["code"] != 1:
        print('Test failed with code %s != 1.' %  resp.json()["code"] )
        return 'fail', resp.elapsed.total_seconds()
    else:
        print('Test passed.')
        return 'pass', resp.elapsed.total_seconds()

def loop_test(loop_wait=0, loop_times=sys.maxsize):
        """
        loop test of some APIs for performance test purpose.  

        Parameters:
        loop_wait   wait time between two loops.
        loop_times  number of loops, default indefinite
        """
        looped_times = 0
        
        while looped_times < loop_times:            
            # run an API test
            test_result, elapsed_time = test_mock_service()           
            # put results into a queue for statistics
            queue_results.put(['test_mock_service', test_result, elapsed_time])
            
            # You can add more API tests in a loop here.
            
            looped_times += 1
            time.sleep(loop_wait)
    
if __name__ == '__main__':
    ### Test Settings ###
    concurrent_users = 2
    loop_times = 3
    # test_time = 3600 # time in seconds, e.g. 36000
    # stats_interval = 2
    
    workers = []
    start_time = time.time()
    print('Tests started at %s.' % start_time )
    
    # start concurrent user threads
    for i in range(concurrent_users):
        thread = threading.Thread(target=loop_test, kwargs={'loop_times': loop_times}, daemon=True)         
        thread.start()
        workers.append(thread)
    
    # # start timer 
    # perf_test.start_timer(test_time)
    
    # # start stats thread
    # stats_thread = Thread(target=perf_test.loop_stats, args=[stats_interval], daemon=True)
    # stats_thread.start()

    # Block until all threads finish.
    for w in workers:
        w.join()       
        
    # # clean up
    # # stop timer if loop_times is reached first.
    # perf_test.cancel_timer()
    
    end_time = time.time()
    
    # # Ensure to execute the last statistics:
    # perf_test.stats()

    print('\nTests ended at %s.' % end_time )
    print('Total test time: %s seconds.' %  (end_time - start_time) )