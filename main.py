import flask
from flask import Flask, render_template, url_for, request, redirect
import sys,requests,random,urllib.request
import bit
from coincurve import PrivateKey,PublicKey
from eth_hash.auto import keccak
from coincurve.utils import int_to_bytes
import hashlib
from threading import Thread
import json
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
def HASH160(pubk_bytes):
    return hashlib.new('ripemd160', hashlib.sha256(pubk_bytes).digest() ).digest()
G = PublicKey.from_point(55066263022277343669578718895168534326250603453777594175500187360389116729240,32670510020758816978083085130507043184471273380659243275938904335757337482424)

app = Flask(__name__)

@app.route('/')
def index():
    key_int = 1
    return redirect('/'+str(key_int))

@app.route('/rnd')
def randp():
    #key_int = random.SystemRandom().randint(1, 904625697166532776746648320380374280100293470930272690489102837043110636675)
    data = urllib.request.urlopen("https://blockchain.info/unconfirmed-transactions?format=json").read()
    output = json.loads(data)
    intkey=int(output["txs"][0]['hash'],16)
    key_int = (intkey//128)+1
    return redirect('/'+str(key_int))

@app.route('/<int:id>')
def homeid(id):
    key_int = int(id)
    if key_int > 904625697166532776746648320380374280100293470930272690489102837043110636675:
        return redirect('/904625697166532776746648320380374280100293470930272690489102837043110636675')
    key_int = (key_int*128)-127
    nextp = int(id)+1
    prevp = int(id)-1 if int(id) > 2 else 1
    popp = int(str(id)[:-1]) if int(id)>100 else int(id)
    P = G.multiply(int_to_bytes(key_int))
    priv = "{:064x}".format(key_int)
    upub_u = P.format(compressed=False)
    upub_c = P.format(compressed=True)
    crmd = HASH160(upub_c)
    urmd = HASH160(upub_u)
    tron = bit.base58.b58encode_check(b'\x41' + keccak(upub_u[1:])[-20:])
    btc_c = bit.base58.b58encode_check(b'\x00' + crmd)
    doge_c=bit.base58.b58encode_check(b'\x1e' + crmd)
    data = {}
    try:
        for n in range(128):
            data[n]={}
            data[n]["key"]=priv
            data[n]["tron"]=tron
            data[n]["tron_bal"]="?"
            data[n]["btc"]=btc_c
            data[n]["btc_bal"]="?"
            data[n]["doge"]=doge_c
            data[n]["doge_bal"]="?"
            P = P.combine_keys([P,G])
            key_int += 1
            priv = "{:064x}".format(key_int)
            upub_u = P.format(compressed=False)
            upub_c = P.format(compressed=True)
            crmd = HASH160(upub_c)
            urmd = HASH160(upub_u)
            tron = bit.base58.b58encode_check(b'\x41' + keccak(upub_u[1:])[-20:])
            btc_c = bit.base58.b58encode_check(b'\x00' + crmd)
            doge_c=bit.base58.b58encode_check(b'\x1e' + crmd)
    except:
        pass
    return render_template('index.html',tasks = data,nextp=nextp,prevp=prevp,popp=popp)
@app.route('/dogeapi/<id>')
def dogeapi(id):
    val = "0"
    try:
        bloc = requests.get("https://dogechain.info/chain/Dogecoin/q/addressbalance/" + id) 
        val = bloc.text
    except:
        pass
    return val

            
@app.route('/key/<id>')
def keyinfo(id):
    intkey=int(id,16)
    intkey = (intkey//128)+1
    key = bit.Key.from_hex(id)
    P = G.multiply(int_to_bytes(int(id,16)))
    upub_u = P.format(compressed=False)
    upub_c = P.format(compressed=True)
    crmd = HASH160(upub_c)
    urmd = HASH160(upub_u)
    tron = bit.base58.b58encode_check(b'\x41' + keccak(upub_u[1:])[-20:])
    btc_u = bit.base58.b58encode_check(b'\x00' + urmd)
    btc_c = bit.base58.b58encode_check(b'\x00' + crmd)
    doge_c=bit.base58.b58encode_check(b'\x1e' + crmd)
    wif_bytes = bit.format.wif_to_bytes(key.to_wif())
    wif_bytes_uncompressed = (wif_bytes[0], wif_bytes[2], False)
    wif_uncompressed = bit.format.bytes_to_wif(*wif_bytes_uncompressed)
    return "Hex: {}<br><a href='/{}' target='_blank'>{}</a><br><br>Cpub: {}<br>H160_U: {}<br>H160_C: {}<br><br>Btc_U: {}<br>Btc_C: {}<br><br>Doge_C: {}<br><br>Tron: {}<br><br><hr>Wif_U: {}<br><br>Wif_C: {}<hr>".format(key.to_hex(),str(intkey),str(intkey),upub_c.hex(),urmd.hex(),crmd.hex(),btc_u,btc_c,doge_c,tron,wif_uncompressed,key.to_wif())

def run():
    app.run(host="0.0.0.0", port=8080)
def keep_alive():
    server = Thread(target=run)
    server.start()
if __name__ == "__main__":
  keep_alive()