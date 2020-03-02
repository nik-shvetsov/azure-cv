# -*- coding: utf-8 -*-\

import os
import json
from pprint import pprint
import http.client
import urllib

# from azure.cognitiveservices.vision.customvision.training\
# import CustomVisionTrainingClient

# WARNING fixed site-packages/azure/cognitiveservices/vision/\
# customvision/training to support v1.0 endpoint (instead of 2.2)

# ./version.py
# ./custom_vision_training_client.py
#     - base_url = '{Endpoint}/customvision/v2.2/Training'
#     - self.api_version = '2.2'

##############################


class CVTClient:
    def __init__(self, project_name):
        self.current_project_id = None
        self.current_project_name = project_name
        self.training_key = ""
        self.prediction_key = ""
        # "https://southcentralus.api.cognitive.microsoft.com"
        self.api_region = "southcentralus.api.cognitive.microsoft.com"
        # self.img_folder = os.path.join(os.path.dirname(
        #                                os.path.realpath(__file__)), "images")
        self.img_folder = ""
        # self.trainer = CustomVisionTrainingClient(self.training_key,
        #                                           endpoint=f"https://{self.api_region}")
        self.actions = {'get_projects': ['GET', ''],
                        'create_project': ['POST', ''],
                        'delete_project': ['DELETE', ''],
                        'create_tag': ['POST', 'tags'],
                        'get_tags': ['GET', 'tags'],
                        'delete_tag': ['DELETE', 'tags'],
                        'get_domains': ['GET', ''],
                        'upload_image': ['POST', 'images/image'],
                        'train_project': ['POST', 'train'],
                        'get_iterations': ['GET', 'iterations'],
                        'quick_test': ['POST', 'quicktest/image'],
                        'quick_test_url': ['POST', 'quicktest/url'],
                        'pred_nostore': ['POST', 'image/nostore'],
                        'pred_url_nostore': ['POST', 'url/nostore'],
                        'pred_store': ['POST', 'image/'],
                        'pred_url_store': ['POST', 'url/']
                        }
        # headers template
        self.headers = {'Training-key': self.training_key,
                        'Prediction-key': self.prediction_key}
        self.domains = self.get_domains()
        self.projects_list = None

    def create_proj(self, name='None', description='default'):
        print("Creating project...")
        try:
            # self.trainer.create_project(self.current_project_name)
            # if name == None else self.trainer.create_project(name)
            params = {
                'name': name,
                'description': description,
                'domainId': self.get_domain_id('General')
            }
            data = self.cvtc_request('create_project', params=params)
            print(data)
        except Exception as e:
            print(e)

    def delete_project(self, projectID):
        try:
            self.cvtc_request('delete_project', projectID=projectID,
                              verbose=True)
        except Exception as e:
            print(e)

    def get_projects_list(self):
        self.projects_list = self.cvtc_request('get_projects')
        print(self.projects_list)

    def get_project_id(self, project_name=None):
        if self.projects_list is None:
            self.get_projects_list()
        if project_name is None:
            project_name = self.current_project_name
        data = self.projects_list
        if isinstance(data, dict):
            return data['Id']
        for item in data:
            for key, val in item.items():
                if val == project_name:
                    return item['Id']

    def get_projects_names(self):
        if self.projects_list is None:
            self.get_projects_list()
        data = self.projects_list
        result = []
        for item in data:
            for key, val in item.items():
                if key == "Name":
                    result.append(val)
        return (result)

    def get_domains(self):
        return (self.cvtc_request('get_domains', endpointDomain='domains'))

    def get_domain_id(self, name='General'):
        if self.domains is not None:
            for item in self.domains:
                if item['Name'] == name:
                    return item['Id']
        else:
            print("No domains found!")
            return (None)

    def create_tag(self, tag_name, description='', projectID=None):
        data = self.cvtc_request('create_tag',
                                 params={'name': tag_name,
                                         'description': description},
                                 projectID=projectID)
        print('Created: ', data)

    def delete_tag(self, tag_name, projectID=None):
        try:
            self.cvtc_request('delete_tag',
                              projectID=projectID,
                              id_params={'Id': self.get_tag_id(tag_name)},
                              verbose=True)
        except Exception as e:
            print(e)

    def get_project_tags(self, project_name=None):
        projectID = self.current_project_id if project_name is None \
                    else self.get_project_id(project_name)
        data = self.cvtc_request('get_tags', projectID=projectID)
        return (data)

    def get_tag_id(self, tag_name, project_name=None):
        data = self.get_project_tags(project_name)
        tag_data = data['Tags']
        for item in tag_data:
            for key, val in item.items():
                if val == tag_name:
                    return item['Id']

    def upload_image(self, data_img, tag_name, projectID=None):
        tag_id = self.get_tag_id(tag_name)
        data = self.cvtc_request('upload_image',
                                 headers={'Content-Type':
                                          'application/octet-stream'},
                                 params={'TagIds': tag_id},
                                 data=data_img.read())
        print('Created: ', data)

    def upload_directory(self, dir, tag_name):
        path = os.path.join(self.img_folder, dir)
        for image_name in os.listdir(path):
            with open(os.path.join(path, image_name), mode="rb") as img_data:
                self.upload_image(img_data, tag_name)

    def train_project(self, projectID=None, verbose=True):
        if projectID is None:
            projectID = self.current_project_id
        try:
            resp = self.cvtc_request('train_project', projectID=projectID)
            if (verbose):
                print(resp)
        except Exception as e:
            print(e)

    def get_iterations(self, projectID=None):
        if projectID is None:
            projectID = self.current_project_id
        data = self.cvtc_request('get_iterations', projectID=projectID)
        return (data)

    def get_completed_iteration_id(self, projectID=None, verbose=True):
        if projectID is None:
            projectID = self.current_project_id
        iter_data = self.get_iterations(projectID)
        for item in reversed(iter_data):
            if item['Status'] == 'Completed':
                if (verbose):
                    print(f"{item['Name']} - {item['Id']}")
                return item['Id']

    def quick_test_image(self, img_data, projectID, iterationID):
        data = self.cvtc_request('quick_test',
                                 projectID=projectID,
                                 headers={'Content-Type':
                                          'application/octet-stream'},
                                 params={'iterationId': iterationID},
                                 data=img_data.read())
        return (data)

    def quick_test_image_url(self, url, projectID, iterationID):
        data = self.cvtc_request('quick_test_url',
                                 projectID=projectID,
                                 headers={'Content-Type': 'application/json'},
                                 params={'iterationId': iterationID},
                                 data=json.dumps({'Url': url}))
        return (data)

    def parse_results_pred(self, data):
        results = data['Predictions']
        res = []
        for item in results:
            res.append(f"{item['Tag']} - {item['Probability']}")
        return (res)

    def predict_image(self, img_data, projectID, iterationID, store=False):
        key = 'pred_store' if store else 'pred_nostore'
        data = self.cvtc_pred_request(key,
                                      projectID=projectID,
                                      data=img_data.read(),
                                      headers={'Content-Type':
                                               'application/octet-stream'},
                                      params={'iterationId': iterationID})
        return (data)

    def predict_url(self, url, projectID, iterationID, store=False):
        key = 'pred_url_store' if store else 'pred_url_nostore'
        data = self.cvtc_pred_request(key,
                                      projectID=projectID,
                                      data=json.dumps({'Url': url}),
                                      headers={'Content-Type':
                                               'application/json'},
                                      params={'iterationId': iterationID})
        return (data)

    def cvtc_pred_request(self, action_key, projectID, data=None, headers={},
                          params={}, id_params=None, verbose=False):

        params = urllib.parse.urlencode(params)
        try:
            conn = http.client.HTTPSConnection(self.api_region)
            action = self.actions[action_key]
            endpoint = f"/customvision/v1.1/Prediction/{projectID}"
            # act = action[1]
            endpoint = endpoint + f"/{action[1]}?{params}"

            if data is None:
                data = "{body}"
            if (verbose):
                print(f"{action[0]}, {endpoint}, body={data}, {headers},\
                      {self.headers}")
            conn.request(action[0], endpoint, body=data,
                         headers={**headers, **self.headers})
            response = conn.getresponse()
            data = json.loads(response.read())
            conn.close()
            if (verbose):
                pprint(data)
            return (data)
        except Exception as e:
            print(e)

    def cvtc_request(self, action_key, headers={}, params={}, projectID=None,
                     data=None, endpointDomain='projects', description=None,
                     id_params=None, verbose=False):
        # id_params may include tag_id, iteration_id
        params = urllib.parse.urlencode(params)
        try:
            if (projectID is None):
                projectID = self.current_project_id
            if description is None:
                description = f"{action_key} {headers} {params} {projectID}"
            if (verbose):
                print(f'Sending request: {description}')
            conn = http.client.HTTPSConnection(self.api_region)
            action = self.actions[action_key]
            endpoint = f"/customvision/v1.1/Training/{endpointDomain}"

            if (projectID is not None):
                if (action[1] != ''):
                    # act = action[1]
                    if id_params is not None:
                        endpoint = endpoint + f"/{projectID}/{action[1]}/\
                                               {id_params['Id']}?{params}"
                    else:
                        endpoint = endpoint + f"/{projectID}/{action[1]}\
                                                ?{params}"
                else:
                    endpoint = endpoint + f"/{projectID}?{params}"
            else:
                endpoint = endpoint + f"?{params}"

            if data is None:
                data = "{body}"
            if (verbose):
                print(f"{action[0]}, {endpoint}, body={data},\
                      {headers}, {self.headers}")
            conn.request(action[0], endpoint, body=data,
                         headers={**headers, **self.headers})
            response = conn.getresponse()
            data = json.loads(response.read())
            conn.close()
            if (verbose):
                pprint(data)
            return (data)
        except Exception as e:
            print(e)
