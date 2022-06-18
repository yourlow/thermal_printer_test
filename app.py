from escpos.printer import Usb
from escpos.constants import PAPER_PART_CUT

from flask import Flask, request
from flask.wrappers import Response
import json 

app = Flask(__name__)


@app.route("/", methods=["POST"])
def output():
    req = json.loads(request.get_data())
    

    print(req, flush=True)
    try:
        
        printer = Usb(idVendor=0x03f0, idProduct=0x0e69, in_ep=0x82, out_ep=0x02)
        
        printer.text(f"Load ID: {req['load_id']}\n")
        printer.text(f"Load Time: {req['timestamp']}\n")
        printer.text(f"Customer: {req['customer']['name']}\n")
        printer.text(f"Product: {req['product']['name']}\n")
        # printer.text(f"Hauler: {req['hauler']['name']}\n")
        # printer.text(f"Driver: {req['driver']['name']}\n")
        
        print("HELLo", flush=True)
        printer.text("--------------------------------\n")

        
        # for i in range(10):
            
        #     printer.text("\t FEED ME FEED ME FEED ME\n")
        #     printer._raw(bytes([10]))  
        printer._raw(bytes([10]))
        printer._raw(bytes([10]))
        printer._raw(bytes([10]))
        
        
        printer.image("./test_image.jpeg")
        printer._raw(bytes([10]))
        printer._raw(bytes([10]))
        printer._raw(bytes([10]))
        printer._raw(bytes([29, 86, 1, 19]))   
        
        return Response("good", status=200)
    except Exception as e:
        print(e, flush=True)




if __name__ == '__main__':

    app.run(host="0.0.0.0", port=9000, debug=True)
