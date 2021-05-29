from subprocess import call

import boto3
import cv2
import numpy as np

coco_names = ['person', 'bicycle', 'car', 'motorbike', 'aeroplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
              'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
              'elephant', 'bear',
              'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',
              'sports ball',
              'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle',
              'wine glass', 'cup', 'fork',
              'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog',
              'pizza', 'donut', 'cake',
              'chair', 'sofa', 'pottedplant', 'bed', 'diningtable', 'toilet', 'tvmonitor', 'laptop', 'mouse', 'remote',
              'keyboard', 'cell phone',
              'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
              'hair drier', 'toothbrush']


def lambda_handler(event, context):
    if event:

        # clear the files already in tmp f
        call('rm -rf /tmp/*', shell=True)

        # set up s3 service parameters to get the files
        s3_client = boto3.client('s3')
        uploadBucket = 'angularuploadtest'
        # Get the object from the event and show its content type
        bucket = event['Records'][0]['s3']['bucket']['name']
        # key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        file_obj = event["Records"][0]
        filename = str(file_obj['s3']['object']['key'])
        # print('filename: ',filename)

        params = {
            'Bucket': uploadBucket,
            'Key': filename
        }

        s3_url = s3_client.generate_presigned_url('get_object', Params=params)
        s3_url_main = s3_url.split("?")
        # print(s3_url_main)

        # get the uploaded file and convert to np array
        fileObj = s3_client.get_object(Bucket=uploadBucket, Key=filename)
        file_content = fileObj["Body"].read()
        np_array = np.fromstring(file_content, np.uint8)
        image_np = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED)
        image = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

        print("reading file from s3")

        cocoFile = s3_client.get_object(Bucket='yoloconfigbucket', Key='coco.names')
        cocoFileContent = cocoFile['Body'].read().decode('utf-8')

        # weightsFile = s3_client.get_object(Bucket = 'yoloconfigbucket', Key = 'yolov3-tiny.weights')
        # weightsFileContent = weightsFile['Body'].read()

        # cfgFile = s3_client.get_object(Bucket = 'yoloconfigbucket', Key = 'yolov3-tiny.cfg')
        # cfgFileContent = cfgFile['Body'].read().decode('utf-8')

        print('downloading config files from s3')
        temp_local_path_weights = '/tmp/yolov3-tiny.weights'
        temp_local_path_cfg = '/tmp/yolov3-tiny.cfg'
        s3_client.download_file('yoloconfigbucket', 'yolov3-tiny.weights', temp_local_path_weights)
        s3_client.download_file('yoloconfigbucket', 'yolov3-tiny.cfg', temp_local_path_cfg)

        net = cv2.dnn.readNet('/tmp/yolov3-tiny.cfg', '/tmp/yolov3-tiny.weights')
        # print(net)
        ln = net.getLayerNames()
        ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        # print(ln)

        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        # print(blob)

        net.setInput(blob)

        layerOutputs = net.forward(ln)

        # print(layerOutputs)

        classIDs = []
        confidences = []

        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > 0.3:
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        objects = []
        length = len(classIDs)
        for i in range(length):
            objects.append(str(coco_names[classIDs[i]]))

        print(objects)

        # clear the tmp folder for next use
        call('rm -rf /tmp/*', shell=True)

        # data = {}
        # data['url'] = {'S': s3_url_main[0]}

        # i=1

        # for each in objects:
        #     print(each)
        #     data["Objects"+str(i)] = {'S': each}
        #     print(data)
        #     i=i+1
        #     print(i)

        # try:
        #     response = s3.get_object(Bucket=bucket, Key=key)
        #     print("CONTENT TYPE: " + response['ContentType'])
        #     return response['ContentType']
        # except Exception as e:
        #     print(e)
        #     print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        #     raise e
