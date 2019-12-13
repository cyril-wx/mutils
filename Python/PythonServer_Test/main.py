# filename: main.py

import web

from handle import Handle

urls=(
	'/codetest', 'Handle',
	'/codetest/\d', 'Handle',
#	'/(.*)', 'Handle'
#	'/', 'Handle',
)

if __name__ == "__main__":
	app=web.application(urls, globals())
	app.run()
