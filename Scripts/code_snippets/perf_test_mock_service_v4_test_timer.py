import requests
import threading
import queue
import sys
import time

# Global variables
queue_results = queue.Queue()
start_time = 0
# event flag to set and check test time is up.
event_time_up = threading.Event()

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
        # print('Test passed.')
        return 'pass', resp.elapsed.total_seconds()

def set_event_time_up():
    if not event_time_up.is_set():
        event_time_up.set()           
            
def loop_test(loop_wait=0, loop_times=sys.maxsize):
    looped_times = 0        
    while (looped_times < loop_times 
        and not event_time_up.is_set()):          
        # run an API test
        test_result, elapsed_time = test_mock_service()           
        # put results into a queue for statistics
        queue_results.put(['test_mock_service', test_result, elapsed_time])
        
        # You can add more API tests in a loop here.
        looped_times += 1
        time.sleep(loop_wait)

def stats():
    # request per second
    rps_mean = 0
    total_tested_requests = 0
    total_pass_requests = 0
    
    # time per request
    tpr_min = 999
    tpr_mean = 0
    tpr_max = 0
    sum_response_time = 0
    
    # failures
    total_fail_requests = 0      
    total_exception_requests = 0  

    global start_time
    end_time = time.time()
    # get the approximate queue size
    qsize = queue_results.qsize()
    loop = 0
    for i in range(qsize):
        try:
            result=queue_results.get_nowait()
            loop +=1
        except Empty:
            break
        # calc stats
        if result[1] == 'exception':
            total_exception_requests += 1
        elif result[1] == 'fail':
            total_fail_requests += 1
        elif result[1] == 'pass':
            total_pass_requests += 1
            sum_response_time += result[2]
            # update min and max time per request
            if result[2] < tpr_min:
                tpr_min = result[2]
            if result[2] > tpr_max:
                tpr_max = result[2]
        
    total_tested_requests += loop
    
    # time per requests - mean (avg)
    if total_pass_requests != 0:
        tpr_mean = sum_response_time / total_pass_requests
    
    # requests per second - mean
    if start_time == 0:
        print('stats: start_time is not set, skipping rps stats.')
    else:
        tested_time = end_time - start_time
        rps_mean = total_pass_requests / tested_time
    
    # print stats
    print('\n-----------------Test Statistics---------------')
    print(time.asctime())
    print('Total requests: %s, pass: %s, fail: %s, exception: %s'
        % (total_tested_requests, total_pass_requests, total_fail_requests, total_exception_requests)
        )
    if total_pass_requests > 0:
        print('For pass requests:') 
        print('Request per Second - mean: %.2f' % rps_mean)
        print('Time per Request   - mean: %.6f, min: %.6f, max: %.6f' 
            % (tpr_mean, tpr_min, tpr_max) )            
    
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
    
    # Performance stats
    stats()

    print('\nTests ended at %s.' % end_time )
    print('Total test time: %s seconds.' %  (end_time - start_time) )