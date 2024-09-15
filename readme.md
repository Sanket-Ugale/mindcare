# MindCare

Empowreing Mental Health through technology

## Installation

1. Clone the repository.

2. Create Virtual Environment:
    ```shell
    source python -m venv venv
    ```

3. Activate venv:
    ```shell
    source venv\Scripts\activate
    ```

4. Go to the repository Directory:
    ```shell
    cd mindcare
    ```
5. install Dependencies:
    ```shell
    pip install requirments.txt
    ```

## Usage

To run the project, follow these steps:

1. Navigate to the project directory.

2. Run the following command to start the project:
    ```shell
    python manage.py runserver
    ```

3. Open New terminal from project directory and run:
    ```shell
    celery -A mindcare beat -l info
    ```

4. Open New terminal from project directory and run:
    ```shell
    celery -A mindcare.celery worker --pool=solo -l info
    ```

5. Open your web browser and visit `http://localhost` to access the project.