from flask import jsonify, request, g
from bucketlist import app, db
from bucketlist.models import User, Bucketlist, BucketlistItem, ValidationError
from bucketlist.auth import auth_token, verify_password, generate_auth_token


@app.route("/auth/register", methods=["POST"])
def new_user():
    """
    Creates a new user.
    """
    user = User()
    try:
        # validates user key/value inputs using a try-catch block
        sanitized = user.import_data(request.json)
        if sanitized == "Invalid":
            return jsonify({"Message": "Username and Password are required"}), 400
    except ValidationError as e:
        return jsonify({"Message": str(e)}), 400

    # check for duplicates before creating the new user
    duplicate = User.query.filter_by(username=user.username).first()
    if not duplicate:
        user.set_password(user.password_hash)
        db.session.add(user)
        db.session.commit()
        return jsonify({"Message": user.username.title() + " has been created"}), 201
    return jsonify({"Message": "A user with that name already exists. Please try again"}), 400


@app.route("/auth/login", methods=["POST"])
def login():
    """
    Login a pre-existing user and return a token.
    """
    user = User()
    user.import_data(request.json)
    username = user.username
    password = user.password_hash

    """Uses a custom verify_password function and flask auth extensions
    to check the password and generate a token"""
    if verify_password(username, password):
        return jsonify({"Token": generate_auth_token(g.user.id)}), 200
    return jsonify({"Message": "Invalid username or password. Please try again"}), 401


@app.route("/auth/user/", methods=["GET"])
@auth_token.login_required
def get_user_details():
    """
    Return a logged-in user's url to view all their bucketlists
    """
    result = User.query.filter_by(id=g.user.id).first()
    return jsonify({"Details": result.export_data()})


@app.route("/bucketlists/", methods=["POST"])
@auth_token.login_required
def new_bucketlist():
    """
    Creates a new bucketlist.
    """
    try:
        # validates user key/value inputs using a try-catch block 
        bucketlist = Bucketlist()
        sanitized = bucketlist.import_data(request.json)
        if sanitized == "Invalid":
            return jsonify({"Message": "The bucketlist must have a name"}), 400
    except ValidationError as e:
        return jsonify({"Message": str(e)}), 400

    # checks for duplicates before creating the new bucketlist
    duplicate = Bucketlist.query.filter_by(name=bucketlist.name, created_by=g.user.id).first()
    if not duplicate:
        bucketlist.created_by = g.user.id
        db.session.add(bucketlist)
        db.session.commit()
        return jsonify({"Message": bucketlist.name.title() + " has been created"}), 201
    return jsonify({"Message": "A bucketlist with that name already exists. Please try again"}), 400


@app.route("/bucketlists/", methods=["GET"])
@auth_token.login_required
def all_bucketlists():
    """
    Returns all the bucketlists.
    
    'q' defines a specific item to be searched for
    'page' defines the number of pages
    'limit' defines the number of results per page
    """
    q = request.args.get("q", "")
    try:
        page = int(request.args.get("page", 1))
    except:
        return jsonify({"Message": "Please use numbers to define the page"})
    try:
        limit = int(request.args.get("limit", 20))
        if limit > 100:
            limit = 100
    except:
        return jsonify({"Message": "Please use numbers to define the limit"})

    try:
        bucketlists = Bucketlist.query.filter(Bucketlist.created_by == g.user.id,
                                              Bucketlist.name.like("%" + q + "%")).paginate(page, limit, error_out=True)
        if not bucketlists:
            return jsonify({"Message": "That bucketlist does not exist. Please try again"}), 404
    except:
        return jsonify({"Message": "There are no bucketlists matching your request. Please try again"}), 404

    if bucketlists.has_next:
        next_page = "/bucketlists/?" + "limit=" + str(limit) + "&page=" + str(page + 1)
    else:
        next_page = "None"
    if bucketlists.has_prev:
        prev_page = "/bucketlists/?" + "limit=" + str(limit) + "&page=" + str(page - 1)
    else:
        prev_page = "None"

    return jsonify({"count": len(bucketlists.items),
                    "next": next_page,
                    "prev": prev_page,
                    "Bucketlists": [bucketlist.export_data() for bucketlist in bucketlists.items]}), 200


