import requests
import queue
import sys
import time

queue_results = queue.Queue()

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
    loop_test(loop_times=3)