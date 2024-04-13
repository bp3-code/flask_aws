from flask import Blueprint, render_template, request, session
import boto3 
import config
import json 

auth = Blueprint('auth', __name__)

AWS_access_key_id="ASIA6ODU6IPVAUL2O4KF"
AWS_secret_access_key="zyezSiqrBHJ2nf3L65eeEwtutdhF+MVrIosfCO9K"
AWS_session_token="IQoJb3JpZ2luX2VjEDQaCXVzLXdlc3QtMiJGMEQCIF8UxROaveTxZRQNHlsoaNc8pRS0Rpzi8bNXRlzLfc1hAiAki4U2t7zLpfbfM6odw38HV2MEEBpKUwIhHk1gGEBObCq2AghtEAAaDDk5MjM4MjY5ODQ3NCIMyRC3nJsHCqLnCORGKpMCu0ycZSpxTb2jmVekbjTz71pQA6cnYSMgV0EuapQ3sKC7WQf5GD1lhj+mg0Nnn0Ywp8/hcrL9DIy3uXe6wqoWaHN3RMfyj6/T9pYuBwjPcgdkf73pH8lwKBuNq1siTi3ZLAUNc4l9vWI4w8mJJhTF/81/zNO+LxdgceYEsN5Xrdk+q3L3KSH/BW3499OaBZNmf/hLe1WFCWZqwDslqOUGyDnrSEOdXj9/sjWhsN5Hdy6MBBumPcd55+Adn7MKiQ0z5UixEAZqIbXpUsjf6nHPhPZOLf5J7OpAxMHeVzNEUixQFic+ueFsopz2bb4Ht404ZZn76HbOkdHCaVZVvFZh4pzEewWJs3/jfsG4/emnbmaOkAAw4IzosAY6ngGgZez9IUIECmvSVK4QKYLB92sZdQHUsQQLhafrIiw0vy5mcEFrZnqOlFh0yubJkkVYrQhxcwocZRfFd4VlHd4dtphNSS2lE6hJvFe/7nys/xoXKs+aawgh9cw7JsT9h0XYvkrWvnYT+IC4XrOrpSFhTaVP1nd5TmZ6kXdgca145Il7gWr0zAwVzv8SIhi5IzKOYFZdV0ZrDFOcupsSPQ=="


boto3.setup_default_session(region_name='us-east-1')
dynamodb = boto3.resource('dynamodb',
                    aws_access_key_id=AWS_access_key_id,
                    aws_secret_access_key=AWS_secret_access_key,
                    aws_session_token=AWS_session_token)

import boto3
import botocore

BUCKET_NAME = 'imagebucket-s3' # replace with your bucket name

s3 = boto3.resource('s3',
                    aws_access_key_id=AWS_access_key_id,
                    aws_secret_access_key=AWS_secret_access_key,
                    aws_session_token=AWS_session_token)


from boto3.dynamodb.conditions import Key, Attr

@auth.route('/signout')
def signout():
    session.pop('user_name', None)
    session.pop('email', None)
    return render_template('index.html')

