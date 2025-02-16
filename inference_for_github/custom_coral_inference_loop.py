import numpy as np
import tflite_runtime.interpreter as tflite
import os
import time
import platform
import argparse

_EDGETPU_SHARED_LIB = {
  'Linux': 'libedgetpu.so.1',
  'Darwin': 'libedgetpu.1.dylib',
  'Windows': 'edgetpu.dll'
}[platform.system()]

parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
      '-m', '--model', required=True, help='File path of .tflite file.')

args = parser.parse_args()

model_path = args.model

if 'edgetpu.tflite'  in model_path:
    interpreter = tflite.Interpreter(
        model_path=model_path, experimental_delegates=[tflite.load_delegate(_EDGETPU_SHARED_LIB,  {})])
else:
    interpreter = tflite.Interpreter(model_path=model_path)

interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_shape = input_details[0]['shape']
for i in range(1, 70):
    filename = "CHNCXR_00{}_0".format(str(i).zfill(2))
    input_data = np.load("image_numpy/{}.npy".format(filename))
    input_data=np.float32(input_data)
    input_data=np.array(input_data).reshape(1,128,128,1)
    interpreter.set_tensor(input_details[0]['index'], input_data)

    inference_time = 0
    count = 100
    for i in range(count):
        start = time.perf_counter()
        interpreter.invoke()
        inference_time += time.perf_counter() - start
    print('%.2f ms' % (inference_time * 1000/count))

    output_data = interpreter.get_tensor(output_details[0]['index'])
    output_img=output_data[0,:,:,0]
    np.save("result_numpy/{}_result.npy".format(filename), output_img)