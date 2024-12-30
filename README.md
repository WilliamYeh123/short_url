# short_url

## Description
This is a project implementing two short_url RESTful HTTP APIs, including a **POST** method generating the original URL into a short URL and a **GET** method redirecting the short URL back to the original URL.

There are a few methods for shortening URLs I've considered:

**Method 1: Random Token**
Generate a random alphanumeric string as the token. It is easier to implements and not predictable, though it may need a database to store the result, since I also need to store other information like original URL and expire time, this could be the better method.

**Method 2: Hashing**
Use a hashing algorithm like MD5 or SHA256.

I chose the first method to implement since it is more simple, other metheds may also be done for needs like verification or decoding. I added a checking mechanism for this method to ensure the uniqueness for tokens in the database.

**Other Features:**
1. Expiration time, default as 30 days.
2. Status codes and error messgaes for cases like invalid formats or URL not found.
3. SQLite for data storage, information including original URL, short_url and expiration time.
4. Implement rate limiting using ``Flask-Limiter``to prevent abuse of the URL shortening service.


## Requirements
* Python 3.9+
* flask 2.0.*
* Docker (optional)
* Docker Compose (optional)

## Setup
#### Method 1: Local Setup
Clone the project from github:

    git clone https://github.com/WilliamYeh123/short_url.git
    cd short_url

Create virtual environment(optional):

    python -m venv venv
    source venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Run service:

    python main.py

#### Method 2: Docker Setup (Build Docker Image)
Clone the project from github:

    git clone https://github.com/WilliamYeh123/short_url.git
    cd short_url

Install Docker if not installed, for Linux:

    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

    # Latest version
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Verify
    sudo docker run hello-world

If using Windows, you can install Docker Desktop on your system, view details and other methods at [Docker][1] official website.

[1]:https://docs.docker.com/engine/install/ubuntu/



Build image using Dockerfile, then run the service:

    docker build -t short_url:v1.0 .
    docker run -d --name url-service -p 5000:5000 short_url:v1.0

or you can choose using docker compose, better if you are adding other services in the future
but docker compose needs to be installed. Base on different version, command may be different

    docker compose up -d
    # older version:
    docker-compose up -d

#### Method 3: Docker Setup (Pull from Docker Hub)
Directly pull the docker image from Docker Hub

    docker pull williamyeh0068511/short_url:v1.0

Start the service:

    docker run -d --name url-service -p 5000:5000 williamyeh0068511/short_url:v1.0

## API Usage

This part introduces how to use the API service, assuming the service is running on localhost, the base URL is `http://127.0.0.1:5000/`, `ip` and `port` can be set based on different environment, `port` can be modified in `config.py` or `docker-compose.yml` if using docker compose.

### API 1: Create Short URL
---
* `url`: `http://127.0.0.1:5000/url/create`
* method: `POST`
* description: Take an URL as input, then returns shortened URL, which is a 20 character token added after the base URL, returns error message if `original_url` is invalid. Token length and expire time are optional inputs.

Request parameter:
| parameter     | type    | description                          | required | default |
|---------------|---------|--------------------------------------|----------|---------|
| original\_url | string  | the original url you want shortening | required |         |
| expire        | integer | total days until url expire          | optional | 30      |
| length        | integer | total length of the generated token  | optional | 20      |

URL rules:
* total length under 2048
* original_url not empty
* includes domain
* includes `http://` or `https://`

Response parameter:
| parameter        | type      | description                               |
|------------------|-----------|-------------------------------------------|
| original\_url    | string    | the original url you want shortening      |
| short\_url       | string    | short url generated from the original url |
| success          | bool      | if the url is shorten successfully        |
| reason           | string    | shows success message or error message    |
| expiration\_time | timestamp | expiration time, 30 days after created    |

Response message:
| status code | message                               |
|-------------|---------------------------------------|
| 200         | Success creating short URL            |
| 400         | Bad request                           |
| 413         | URL too long \(should be under 2048\) |
| 422         | Invalid format                        |
| 429         | Rate limit exceeded                   |

#### Example Usage
Sample request payload:

    {
        "original_url":"https://www.google.com.tw/?hl=zh_TW"
    }
Sample return data:

    # success
    {
        "expiration_date": 1737876798.399497,
        "original_url": "https://www.google.com.tw/?hl=zh_TW",
        "reason": "Success creating short URL",
        "short_url": "http://127.0.0.1:5000/qMQhNvk4k1zlW0gpoUYa",
        "success": true
    }
    # error
    {
        "reason": "Invalid format: must include scheme (http:// or https://) and domain",
        "success": false
    }

Running with Linux:

    curl --request POST \
     --url http://127.0.0.1:5000/url/create \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '{"original_url":"https://www.google.com.tw/?hl=zh_TW"}'
### API 2: Redirect Short URL
---
* `url`: `http://127.0.0.1:5000/<string:short_url>`
* method: `GET`
* description: Send `GET` request with URL returned from the first API, or simply search the URL in the browser, it would redirect to the original URL, returns error message if the short URL expired (30 dyas) or URL wasn't found in database. the database only stores the token, which is the 20 character behind, so it's ok to change ip and port as long as the data isn't removed from the table.

Response message:
| status code | message                    |
|-------------|----------------------------|
| 200         | Success creating short URL |
| 404         | URL not found              |
| 410         | URL has expired            |
| 429         | Rate limit exceeded        |

#### Example Usage
Running with Linux:

    curl --request GET \
     --url http://localhost:5000/qMQhNvk4k1zlW0gpoUYa \
     --header 'accept: application/json'

It would show redirecting message:

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <title>Redirecting...</title>
    <h1>Redirecting...</h1>
    <p>You should be redirected automatically to target URL: <a href="https://github.com/scikit-learn/scikit-learn/blob/main/README.rst?plain=1">https://github.com/scikit-learn/scikit-learn/blob/main/README.rst?plain=1</a>. If not click the link.

Run in postman:
![postman result](images/get_result1.PNG)

Search in browser:
type short_url in browser
![search result1](images/get_result2.PNG)

Then redirects to the original website
![search result2](images/get_result3.PNG)

Example of expired url:

    {
        "error": "URL has expired",
        "message": "URL has expired since Sun, 27 Oct 2024 09:37:19 GMT"
    }