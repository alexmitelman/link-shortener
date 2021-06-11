#Chalice

## AWS CLI
Make sure you have AWS CLI installed:
```
aws --version
```
Make sure to configure it:
```
aws configure
```

## Deploy
Run `cdk bootstrap` first time.

```
cd infrastructure
cdk deploy
```

## Test locally
```
chalice local
```