@auth.route('/signup', methods=['post'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        table = dynamodb.Table('login')
        response = table.query(
                KeyConditionExpression=Key('email').eq(email)
        )
        items = response['Items']

        if items:
            msg = "Email already exists! Please try with another email address"
            return render_template('index.html',msg = msg)
        else:
            table.put_item(
                    Item={
            'user_name': name,
            'email': email,
            'password': password
                }
            )
            msg = "Registration Complete. Please Login to your account !"
        
            return render_template('login.html',msg = msg)

@auth.route('/check',methods = ['post'])
def check():
    if request.method=='POST':
        
        email = request.form['email']
        password = request.form['password']
        
        table = dynamodb.Table('login')
        response = table.query(
                KeyConditionExpression=Key('email').eq(email)
        )
        items = response['Items']
        name = items[0]['user_name']
        print(items[0]['password'])
        if password == items[0]['password']:
            session['user_name'] = name
            session['email'] = email
            return render_template("home.html",name=name)
    return render_template("login.html")

@auth.route('/search',methods = ['post'])
def search():
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        artist = request.form['artist']
        table = dynamodb.Table('music')

        y = year.isnumeric()
        if title:
            t = True
        else:
            t = False
        if artist:
            a = True
        else:
            a = False

        if y & a & t:
            response = table.scan(
                FilterExpression=Attr('title').eq(title) & Attr('year').eq(int(year)) & Attr('artist').eq(artist)
            )
        elif y & a:
            response = table.scan(
                FilterExpression=Attr('year').eq(int(year)) & Attr('artist').eq(artist)
            )
        elif y & t:
            response = table.scan(
                FilterExpression=Attr('year').eq(int(year)) & Attr('title').eq(title)
            )
        elif a & t:
            response = table.scan(
                FilterExpression=Attr('artist').eq(artist) & Attr('title').eq(title)
            )
        elif y:
            response = table.query(
                KeyConditionExpression=Key('year').eq(int(year))
        )
        elif a:
            response = table.scan(
                FilterExpression=Attr('artist').eq(artist)
            )
        elif t:
            response = table.scan(
                FilterExpression=Attr('title').eq(title)
            )
        items = response['Items']
        table_2 = dynamodb.Table('subscriptions')
        response_2 = table_2.scan(
                FilterExpression=Attr('email').eq(session['email'])
            )
        items_2 = response_2['Items']
        
        unsubbed = []
        for item in items:
            for item2 in items_2:
                if item['title'] == item2['title'] and item['artist'] == item2['artist'] and item['year'] == item2['year']:
                    item['subscribed'] = True
                elif 'subscribed' in item and item['subscribed'] == True:
                    pass
                else:
                    item['subscribed'] = False
        if items_2:
            for item in items:
                if item['subscribed'] == False:
                    unsubbed.append(item)
        else:
            unsubbed = items
        for item in unsubbed:
            item['url'] = create_presigned_url(BUCKET_NAME, item['artist'] + '.jpg')

        if not unsubbed:
            msg = "No result is retrieved. Please query again"
            return render_template('music.html',msg = msg)

        return render_template('music.html',items = unsubbed)
    
def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object"""
    s3_client = boto3.client('s3')
    response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name,
                                                        'Key': object_name},
                                                ExpiresIn=expiration)
    return response

@auth.route('/subscribe',methods = ['post'])
def subscribe():
    if request.method == 'POST':
        item = request.form.get('item')
    item = item.replace("\'", "\"")
    item = item.replace("Decimal(", "")
    item = item.replace("True", "\"True\"")
    item = item.replace("False", "\"False\"")
    item = item.replace(")", "")
    item = json.loads(item)
    table = dynamodb.Table('subscriptions')
    table.put_item(
                    Item={
            'email': session['email'],
            'title': item['title'],
            'artist': item['artist'],
            'year': int(item['year'])
                })
    table = dynamodb.Table('subscriptions')
    response = table.scan(
                FilterExpression=Attr('email').eq(session['email'])
            )
    items = response['Items']
    for item in items:
            item['url'] = create_presigned_url('imagebucket-s3', item['artist'] + '.jpg')
    return render_template('subscriptions.html',items=items)
    

@auth.route('/subscriptions')
def subscriptions():
    table = dynamodb.Table('subscriptions')
    response = table.scan(
                FilterExpression=Attr('email').eq(session['email'])
            )
    items = response['Items']
    for item in items:
            item['url'] = create_presigned_url('imagebucket-s3', item['artist'] + '.jpg')
    return render_template('subscriptions.html',items=items)

@auth.route('/unsubscribe',methods = ['post'])
def unsubscribe():
    if request.method == 'POST':
        item = request.form.get('item')
    item = item.replace("\'", "\"")
    item = item.replace("Decimal(", "")
    item = item.replace("True", "\"True\"")
    item = item.replace("False", "\"False\"")
    item = item.replace(")", "")
    item = json.loads(item)
    table = dynamodb.Table('subscriptions')
    response = table.delete_item(
        Key={
            'title': item['title'],
            'year': int(item['year'])
        }
    )
    table = dynamodb.Table('subscriptions')
    response = table.scan(
                FilterExpression=Attr('email').eq(session['email'])
            )
    items = response['Items']
    for item in items:
        item['url'] = create_presigned_url('imagebucket-s3', item['artist'] + '.jpg')

    return render_template('subscriptions.html',items=items)
