import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-2:980720145618:deployPortfolioTopic')
    location = {
        "bucketName": 'tomspartanbuildbucket',
        "objectKey": 'portfoliobuild.zip'
    }
    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        portfolio_bucket = s3.Bucket('tomspartan.com')
        build_bucket = s3.Bucket(location["bucketName"])

        print "Building portfolio from " + str(location)
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)


        with zipfile.ZipFile(portfolio_zip) as myzip:
            for name in myzip.namelist():
               obj = myzip.open(name)
               portfolio_bucket.upload_fileobj(obj, name,ExtraArgs={'ContentType': mimetypes.guess_type(name)[0]})
               portfolio_bucket.Object(name).Acl().put(ACL='public-read')
        print "Lambda job complete"
        topic.publish(Subject="Portfolio deployed to S3 from github", Message='Portfolio deployed')
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
    except:
        topic.publish(Subject="Portfolio deploy failed", Message="Portfolio deploy failed")
        raise
