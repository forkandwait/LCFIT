from app import app as A

class Foo(A, object):
	def __init__(self, **kwargs):
		A.__init__(self)
		self.__dict__.update(kwargs)
		pass
	pass

if __name__ == '__main__': 
	foo = Foo(TITLE='MY TITLE', TARGET='MY TARGET',
			  NAME_KEY='MY NAME KEY', PASSWD_KEY='MY PASSWORD KEY')
	print foo
