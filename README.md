# ambilabs-backend-coding

This API project is created to manage simple tasks.
That remind the user if the task will expired in 15 minutes,
there is an additional JSON field that indicate if the task will expired.
For further detail, please refer to `Coding Assessment.pdf`

This application supports:
1. Create single or bulk tasks
2. Read single or bulk tasks
3. Update single task
4. Delete single task

This application is written in Python programming language and SQLite to store the data.
This application is using Flask as the API framework and SQLAlchemy as the ORM.

The entire application is contain within `main.py` file.

`ambilabs_run.sh` is to run the `main.py`

## Install
    pip install -r requirements.txt

## Run the Program
    source ambilabs_run.sh

# REST API
To test the API import the `Ambilabs Coding Assessment.postman_collection.json` to your Postman

## Create Single Task

### Request
`POST /create_task`

    curl --location --request POST 'localhost:5000/create_task' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "task_id": "string (task_xxx)",
        "title": "string",
        "description": "string",
        "expired": "dd/mm/yyyy HH:mm"
    }'

### Response
`201 Created`

    {"result": "task_id task_001 has been added"}

`400 Bad Request`
either task_id, title, description, expired is not in the request body

    {"result": "Please fill all the task_id, title, description, and expired"}

if taskID / title & expired found in database

    {"result": "You have put this task suggest to update instead of create new"}

if task already expired

    {"result": "sorry but your task has already expired"}

## Create Bulk Tasks

### Request
`POST /create_bulk_tasks`

    curl --location --request POST 'localhost:5000/create_bulk_tasks' \
    --header 'Content-Type: application/json' \
    --data-raw '[
        {
            "task_id": "task_002",
            "title": "Do the ambilabs coding",
            "description": "Code the ambilabs assessment",
            "expired": "05/02/2021 15:30"
        },
        {
            "task_id": "task_003",
            "title": "Clean the house",
            "description": "DO the house chores",
            "expired": "06/02/2021 15:30"
        },{
            "task_id": "task_004",
            "title": "Do the laundry",
            "description": "Do the laundry at home",
            "expired": "07/02/2021 15:30"
        }
    ]'

### Response
`201 Created`

    {
        "messages": [
            "task_id task_003 has been added",
            "task_id task_004 has been added",
            "task_id task_005 has been added"
        ]
    }

## Get Task by Task_ID

### Request
`GET /task/:task_id`
    
    curl --location --request GET 'localhost:5000/get_task/task_001'

### Response
`200 Success`

    {
        "result": {
            "description": "Do the coding assessment",
            "expired": "05/02/2021 15:30",
            "expired_in_15_mins": false,
            "title": "Do ambilabs assessment"
        }
    }

`404 Not Found`

    { "result": "task ID task_006 not found" }

## Get non Expired Tasks

### Request
`GET /tasks/all_non_expired`

    curl --location --request GET 'localhost:5000/tasks/all_non_expired'

### Response
`200 Success`

    {
        "result": [
            {
                "description": "Do the coding assessment",
                "expired": "05/02/2021 15:30",
                "expired_in_15_mins": false,
                "title": "Do ambilabs assessment"
            },
            {
                "description": "Code the ambilabs assessment",
                "expired": "05/02/2021 15:30",
                "expired_in_15_mins": false,
                "title": "Do the ambilabs coding"
            }
        ]
    }

## Get All Tasks (include expired)

### Request
`GET /tasks/all`

    curl --location --request GET 'localhost:5000/tasks/all'

### Response
`200 Success`

    {
        "result": [
            {
                "description": "Code the ambilabs assessment",
                "expired": "02/05/2020 15:30",
                "expired_in_15_mins": false,
                "title": "Do the ambilabs coding"
            },
            {
                "description": "Do the coding assessment",
                "expired": "05/02/2021 15:30",
                "expired_in_15_mins": false,
                "title": "Do ambilabs assessment"
            }
        ]
    }

## Update Task

### Request
`PUT /update_task/:task_id`

    curl --location --request PUT '127.0.0.1:5000/update_task/task_001' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "title": "update ambilabs", //optional
        "description": "update the create of ambilabs", //optional
        "expired": "05/02/2021 12:30" //optional
    }'


### Response
`200 Success`

    { "result": "TaskID task_001 has been updated" }

`404 Not Found`

    { "result": "TaskID task_001 not found" }

## Delete Task

### Request
`DELETE /delete_task/:task_id`

    curl --location --request DELETE 'localhost:5000/delete_task/task_001'

### Response
`200 Success`

    { "result": "TaskID task_001 has been deleted" }

`404 Not Found`

    { "result": "TaskID task_001 not found" }