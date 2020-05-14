import unittest

import coverage

def main():
    cov = coverage.Coverage(
    branch=True,
    include='rest_server/*',
    )

    cov.start()
    tests = unittest.TestLoader().discover("test")
    result = unittest.TextTestRunner(verbosity=2).run(tests)

    if result.wasSuccessful():
        cov.stop()
        cov.report(show_missing=True)
        return 0
    else:
        return 1

if __name__ == '__main__':
    exit(main())
