from distutils.core import setup

setup(name='Pyranha',
      description='Elegant IRC client',
      version='0.1',
      author='John Reese',
      author_email='john@noswap.com',
      url='https://github.com/jreese/pyranha',
      classifiers=['License :: OSI Approved :: MIT License',
                   'Topic :: Communications :: Chat :: Internet Relay Chat',
                   'Development Status :: 2 - Pre-Alpha',
                   ],
      license='MIT License',
      packages=['pyranha', 'pyranha.irc'],
      package_data={'pyranha': ['dotfiles/*']},
      scripts=['bin/pyranha'],
      )