@app.route("/bucketlists/<int:bucket_id>/", methods=["GET"])
@auth_token.login_required
def get_bucketlist(bucket_id):
    """
    Returns a specified bucketlist.
    """
    # ensures that a logged-in user can only edit their own bucketlist
    bucketlist = Bucketlist.query.filter_by(id=bucket_id, created_by=g.user.id).first()
    if not bucketlist:
        return jsonify({"Message": "That bucketlist does not exist for your user account. Please try again"}), 404
    return jsonify({"Bucketlist": bucketlist.export_data()}), 200


@app.route("/bucketlists/<int:bucket_id>/", methods=["PUT"])
@auth_token.login_required
def update_bucketlist(bucket_id):
    """
    Updates a specified bucketlist.
    """
    # ensures that a logged-in user can only edit their own bucketlist
    bucketlist = Bucketlist.query.filter_by(id=bucket_id, created_by=g.user.id).first()
    if not bucketlist:
        return jsonify({"Message": "That bucketlist does not exist for your user account. Please try again"}), 404
    updated = bucketlist.update_data(request.json)
    db.session.commit()
    return jsonify({"Message": "Updated to " + updated.name.title()}), 200


@app.route("/bucketlists/<int:bucket_id>/", methods=["DELETE"])
@auth_token.login_required
def delete_bucketlist(bucket_id):
    """
    Deletes a specified bucketlist.
    """
    # ensures that a logged-in user can only edit their own bucketlist
    bucketlist = Bucketlist.query.filter_by(id=bucket_id, created_by=g.user.id).first()
    if not bucketlist:
        return jsonify({"Message": "That bucketlist does not exist for your user account. Please try again"}), 404
    db.session.delete(bucketlist)
    db.session.commit()
    return jsonify({"Message": bucketlist.name.title() + " has been deleted"}), 200


@app.route("/bucketlists/<int:bucket_id>/items/", methods=["POST"])
@auth_token.login_required
def new_item(bucket_id):
    """
    Creates a new bucketlist item.
    """
    # check if bucketlist exists, then validate user input using try-catch block
    bucketlist = Bucketlist.query.filter_by(id=bucket_id, created_by=g.user.id).first()
    if not bucketlist:
        return jsonify({"Message": "You can only create an item within your own bucketlist. Please try again"}), 404
    else:    
        try:
            item = BucketlistItem()
            sanitized = item.import_data(request.json)
            if sanitized == "Invalid":
                return jsonify({"Message": "The item must have a name"}), 400
        except ValidationError as e:
            return jsonify({"Message": str(e)}), 400

        # check for duplicates before creating the new item
        duplicate = BucketlistItem.query.filter_by(name=item.name, bucket=bucket_id).first()
        if not duplicate:
            item.bucket = bucket_id
            item.created_by = g.user.id
            db.session.add(item)
            db.session.commit()
            return jsonify({"Message": item.name.title() + " has been created",
                            "View it here": item.export_data()}), 201
        return jsonify({"Message": "A bucketlist item with that name already exists. Please try again"}), 400


#FIX THE PUT REQUEST SO THAT EITHER NAME OR DONE, NOT BOTH REQUIRED
@app.route("/bucketlists/<int:bucket_id>/items/<int:item_id>/", methods=["PUT"])
@auth_token.login_required
def update_item(bucket_id, item_id):
    """
    Updates a specified item belonging to a specified bucketlist
    """
    # ensures that a logged-in user can only access their own bucketlist
    item = BucketlistItem.query.filter_by(bucket=bucket_id, id=item_id, created_by=g.user.id).first()
    if not item:
        return jsonify({"Message": "That item does not exist for your user account. Please try again"}), 404
    # checks for duplicates before updating the item
    item.update_data(request.json)
    db.session.commit()
    return jsonify({"Message": "Updated: " + item.name.title(),
                    "View it here": item.export_data()}), 200


@app.route("/bucketlists/<int:bucket_id>/items/<int:item_id>/", methods=["DELETE"])
@auth_token.login_required
def delete_item(bucket_id, item_id):
    """
    Deletes a specified item belonging to a specified bucketlist
    """
    # ensures that a logged-in user can only access their own bucketlist
    item = BucketlistItem.query.filter_by(bucket=bucket_id, id=item_id, created_by=g.user.id).first()
    if not item:
        return jsonify({"Message": "That item does not exist for your user account. Please try again"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"Message": item.name.title() + " has been deleted",
                    "View the remaining items here": item.export_data()}), 200
