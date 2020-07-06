# Tweetbrief

A user-controlled automation for generating daily Twitter briefs.

## Why

Wouldn't it be nice and relaxing to be able to stay up to date with one's own Twitter bubble without the need to actually engage in all the Social Web nonsense? Without loosing oneself into the hopeless attempts to catch up with the endless Twitter timelines? Without pseudo social interactions? Without being subject to Twitter algorithms which decide what one sees and what we overlook?

## What

This project is a user-controlled automation (packaged to conveniently run in a  docker container) for generating daily Twitter briefs. This machinery expects only a few essential input parameters:

- `CONSUMER_KEY`

- `CONSUMER_SECRET`

- `TARGET_USERNAME`

- and at least one of the following options for storing data:
    - `HOST_OUTPUT` and `BRIEF_OUTPUT` to save it locally,
    - `DROPBOX_ACCESS_TOKEN` to upload it to Dropbox.

Once given the above parameters, the following algorithm is used to assemble a daily brief:

1. The authentication credentials (`CONSUMER_KEY` and `CONSUMER_SECRET`) are set to enable querying Twitter.

2. The set of accounts being followed by the `TARGET_USERNAME` is read.

3. For each of these followed accounts, the list of max. 3 "top" tweets are read from that account's feed.

4. All these lists of the "top" tweets from all the followed accounts are combined into one single list. This combined  list is then sorted and trimmed
so it fits on one page when tweets are printed (yes, that means lots of trimming!).

5. A one 2-column page PDF is generated, presenting all the top tweets obtained in the previous step. This PDF is made  available through an `HOST_OUTPUT` volume for further consumption by the user.

The metric used for calculating the "top" tweets are the number of retweets they got. In the future version, we will likely want to replace this metric with: "the number of RTs from the users being followed by the target user".

### Configuration

The whole configuration is defined via a `.env` file containing required parameters that are used then to deploy the application locally as a Docker container or to a cloud infrastructure as an AWS Lambda function.

```sh
# AWS credentials
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=...

# Tweetbrief credentials
CONSUMER_KEY=..
CONSUMER_SECRET=...
DROPBOX_ACCESS_TOKEN=...
HOST_OUTPUT=./output
BRIEF_OUTPUT=/output
BRIEF_PERIOD=1
BRIEF_MAX_TWEETS=32
SINGLE_AUTHOR_MAX_TWEETS=2
URL2QR=False
TARGET_USERNAME=WildlandIO
```

As seen above, it is also possible to configure the some secondary params, which otherwise should get sane defaults:

- `BRIEF_PERIOD` -- the period of time, in days (24h), defining the window time of which tweets to gather in step `#1`  above. Default `1` day.

- `BRIEF_MAX_TWEETS` -- the maximum number of tweets to include in a brief. Default `30`.

- `SINGLE_AUTHOR_MAX_TWEETS` -- the maximum number of tweets from one user to include (step `#2`). Default `3`.

- `URL2QR` --  the flag indicating whether URLs should be converted to QR codes. Default `True`.

For a cloud deployment, the following parameters are required:

- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` assigned to an IAM with the permissions listed below:
    - `AWSCloudFormationFullAccess`
    - `AWSLambdaFullAccess`
    - `IAMFullAccess`
    - optional: to restrict the above permissions, create a custom policy with actions included in `aws-policy.json` file (reference: [IAM JSON Policy Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html))

- `AWS_DEFAULT_REGION` -- the AWS region in which resources will be created.

### Deployment

The deployment process are performed using one of the available scripts:

- `./docker-compose.aws.yaml` for AWS deployment via `docker-compose`,

- `./docker-compose.yaml` for local deployments via `docker-compose`.

Both of them require Docker and Docker Compose installed.

## How

### Twitter API

The connection to the Twitter API is made using the Python package [tweepy](https://github.com/tweepy/tweepy). The library was chosen because of the regular releases that are made in parallel with the releases of the new Python
version.

The Twitter API requires that all requests use OAuth to authenticate. So it is needed to create the authentication credentials to be able to use the API. These credentials are two text strings:

- Consumer API Key,
- Consumer API Secret.

To obtain them, a Twitter Developer Account is needed and it must be verified by a code sent via SMS. Then, it is required to submit detailed use case information about an intended use of Twitter APIs so it can be approved by Twitter. The last step is to create an Twitter App which provides access to the above-mentioned keys.

The whole procedure is described at this [link](https://developer.twitter.com/en/docs/basics/apps/overview).

### PDF

The PDF files are generated using the Python package [weasyprint](https://github.com/Kozea/WeasyPrint), which allow to convert an HTML page to a PDF page. From many available solutions this one was chosen beacuse of CSS flexbox and columns support which made it easy to generate 2-columns page PDF files.

### Dropbox

Uploading files to Dropbox is implemented using the Python package [dropbox](https://github.com/dropbox/dropbox-sdk-python) which is the official Dropbox API Client for integrating with the Dropbox API v2. Its use requires the creation of a Dropbox App which will allow to get an access token. The detailed instruction is available at this [link](https://www.dropbox.com/developers/reference/getting-started#app%20console).

### AWS

An automated deployment to AWS is performed using a CloudFormation template which describe all resources, roles and permissions needed to execute the application. In addition, a GitHub Workflow is configured so the deployment is triggered on every push to the master branch.

## Debug

The following commands might be helpful in debugging:

* to get info about the function:
```sh
docker run \
    --interactive \
    --env-file .env \
    tweetbrief-aws \
        aws lambda get-function \
            --function-name Tweetbrief
```

* to trigger the function:
```sh
docker run \
    --interactive \
    --env-file .env \
    tweetbrief-aws \
        aws lambda invoke \
            --function-name Tweetbrief \
            --invocation-type Event \
            /dev/null
```