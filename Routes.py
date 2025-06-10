from controllers.OneFive.index import OneFiveScrapper


class Routes():
    
    def __init__(self, Api) -> object:
        
        self.api = Api
        self.route = '/api'
        self.__post()
        # self.__get()
        # self.__delete()
        # self.__put()
        
    def __get(self):
        pass
    
    def __post(self) -> object:
        self.api.add_resource(OneFiveScrapper, f"{self.route}/OneFive")
    

    
    
