## About
A service for storing images with annotations. Features:
1. Uploading and downloading of files
1. Annotations updating and retrieving (in 2 formats)

## Start
Run `docker-compose up`

## Ideas
1. Storing files in Minio storage, because it's Amazon S3 compatible and overall better than default file system storage
1. Created a separate model for labels to ensure better validation of input data and to make it more agile to edit labels.
    Also it makes the table more sparse compared to storing everything in JSONField
1. Using file names as IDs for retrieving/updating annotations and retrieving images, 
    because it's more verbose and convenient for clients to use

## Assumptions
1. Because we need to be able to fetch image files using URLs like `<url>/my_image.jpg`, 
    I assume that names of files that we upload need to be unique across all files that were uploaded already. 
    
    **That's why we'll be using filename as an ID for fetching annotations or image files**
1. I assume that a structure of image annotation is clearly defined and goes as follows:
```json
{
  "labels": [
    {
      "id": "5b0cd508-587b-493b-98ea-b08a8c31d575",
      "class_id": "tooth",
      "surface": [
        "B",
        "O",
        "L"
      ],
      "shape": {
        "endX": 983,
        "endY": 1399,
        "startY": 605,
        "startX": 44
      },
      "meta": {
        "confirmed": false,
        "confidence_percent": 0.99
      }
    }
  ]
}
```

## API description

#### POST /api/v1/images/
Used to upload files with or without annotation

+ Request
        
        POST /api/v1/images/
         
+ Headers

        Content-Type=multipart/form-data
        
+ Body

        file=<file-object>,
        data={"annotation": {"labels": [...]}}
       
+ Response 201

        {"id": "sample.png"}
        
#### GET /api/v1/images/<str:file>/
Used to download files

+ Request
        
        GET /api/v1/images/<str:file>/
       
+ Response 200

        <file-object>
  
#### GET /api/v1/images/<str:image__file>/annotation/
Used to retrieve annotations.

Use parameter `format` for different representations. `format=export` shows only labels with `meta.confirmed=true`

+ Request
        
        GET /api/v1/images/sample.jpg/annotation/?format=internal
       
+ Response 200

        {
            "labels": [
                {
                    "id": "2b1cd508-587b-493b-98ea-b08a8c31d111",
                    "class_id": "tooth",
                    "surface": [
                        "1",
                        "2",
                        "3"
                    ],
                    "shape": {
                        "endX": 111,
                        "endY": 1399,
                        "startY": 605,
                        "startX": 44
                    },
                    "meta": {
                        "confirmed": true,
                        "confidence_percent": 0.99
                    }
                }
            ]
        }

+ Request
        
        GET /api/v1/images/sample.jpg/annotation/?format=export
       
+ Response 200

        {
            "labels": [
                {
                    "id": "2b1cd508-587b-493b-98ea-b08a8c31d111",
                    "class_id": "tooth",
                    "surface": "123",
                }
            ]
        }


#### PUT /api/v1/images/<str:image__file>/annotation/
Used to updated annotations information

+ Request
        
        PUT /api/v1/images/sample.jpg/annotation/
        
+ Body

        {
            "labels": [
                {
                    "id": "11111111-587b-493b-98ea-b08a8c31d111",
                    "class_id": "tooth2",
                    "meta": {
                        "confirmed": false,
                        "confidence_percent": 0.99
                    }
                }
            ]
        }
       
+ Response 200

        {
            "labels": [
                {
                    "id": "11111111-587b-493b-98ea-b08a8c31d111",
                    "class_id": "tooth2",
                    "surface": [],
                    "shape": {},
                    "meta": {
                        "confirmed": false,
                        "confidence_percent": 0.99
                    }
                }
            ]
        }


