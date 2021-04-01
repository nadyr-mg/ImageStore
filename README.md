# ImageStore

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