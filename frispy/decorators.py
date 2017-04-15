def log_assertion():
    def decorate(f):
        def applicator(*args, **kwargs):
            self = args[0]
            try:
                result = f(*args, **kwargs)
                if 'message' not in result:
                    result['message'] = 'OK'
                result['error'] = False

            except AssertionError as ae:
                result = ae.args[0]
                if 'message' not in result:
                    result['message'] = 'FAILED'
                result['error'] = True

            self.expectations.append(result)
            return self

        return applicator

    return decorate
