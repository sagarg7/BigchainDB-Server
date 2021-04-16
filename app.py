from flask import Flask, redirect, url_for, request, jsonify
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from datetime import datetime

# Start Flask app
app = Flask(__name__)

# Setup BigchainDB conenction
bdb_root_url = 'http://localhost:9984'
bdb = BigchainDB(bdb_root_url)
alice, bob = generate_keypair(), generate_keypair()


def sortFuncTime(obj):
    return datetime.fromisoformat(obj['timestamp'])


def sortFuncTime2(obj):
    return datetime.fromisoformat(obj['data']['timestamp'])


def sortFuncEUID(obj):
    return obj['data']['euid']


@app.route('/query/all/<uid>', methods=['GET'])
def indexView(uid):
    l = bdb.assets.get(search=uid)
    l = l[3:]
    d = {}
    l = sorted(l, key=sortFuncEUID)
    delass = []
    for obj in l:
        euid = obj['data']['euid']
        if obj['data']['deleted'] == True:
            delass.append(euid)
        if euid in d:
            d[euid].append(obj['data'])
        else:
            d[euid] = [obj['data']]
    fl = []
    for euid in d:
        if euid not in delass:
            fl.append(sorted(d[euid], key=sortFuncTime)[-1])
    return jsonify(fl)


@app.route('/query/<euid>', methods=['GET'])
def detailView(euid):
    l = bdb.assets.get(search=euid)
    l = sorted(l, key=sortFuncTime2)
    return jsonify(l[-1])


@app.route('/query/doc', methods=['GET'])
def indexDocView():
    l = bdb.assets.get(search="DataEntry")
    l = l[3:]
    d = {}
    l = sorted(l, key=sortFuncEUID)
    delass = []
    for obj in l:
        euid = obj['data']['euid']
        if obj['data']['deleted'] == True:
            delass.append(euid)
        if euid in d:
            d[euid].append(obj['data'])
        else:
            d[euid] = [obj['data']]
    diag = []
    undiag = []
    for euid in d:
        if euid not in delass:
            last = sorted(d[euid], key=sortFuncTime)[-1]
            if last['diagnosis'] == 'None':
                undiag.append(last)
            else:
                diag.append(last)
    return jsonify({'diagnosed': diag,
                    'undiagnosed': undiag})


@app.route('/delete', methods=['POST'])
def deleteView():
    data = request.get_json()
    data['timestamp'] = str(datetime.today())
    data['diagnosis'] = 'None'
    data['token'] = 'DataEntry'

    asset = {
        'data': data
    }

    prepared_creation_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        asset=asset,
    )

    fulfilled_creation_tx = bdb.transactions.fulfill(
        prepared_creation_tx, private_keys=alice.private_key)

    sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)

    return jsonify({
        'msg': 'Asset Deleted',
        'status': 200
    })


@app.route('/edit', methods=['POST'])
def editView():
    data = request.get_json()
    data['timestamp'] = str(datetime.today())
    data['deleted'] = False
    data['diagnosis'] = 'None'
    data['token'] = 'DataEntry'

    asset = {
        'data': data
    }

    prepared_creation_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        asset=asset,
    )

    fulfilled_creation_tx = bdb.transactions.fulfill(
        prepared_creation_tx, private_keys=alice.private_key)

    sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)

    return jsonify({
        'msg': 'Asset Edited',
        'status': 200
    })


@app.route('/add', methods=['POST'])
def addView():
    data = request.get_json()
    data['euid'] = data['uid']+str(len(bdb.assets.get(search=data['uid'])))
    data['timestamp'] = str(datetime.today())
    data['deleted'] = False
    data['diagnosis'] = 'None'
    data['token'] = 'DataEntry'

    asset = {
        'data': data
    }

    prepared_creation_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        asset=asset,
    )

    fulfilled_creation_tx = bdb.transactions.fulfill(
        prepared_creation_tx, private_keys=alice.private_key)

    sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)

    return jsonify({
        'msg': 'Asset created',
        'status': 200
    })
    
@app.route('/diag', methods=['POST'])
def addDocView():
    data = request.get_json()
    data['timestamp'] = str(datetime.today())
    data['deleted'] = False
    data['token'] = 'DataEntry'

    asset = {
        'data': data
    }

    prepared_creation_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        asset=asset,
    )

    fulfilled_creation_tx = bdb.transactions.fulfill(
        prepared_creation_tx, private_keys=alice.private_key)

    sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)

    return jsonify({
        'msg': 'Asset Edited',
        'status': 200
    })


if __name__ == '__main__':
    app.run(debug=True)
