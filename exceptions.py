class InvalidQueryParamPeriod(Exception):
    def __init__(self,per):
        self.message = f'Query Parameter {per} is not a valid period'
        super().__init__(self.message)

class InvalidQueryParamCourse(Exception):
    def __init__(self,sec):
        self.message = f'Query Parameter {sec} is not a valid course'
        super().__init__(self.message)

class UnauthorizedCacheToken(Exception):
    def __init__(self):
        self.message = f'Unauthorized login token retrieved from browser cache. Clearing cache should resolve this.'
        super.__init__(self.message)
        
