from flask import request
from app import app,db
from fake_data.posts import post_data
from app.models import User,Post
from app.auth import basic_auth,token_auth


# will setup DB later, for now we will store all new users in this list
users = []

@app.route('/')
def index():
    first_name = "Javan"
    last_name = "smalls"
    return f"Hello world! - From {first_name} {last_name}"

# User ENDPOINTS
@app.route("/token")
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = user.get_token()
    return{"token":token,
            "tokenExpiration":user.token_expiration}




# Create New User 
@app.route('/users', methods=['POST'])
def create_user():
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error':'Your content-type must be application/json'},400
    # Get the data from the request body
    data = request.json
    # Validate that the data has all of the required fields
    required_fields = ['firstName','lastName','username','email','password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"},400
    
    #  Get the values from the data
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    #  Check to see if any current users already have that username and/or email
    check_users = db.session.execute(db.select(User).where((User.username==username) | (User.email==email) )).scalars().all()
    # If the list is empty someonelready has that username or email
    if check_users:
        return {'error': 'A user with that username and?or email already exists'},400
    
    # create a new user instance with the request data which will add it to the database
    new_user = User(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
    return new_user.to_dict(),201
    


# POST ENDPOINTS

# Get all posts
@app.route('/posts')
def get_posts():
    # Get the posts from the database
    posts = db.session.execute(db.select(Post)).scalars().all()
    return [p.to_dict() for p in posts]

#  Get single post by ID

@app.route('/posts/<int:post_id>')
def get_post(post_id):
    post = db.session.get(Post,post_id)
    # For each dictionary in the list of ppost dictionariesL
    if post:
        return post.to_dict()
    else:
        return {'error': f"Post with an ID of {post_id} does not exist"}

# Create new Post route
@app.route('/posts', methods=['POST'])
@token_auth.login_required
def create_post():
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error':' You content-type must be application/json'},400
    #  Get the data from the request body
    data = request.json
    # Validate the incoming data
    required_fields = ['title','body']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400


    # Get data from the body
    title = data.get('title')
    body = data.get('body')

# Create a new instance of Post which 
    new_post = Post(title=title,body=body,user_id=4)
    return new_post.to_dict(),201


# Update
@app.route('/users/<int:user_id>',methods=['POST'])
@token_auth.login_required
def edit_user(user_id):
    # check if they sent the data correctly
    if not request.is_json:
        return {"error": "Your content type must be application/JSON !"},400
    # get user based off id
    user = db.session.get(User,user_id)
    # make sure it exists
    if user is None:
        return {"error":f"User with {user_id} does not exist"},404
    # if user exists get token 
    current_user = token_auth.current_user()
    # make sure they are the person logged in
    if user is not current_user:
        return {"error":"You cannot change this user as you are not them !"},403
    # then we update:
    data = request.json
    user.update(**data)
    return user.to_dict

# delete
@app.route("/users/<int:user_id>",methods = ["DELETE"])
@token_auth.login_required
def delete_user(user_id):
    # get the user based on the id
    user = db.session.get(User,user_id)
    # get token
    current_user = token_auth.current_user()
    # make sure its a real user
    if user is None:
        return {"error":f"User with {user_id} not found!"},404
    # make sure they are logged in
    if user is not current_user:
        return {"error": "You cant do that,delete yourself only"},403
    # Delete User
    user.delete()
    return{"Success": f"{user.username} has been deleted"}

# retrive?
@app.route("/users/<int:user_id>")
def get_user(user_id):
    # get the user
    user = db.session.get(User,user_id)
    # if no user let them know
    if user:
        return user.to_dict
    else:
        return {"error": f"user with id: {user_id} not found"},404
    
@app.route('/users/me')
@token_auth.login_required
def get_me():
    current_user = token_auth.current_user()
    return current_user.to_dict()

