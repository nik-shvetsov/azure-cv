# -*- coding: utf-8 -*-\

from cvs import CVTClient

if __name__ == "__main__":
    project_name = ""
    cvc = CVTClient(project_name)
    cvc.get_domains()
    # cvc.create_proj(project_name)
    cvc.current_project_id = cvc.get_project_id()
    # cvc.delete_project(cvc.get_project_id(project_name))
    # if project_name not in cvc.get_projects_names():
    #   cvc.create_proj(project_name)
    print('Project names: ', cvc.get_projects_names())
    print('Projects: \n', cvc.projects_list)
    print('Current project ID: ', cvc.current_project_id)
    # cvc.create_tag('tag_name', description = 'tag_description')
    # print(cvc.get_project_tags())
    # cvc.upload_directory("dir", "subdir")

    # path = os.path.join(cvc.img_folder, '')
    # for image_name in os.listdir(path):
    #     with open(os.path.join(path, image_name), mode="rb") as img_data:
    #         data = cvc.quick_test_image(img_data, cvc.get_project_id(),
    #                                     cvc.get_completed_iteration_id())
    #         print(image_name, cvc.parse_results_pred(data))

    # cvc.train_project(verbose=True)
    # pprint(cvc.get_iterations())
    # print(cvc.get_completed_iteration_id())

    # data = cvc.quick_test_image_url('https://*.jpg',
    #                                 cvc.get_project_id(),
    #                                 cvc.get_completed_iteration_id())
    # print(cvc.parse_results_pred(data))

    # with open(os.path.join(cvc.img_folder, 'Test', 'test_image.jpg'),
    #           mode="rb") as img_data:
    #     cvc.quick_test_image(img_data, cvc.get_project_id(),
    #     cvc.get_completed_iteration_id())

    ##############
    # Prediction API

    # with open(os.path.join(cvc.img_folder, 'Test', 'test_image.jpg'),
    #           mode="rb") as img_data:
    #     data = cvc.predict_image_no_store(img_data, cvc.get_project_id(),
    #                                       cvc.get_completed_iteration_id())
    #     print (cvc.parse_results_pred(data))

    # data = cvc.predict_url('https://*.jpg',
    #                        cvc.get_project_id(),
    #                        cvc.get_completed_iteration_id())
    # print(cvc.parse_results_pred(data))
