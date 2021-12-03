[![CI](https://github.com/dai-anna/AWSCloud-TweetGenerator/actions/workflows/main.yml/badge.svg)](https://github.com/dai-anna/AWSCloud-TweetGenerator/actions/workflows/main.yml)
# AWS Cloud Tweet Generator <img width=90 align="right" src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Duke_University_logo.svg/1024px-Duke_University_logo.svg.png">
Lives on  <img width=100 src="https://www.icmanage.com/wp-content/uploads/2018/05/AWS-logo.png">

## The Project
AWS cloud native Tweet generator leveraging NLP text generation models to generate Tweets based off trending hashtags in the past 24 hours.
- Ingests currently trending hashtags
- Scrapes tweets associated to the hashtags
- Uses generative text model to fabricate artificial tweets about trending topics

## See it in Action
- Check out the interactive generator website: XXXTBDXXX
- Follow our Bot on Twitter [here](https://twitter.com/NGtweetsdaily)

## Project Architecture
![Architectural_diagram](https://user-images.githubusercontent.com/89488845/142493175-65211b07-92be-4419-84ff-48a256f151e9.png)

## Frontend
<div align="center">
<img width="800" alt="image" src="https://user-images.githubusercontent.com/58488209/142140632-2ed40fef-075a-4639-8d60-aebdc615c046.png">
</div>


## Environment Setup
### Install Dependencies
```bash
python -m venv env
source env/bin/activate
```

```bash
make install
```
### Environment Variables 
The project requires four environment variables to be set:
| Name | Value |
| --- | --- |
| `API_TOKEN` | Your Twitter API Bearer Token |
| `BUCKET_NAME` | Name of the S3 Bucket to use for data storage |
| `ACCESS_KEY_ID` | Your AWS Access Key ID |
| `SECRET_ACCESS_KEY` | Your AWS Secret Access Key |

