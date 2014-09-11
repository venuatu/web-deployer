from __future__ import print_function
from flask import Flask, jsonify, request
from flask.ext.pymongo import PyMongo
from sh import git, sh, ErrorReturnCode
import config, os, sys

app = Flask(__name__)
app.config.from_object(config)
mongo = PyMongo(app)

if app.config.get('ALLOWED_RANGES', None):
    ALLOWED_RANGES = app.config['ALLOWED_RANGES'] or []

"""
Mongo collections:
-   sites: {_id: 'the site name', path: 'the absolute path on this server'}
-   deploys: {site: site._id, git_revs: [start, end], 'git_output': git stdout/err, 'deploy': deploy script strerr/out,
                'service': service strerr/out}
"""

@app.route('/push/<name>', methods=['POST'])
def push(name):
    if not any([request.remote_addr.startswith(x) for x in ALLOWED_RANGES]):
        return jsonify({'status': 'access denied'}), 401

    site = mongo.db.sites.find_one({'_id': name})
    if site == None:
        return jsonify({'status': 'invalid repo spec'}), 404

    rev = str(git('rev-parse', 'origin/master', _cwd=site['path']))
    git.fetch(_cwd=site['path'])
    after_rev = str(git('rev-parse', 'origin/master', _cwd=site['path']))

    if rev != after_rev:
        git_output, deploy, err = [''] * 3
        try:
            git_output = str(git.pull(_cwd=site['path'])).strip()
            deploy = str(sh('./deploy.sh', _cwd=site['path'])).strip()
            restart = str(sudo('service', name, 'restart'))
        except ErrorReturnCode as e:
            err = str(e)
            print('weird error', err)

        mongo.db.deploys.insert({
            'site': name,
            'git_revs': [rev, after_rev],
            'git_output': git_output,
            'deploy': deploy,
            'restart': restart,
            'err': err,
        })

        return jsonify({
            'status': 'new_rev',
            'git_revs': [rev, after_rev],
            'git_output': git_output,
            'deploy': deploy,
            'restart': restart,
            'err': err,
        }), 201
    return jsonify({
        'status': 'same',
        'rev': rev or '...',
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5010)
