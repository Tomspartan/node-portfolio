import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-2:980720145618:deployPortfolioTopic')
    try:
        portfolio_bucket = s3.Bucket('tomspartan.com')
        build_bucket = s3.Bucket('tomspartanbuildbucket')


        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)


        with zipfile.ZipFile(portfolio_zip) as myzip:
            for name in myzip.namelist():
               obj = myzip.open(name)
               portfolio_bucket.upload_fileobj(obj, name,ExtraArgs={'ContentType': mimetypes.guess_type(name)[0]})
               portfolio_bucket.Object(name).Acl().put(ACL='public-read')
        print "Lambda job complete"
        topic.publish(Subject="Portfolio deployed to S3 from github", Message='Portfolio deployed')
    except:
        topic.publish(Subject="Portfolio deploy failed", Message="Portfolio deploy failed")
        raise
