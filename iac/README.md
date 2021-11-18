
# Setting up AWS CDK for Infrastructure as Code  

Commands to spin up the infrastructure in your AWS Account:  

```console
$ cd PATH/TO?AWSCloud-TweetGenerator/iac
$ cdk init app --language python
$ source .venv/bin/activate
$ python -m pip install -r requirements.txt
$ cdk bootstrap aws://ACCOUNT-NUMBER/REGION
$ cdk synth
$ cdk deploy
```
