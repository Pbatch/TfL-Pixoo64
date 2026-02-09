# Pixoo64 TFL Dashboard



# Setup

### Port forwarding
* Set up port forwarding to bridge AWS Lambda to your Pixoo64.

### Environment variables
* Request an API key from the TFL website (https://api-portal.tfl.gov.uk/signup). 
Save it to the environment variable `TFL_APP_KEY`.

* Save the environment variable `PIXOO_URL=http://<PUBLIC_IP>:<PIXOO_PORT>/post`.

For simplicity, I have both of these variables in my `~/.bashrc`
I.e.
```bash
export PIXOO_URL="http://<PUBLIC_IP>:<PIXOO_PORT>/post"
export TFL_APP_KEY=<TFL_APP_KEY>
```

### AWS

* All these commands are run from the `aws` folder.
* If it's your first time using AWS CDK, run `cdk bootstrap` to create the CDK toolkit stack.
* Build your infrastructure with `cdk deploy`.

# Questions

If you need any help setting up this project, please post in the Issues tab.

