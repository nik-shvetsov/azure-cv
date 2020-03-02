# -*- coding: utf-8 -*-\

import time
import requests
import cv2
import numpy as np
import os
import sys
import json as jl

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# REST API Requirements
# Request body: Image in the JPEG, PNG or BMP format with size less than 4MB
# and dimensions at least 40×40, at most 3200×3200.
# Request parameters: It is a dictionary of a single boolean parameter with
# key ‘handwriting’. If it is set to True or is not specified, handwriting
# recognition is performed. If “false” is specified, printed text recognition
# is performed by calling OCR operation.
# Request headers: It is a dictionary of two parameters. 1- ‘Content-Type’
# (optional) which tells the string media type of the body sent to the API.
# 2- ‘Ocp-Apim-Subscription-Key’ is the subscription key which provides access
# to this API.
# Request URL: It is the URL for your location.


# Process request from Azure
def process_request(json, data, headers, params, url):
    """
    Input parameters:
    json: JSON object
    data: Image data object
    headers: subscription key and data type requests
    params: boolean object for handwriting or printed text
    """

    retries = 0
    result = None

    while (True):
        response = requests.request('post', url, json=json, data=data,
                                    headers=headers, params=params)
        if response.status_code == 429:
            print(f"Message: {response.json()}")
            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break
        elif response.status_code == 202:
            result = response.headers['Operation-Location']
        else:
            print(f"Error code: {response.status_code}")
            print(f"Message: {response.json()}")
        break
    return result


# Get text result
def get_ocr_text_result(operationLocation, headers):
    """
    Parameters:
    operationLocation: operationLocation to get text result
    headers: for subscription key
    """

    retries = 0
    result = None

    while True:
        response = requests.request('get', operationLocation, json=None,
                                    data=None, headers=headers, params=None)
        if response.status_code == 429:
            print(f"Message: {response.json()}")
            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print("Error: failed after retrying!")
                break
        elif response.status_code == 200:  # Service has accepted request
            result = response.json()
        else:
            print(f"Error code: {response.status_code}")
            print(f"Message: {response.json()}")
        break

    return result


def show_result_on_image(result, img, save_path):
    """
    Display obtained results onto the input images
    """
    img = img[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(img, aspect='equal')

    lines = result['recognitionResult']['lines']

    for i in range(len(lines)):
        words = lines[i]['words']
        for j in range(len(words)):
            tl = (words[j]['boundingBox'][0], words[j]['boundingBox'][1])
            tr = (words[j]['boundingBox'][2], words[j]['boundingBox'][3])
            br = (words[j]['boundingBox'][4], words[j]['boundingBox'][5])
            bl = (words[j]['boundingBox'][6], words[j]['boundingBox'][7])
            text = words[j]['text']
            x = [tl[0], tr[0], tr[0], br[0], br[0], bl[0], bl[0], tl[0]]
            y = [tl[1], tr[1], tr[1], br[1], br[1], bl[1], bl[1], tl[1]]
            line = Line2D(x, y, linewidth=3.5, color='red')
            ax.add_line(line)
            ax.text(tl[0], tl[1]-2, f'{text}', bbox=dict(
                facecolor='blue', alpha=0.5), fontsize=14, color='white')

    plt.axis('off')
    plt.tight_layout()
    plt.draw()
    plt.savefig(save_path, bbox_inches='tight')
    # plt.show()


def process(data_name, key, url):
    path = os.path.normpath(sys.path[0] + '/input/' + data_name)
    for root, dirs, files in os.walk(path):
        for file in files:
            image_path = os.path.join(root, file)
            with open(image_path, 'rb') as f:
                data = f.read()

            params = {'mode': 'Handwritten'}
            headers = dict()
            headers['Ocp-Apim-Subscription-Key'] = key
            headers['Content-Type'] = 'application/octet-stream'
            json = None
            operationLocation = process_request(json, data, headers,
                                                params, url)

            result = None
            if (operationLocation is not None):
                while (True):
                    time.sleep(1)
                    result = get_ocr_text_result(operationLocation, headers)
                    if result['status'] == 'Succeeded' or \
                            result['status'] == 'Failed':
                        break
            if result is not None and result['status'] == 'Succeeded':
                data8uint = np.frombuffer(data, np.uint8)
                img = cv2.cvtColor(cv2.imdecode(data8uint, cv2.IMREAD_COLOR),
                                   cv2.COLOR_BGR2RGB)
                result_path = os.path.normpath(sys.path[0] + '/output/' +
                                               data_name)
                #  os.path.join(root, 'proc_' + file)

                if not os.path.exists(result_path):
                    os.makedirs(result_path)
                show_result_on_image(result, img,
                                     os.path.join(result_path,
                                                  os.path.splitext(file)[0] +
                                                  '_proc'))
                with open(os.path.join(result_path, os.path.splitext(file)[0] +
                                       '_response.json'), 'w') as jf:
                    jf.write(jl.dumps(result))
                print("Done " + file)


if __name__ == '__main__':
    _url = 'https://northeurope.api.cognitive.microsoft.com/vision/v2.0/RecognizeText'
    _key = ''
    _maxNumRetries = 10
    data_name = ''
    process(data_name, _key, _url)
