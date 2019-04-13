# A Restful API testing framework example

## Features:

* Common get/post function to 

        ** Print every request and response in a API output file
        ** Append common headers
        ** Take care of request exception and non-200 response codes and return None, so you only need to care normal json response.
        
* Use flask to mock service

* html report
    
## Install:

pip install -U pytest requests pytest-html ipdb

## Run:

pytest
