# -*- coding: UTF-8 -*-
from __future__ import with_statement
from fabric.api import local, settings, abort, run, cd, env, sudo
from fabric.contrib.console import confirm
import os

if os.path.exists('.env'):
	print('Importing environment from .env...')
	for line in open('.env'):
		var = line.strip().split('=')
		if len(var) == 2:
			os.environ[var[0]] = var[1]

server_host=[]
server_host.append(str(os.environ.get('ENVHOST')))
env.hosts = server_host
env.user = os.environ.get('ENVUSER')
env.sudo_user = os.environ.get('ENVSUDO_USER')
env.password= os.environ.get('ENVPASSWORD')

def test():
	with settings(warn_only=True):
		result = local('python manage.py test', capture=True)
	if result.failed and not confirm('Tests failed. Continue anyway?'):
		abort('Aborting at user request.')

def commit():
	local('git add -p && git commit')

def push():
	local('git push')

def prepare_deploy():
	test()
	commit()
	push()

def deploy():
	code_dir = os.environ.get('ENV_CODE_DIR')
	git_path = os.environ.get('ENV_GIT_PATH')
	with settings(warn_only=True):
		if run('test -d %s' % code_dir).failed:
			run('git clone %s %s' % (git_path,code_dir))
	with cd(code_dir):
		run('git pull')
		sudo('systemctl restart my_blog')
		sudo('systemctl restart nginx')