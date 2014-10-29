#!/bin/env python

import os
import sys
import random, string
import yaml


items = """ks_swift_password
keystone_db_password
mysql_root_password
ks_admin_password
ks_admin_token
ks_swift_dispersion_password
swift_hash_suffix
mysql_sys_maint_password
galera_clustercheck_dbpassword
neutron_metadata_proxy_shared_secret
secret_key
rabbit_password
ks_neutron_password
glance_db_password
ks_cinder_password
neutron_db_password
ks_glance_password
cinder_db_password
ks_nova_password
nova_db_password
ceilometer_secret
ks_ceilometer_password
heat_db_password
ks_heat_password
heat_auth_encryption_key
ceph_mon_secret
"""

def usage():
    print """
    SpinalStack YAML generator for Environment file
    Usage: yaml_autogen.py myenv.yml

    Will produce output.yml, preserving defined data, but replacing all 
    passwords, UUIDs and SSH keys
    """

def password_generator():
    length = 40
    xtrachars = '~!@#$%^&*()_+><.,'
    chars = string.ascii_letters + string.digits + xtrachars
    rnd = random.SystemRandom()
    passw = ''.join(rnd.choice(chars) for i in range(length))
    return passw


def generate_dict():
    passwords = {}
    for i in items.splitlines():
        passwords[i] = str(password_generator())
    return passwords

def ssh_keygen():
    from Crypto.PublicKey import RSA
    pubkey = ''
    privkey = ''
    key = RSA.generate(2048, os.urandom)
    pubkey = key.exportKey('OpenSSH')
    privkey = key.exportKey('PEM')
    return pubkey, privkey

def update_env_yaml():
    import uuid
    envfile = sys.argv[1]
    passwords = generate_dict()
    f = open(envfile, 'r')
    yml = yaml.load(f)
    config = yml['config']
    for k in config:
        if k in passwords:
            config[k] = passwords[k]
    pubkey, privkey = ssh_keygen()
    config['nova_ssh_private_key'] = privkey
    config['nova_ssh_public_key'] = pubkey
    config['ceph_fsid'] = str(uuid.uuid1())
    config['haproxy_auth'] = 'root:' + password_generator()
    yml['config'] = config
    f.close()
    outfile = open('output.yml', 'w')
    stream = yaml.dump(yml, default_flow_style=False)
    outfile.write(stream.replace('\n\n', '\n'))
    outfile.close()

if len (sys.argv) != 2:
    usage()
else:
    update_env_yaml()
