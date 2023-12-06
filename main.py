from flask import Flask, render_template, request, jsonify
import subprocess
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://u1256183_in13:uU6mX3yT3ruN8gF0@37.140.192.81/u1256183_for_interview_13'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255))
    ip_addresses = db.Column(db.String(255))
    
class IPAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    ip_addresses = db.Column(db.String(255), nullable=False)

@app.route("/")
def table():
    return render_template('table.html')

@app.route('/add_site', methods=['POST'])
def add_site():
    url = request.form['url']
    ip_addresses = get_ip_addresses(url)
    add_site(url, ip_addresses)
    return jsonify({'url': url, 'ip_addresses': ip_addresses})

def add_site(url, ip_addresses):
    ip_addresses_str = ', '.join(ip_addresses)
    site = Site(url=url, ip_addresses=ip_addresses_str)
    db.session.add(site)
    db.session.commit()

    
def get_ip_addresses(url):
    try:
        result = subprocess.check_output(['nslookup', url], universal_newlines=True)
        ip_addresses = parse_result(result)
        return ip_addresses
    except subprocess.CalledProcessError as e:
        return []

def parse_result(result):
    addresses_start = result.find("Addresses:")
    if addresses_start == -1:
        address_start = result.find("Address:")
        if address_start == -1:
            return []
        else:
            result = result.replace("Address: ", "", 1)
            address_line = result[result.find("Address:") + len("Address:"):].strip()
            addresses_list = [address_line.replace("Address: ", "", 1)]
            return [address_line]

    else:
        addresses_str = result[addresses_start + len("Addresses:"):].strip()
        addresses_list = [address.strip() for address in addresses_str.split(' ')]

    ipv4_addresses = [address for address in addresses_list if '.' in address]
    ipv6_addresses = [f'{address}' for address in addresses_list if ':' in address]

    ip_addresses = ipv4_addresses + list(ipv6_addresses)

    return ip_addresses

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
