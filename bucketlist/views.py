from flask import url_for, jsonify, request, g
from bucketlist import app, db
from bucketlist.models import User, Bucketlist, BucketlistItem, ValidationError
from bucketlist.auth import auth_token, verify_password, generate_auth_token


@app.route("/auth/register", methods=["POST"])
def new_user():
    user = User()
    try:
        sanitized = user.import_data(request.json)
        if sanitized == "Invalid":
            return jsonify({"Message": "Username and Password are required"}), 400
    except ValidationError as e:
        return jsonify({"Message": str(e)}), 400
    user.set_password(user.password_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({"Message": user.username.title() + " has been created"}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    user = User()
    user.import_data(request.json)
    username = user.username
    password = user.password_hash
    if verify_password(username, password):
        return jsonify({"Token": generate_auth_token(g.user.id)}), 200
    return jsonify({"Message": "Invalid username or password. Please try again"}), 401


@app.route("/bucketlists/", methods=["POST"])
@auth_token.login_required
def new_bucketlist():
    bucketlist = Bucketlist()
    try:
        sanitized = bucketlist.import_data(request.json)
        if sanitized == "Invalid":
            return jsonify({"Message": "The bucketlist must have a name"}), 400
    except ValidationError as e:
        return jsonify({"Message": str(e)}), 400
    bucketlist.created_by = g.user.id
    db.session.add(bucketlist)
    db.session.commit()
    return jsonify({"Message": bucketlist.name.title() + " has been created"}), 201


@app.route("/bucketlists/", methods=["GET"])
@auth_token.login_required
def all_bucketlists():
    q = request.args.get("q", "")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    if limit > 100:
        limit = 100
    try:
        bucketlists = Bucketlist.query.filter(
            Bucketlist.name.like("%" + q + "%")).paginate(page, limit, error_out=True)
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
    except:
        return jsonify({"Message": "There are no bucketlists"}), 404


@app.route("/bucketlists/<int:bucket_id>", methods=["GET"])
@auth_token.login_required
def get_bucketlist(bucket_id):
    try:
        bucketlist = Bucketlist.query.get_or_404(bucket_id)
        if bucketlist.created_by != g.user.id:
            return jsonify({"Unauthorized": "You can only view bucketlists that you have created"})
        else:
            return jsonify({"Bucketlist": bucketlist.export_data()}), 200
    except:
        return jsonify({"Message": "That bucketlist does not exist"}), 404


@app.route("/bucketlists/<int:bucket_id>", methods=["PUT"])
@auth_token.login_required
def update_bucketlist(bucket_id):
    try:
        bucketlist = Bucketlist.query.get_or_404(bucket_id)
        if bucketlist.created_by != g.user.id:
            return jsonify({"Unauthorized": "You can only update bucketlists that you have created"})
        else:
            bucketlist.update_data(request.json)
            db.session.commit()
            return jsonify({"Message": "Updated to " + bucketlist.name.title()}), 200
    except:
        return jsonify({"Message": "That bucketlist does not exist"}), 404


@app.route("/bucketlists/<int:bucket_id>", methods=["DELETE"])
@auth_token.login_required
def delete_bucketlist(bucket_id):
    try:
        bucketlist = Bucketlist.query.get_or_404(bucket_id)
        db.session.delete(bucketlist)
        db.session.commit()
        return jsonify({"Message": bucketlist.name.title() + " has been deleted"}), 200
    except:
        return jsonify({"Message": "That bucketlist does not exist"}), 404


@app.route("/bucketlists/<int:bucket_id>/items", methods=["POST"])
@auth_token.login_required
def new_item(bucket_id):
    Bucketlist.query.get_or_404(bucket_id)
    item = BucketlistItem()
    try:
        sanitized = item.import_data(request.json)
        if sanitized == "Invalid":
            return jsonify({"Message": "The item must have a name"}), 400
    except ValidationError as e:
        return jsonify({"Message": str(e)}), 400
    item.bucket = bucket_id
    db.session.add(item)
    db.session.commit()
    return jsonify({"Message": item.name.title() + " has been created"}), 201


@app.route("/bucketlists/<int:bucket_id>/items/<int:item_id>", methods=["PUT"])
@auth_token.login_required
def update_item(bucket_id, item_id):
    try:
        item = BucketlistItem.query.filter_by(bucket=bucket_id, id=item_id).first()
        item.update_data(request.json)
        db.session.commit()
        return jsonify({"Message": "Updated: " + item.name.title()}), 200
    except:
        return jsonify({"Message": "Item does not exist"}), 404


@app.route("/bucketlists/<int:bucket_id>/items/<int:item_id>", methods=["DELETE"])
@auth_token.login_required
def delete_item(bucket_id, item_id):
    itemlist = BucketlistItem.query.filter_by(bucket=bucket_id)
    for item in itemlist:
        if item.id == item_id:
            db.session.delete(item)
            db.session.commit()
            return jsonify({"Message": item.name.title() + " has been deleted"}), 200
    return jsonify({"Message": "Item does not exist"}), 404
