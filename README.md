# Machine Learning API

A side project to develop a back end using the [FastAPI](https://fastapi.tiangolo.com/) framework. My main goal was to study the framework using machine learning functionalities within it. To create something cool - and not only two or three POST routes - I designed a embarrassingly simple version of twitter. Also, I used [Elasticsearch](https://www.elastic.co/elasticsearch/) as the main database.

## Data Modeling

There are three types of documents: **users**, **tweets** and **retweets**. Each one of them represents one concept of this minimal twitter version and will be described in the following sub-sections:

### Users

It simply defines a user. They have an unique id (a md5 hash of their username), an username and the date when they joined the system. Also, they have the ability to follow other users (and be followed). Its document is structured as follow:

```json
{
    "id": "",
    "username":"",
    "joined_at": "",
    "follows": [],
    "followers": []
}
```

### Tweets

It represents a tweet. It has an unique id, a reference to the user's id who published it, when it was tweeted, its very text, its sentiment (negative, neutral or positive), its hashtags, retweets and likes (lists of references to users who did the action). Here is an example:

```json
{
    "id": "",
    "author_id":"",
    "tweeted_at": "",
    "text": "",
    "sentiment": "",
    "confidence": 1.0,
    "hashtags": [],
    "retweets": [],
    "likes": []
}
```

### Retweets

It represents a reference to an actually tweet. It contains an unique id, the user who referenced the tweet, when it was retweeted and the referenced tweet, as shown:

```json
{
    "id": "",
    "user_id":"",
    "referenced_at": "",
    "tweet_id": ""
}
```

## Database

The *db/setup.py* creates the necessary indices and populates them with examples. Also, the client to access the data is defined in *db/client.py*.

## Endpoints

### /users

Implements basic CRUD operations. As well as the follow/unfollow feature.

* GET <http://127.0.0.1:8000/api/v1/users/{user_id>}
* DELETE <http://127.0.0.1:8000/api/v1/users/{user_id>}
* POST <http://127.0.0.1:8000/api/v1/users/>

    ```json
    {
        "username": "string"
    }
    ```

* PUT <http://127.0.0.1:8000/api/v1/users/{follower_id}/follow/{followed_id>}
* PUT <http://127.0.0.1:8000/api/v1/users/{follower_id}/unfollow/{followed_id>}

### /tweets

Implements basic CRUD operations. Also, there are endpoints for *retweet* and *like*.

* GET <http://127.0.0.1:8000/api/v1/tweets/{tweet_id>}
* GET <http://127.0.0.1:8000/api/v1/tweets/user/{user_id>}
* POST <http://127.0.0.1:8000/api/v1/tweets/{user_id}/tweet>

    ```json
    {
        "text": "string"
    }
    ```

* POST <http://127.0.0.1:8000/api/v1/tweets/{user_id}/retweet/{tweet_id>}
* POST <http://127.0.0.1:8000/api/v1/tweets/{user_id}/like/{tweet_id>}
* DELETE <http://127.0.0.1:8000/api/v1/tweets/{tweet_id>}

### /sentiment

Implements endpoints for classify and quantify tweet's sentiment.

* POST <http://127.0.0.1:8000/api/v1/sentiment/classify>

    ```json
    {
        "text": "string"
    }
    ```

* POST <http://127.0.0.1:8000/api/v1/sentiment/quantify/user/{user_id>}
* POST <http://127.0.0.1:8000/api/v1/sentiment/quantify/hashtag/{hashtag>}

## Machine Learning

I implemented a machine learning task (**sentiment classification**) inside the API. It classifies every tweet published in three possible classes (negative, neutral or positive). The only model I trained is a [Multinomial Naive Bayes](https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html#sklearn.naive_bayes.MultinomialNB) using as input a Bag-of-Words representation ([CountVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html?highlight=countvectorizer#sklearn.feature_extraction.text.CountVectorizer)). You can check the training step in the script *train_model.py* as well as the data in *twitter_training.csv* file.

## Log

The logging is configured in the **logging.conf** file. It creates a file for every hour of activity in the *logs* folder.

## Tests

I set up the tests using the [pytest framework](https://docs.pytest.org/en/7.1.x/), and its configuration is defined in the **pytest.ini** file. All the fixtures are defined in the **conftest.py** file. There are three main files and each route has its correspondent class to implement possible use cases (tests). They are organized as follow:

* **test_users**: contains tests for routes regarding operations on users;
* **test_tweeets**: contains tests for routes regarding operations on users;
* **test_sentiment**: contains tests for routes regarding classification and quantification routes.

To run the tests use:

```bash
python3 -m pytest -vv --disable-warnings --durations=0
```

### .coveragerc

Configuration file for the test coverage. To see the coverage report run:

```bash
# generate report
coverage run -m pytest
# show report
coverage report
```

## Configuration Files

Some information may seem duplicated in different files - as elasticsearch secrets. However, the idea is to have the database and the API in different enviroments/repositories (potencially in different machines). Because I am doing everything in the same project, they seem duplicated.

### .env

It contains (env) variables used by the Elasticsearch and Kibana containers, such as: *user*, *password*, *port* and *memory limit*.

### api.cfg

File to store general information for the API to access: elasticsearch secrets, model filename, etc.

### docker-compose.yml

It sets up the Elasticsearch and Kibana containers. References: [official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.9/docker.html) and [github repository](https://github.com/justmeandopensource/elk/blob/master/docker/docker-compose-v7.9.2.yml). To run those containers, simply run:

```bash
# use the -d flag at the end if you want them to run in the background
sudo docker-compose up
```

### Dockerfile

File to build the API container.

```bash
# build the image
sudo docker build -t caiolueno/ml-api .
# publish the image in the repository
sudo docker push caiolueno/ml-api:latest
# run the API in the container
sudo docker run --network=host -p 8000:8000 caiolueno/ml-api
```

## Running

Two options to run the API:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

or using the docker container as described before:

```bash
sudo docker build -t caiolueno/ml-api .
sudo docker run --network=host -p 8000:8000 caiolueno/ml-api
```
