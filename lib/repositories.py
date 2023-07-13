from pymongo import MongoClient
from pymongo.results import InsertOneResult
from pymongo.results import DeleteResult
from lib.models import Flight
import jsonpickle

class Repository:
    """
    Base class for all repositories (singleton)
    """
    _self = None

    def __new__(cls, *args, **kwargs):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self):
        self.connection_string = "mongodb+srv://Cluster37645:QkdvWU1Ucn5b@cluster37645.ynpplud.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(self.connection_string)
        self.db = self.client.rocketpy
        self.collection = self.db.flights

    def __del__(self):
        self.client.close()

class FlightRepository(Repository):
    """
    Flight repository

    Init Attributes:
        flight: Flight object
        flight_id: Flight id

    Enables CRUD operations on flight objects
    """
        
    def __init__(self, flight: Flight = None, flight_id: str = None):
        super().__init__()
        self.flight = flight
        if flight_id:
            self.flight_id = flight_id
        else:
            self.flight_id = self.flight.__hash__()

    def __del__(self):
        super().__del__()

    def create_flight(self, rocketpy_flight) -> InsertOneResult:
        """
        Creates a flight in the database

        Args:
            rocketpy_flight: rocketpy flight object

        Returns:
            InsertOneResult: result of the insert operation
        """
        if not self.get_flight():
            try: 
                flight_to_dict = self.flight.dict()
                flight_to_dict["flight_id"] = self.flight_id 
                rocketpy_jsonpickle_hash = jsonpickle.encode(rocketpy_flight)
                flight_to_dict["rocketpy_flight"] = rocketpy_jsonpickle_hash
                return self.collection.insert_one(flight_to_dict)
            except:
                raise Exception("Error creating flight")
        return InsertOneResult( acknowledged=True, inserted_id=None )

    def update_flight(self) -> "int | None":
        """
        Updates a flight in the database

        Returns:
            int: flight id
        """
        try:
            flight_to_dict = self.flight.dict()
            flight_to_dict["flight_id"] = self.flight.__hash__() 

            updated_flight = self.collection.update_one(
                { "flight_id": self.flight_id }, 
                { "$set": flight_to_dict }
            )

            self.flight_id = flight_to_dict["flight_id"]
            return  self.flight_id
        except:
            raise Exception("Error updating flight")

    def get_flight(self) -> "Flight | None":
        """
        Gets a flight from the database
        
        Returns:
            models.Flight: Model flight object
        """
        try:
            flight = self.collection.find_one({ "flight_id": self.flight_id })
            if flight is not None:
                del flight["_id"] 
                del flight["rocketpy_flight"]
                return Flight.parse_obj(flight)
            else:
                return None
        except:
            raise Exception("Error getting flight")

    def get_rocketpy_flight(self) -> "str | None":
        """
        Gets a rocketpy flight from the database

        Returns:
            str: rocketpy flight object encoded as a jsonpickle string hash
        """
        try:
            flight = self.collection.find_one({ "flight_id": self.flight_id })
            if flight is not None:
                return flight["rocketpy_flight"]
            else:
                return None
        except:
            raise Exception("Error getting rocketpy flight")
    
    def delete_flight(self) -> DeleteResult: 
        """
        Deletes a flight from the database

        Returns:
            DeleteResult: result of the delete operation
        """
        try: 
            return self.collection.delete_one({ "flight_id": self.flight_id })
        except:
            raise Exception("Error deleting flight")
