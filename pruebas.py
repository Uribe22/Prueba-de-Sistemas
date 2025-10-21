import unittest
import grpc
from concurrent import futures
import distance_unary_pb2_grpc as pb2_grpc
import distance_unary_pb2 as pb2
from distance_grpc_service import DistanceServicer
from geo_location import Position

class TestPositionLatitude(unittest.TestCase):

    def test_min_latitude_out_of_range(self):
        with self.assertRaises(ValueError) as context:
            Position(-90.000001, 0, 0) 
        self.assertIn("Latitude out of range", str(context.exception))

    def test_max_latitude_out_of_range(self):
        with self.assertRaises(ValueError) as context:
            Position(90.000001, 0, 0)
        self.assertIn("Latitude out of range", str(context.exception))

    def test_min_latitude_edge(self):#
        posicion = Position(-90, 0, 0) #valores frontera
        self.assertEqual(posicion._latitude, -90.0)
    
    def test_max_latitude_edge(self):
        posicion = Position(90, 0, 0)
        self.assertEqual(posicion._latitude, 90.0)

class TestPositionLongitude(unittest.TestCase):

    def test_min_longitude_out_of_range(self):
        with self.assertRaises(ValueError) as context:
            Position(0, -180.000001, 0)
        self.assertIn("Longitude out of range", str(context.exception))

    def test_max_longitude_out_of_range(self):
        with self.assertRaises(ValueError) as context:
            Position(0, 180.000001, 0)
        self.assertIn("Longitude out of range", str(context.exception))

    def test_min_longitude_edge(self):
        posicion = Position(0, -180, 0) #valores frontera
        self.assertEqual(posicion._longitude, -180.0)
    
    def test_max_longitude_edge(self):
        posicion = Position(0, 180, 0)
        self.assertEqual(posicion._longitude, 180.0)


class TestPositionTypeValues(unittest.TestCase):

    def test_latitude_as_string(self):
        with self.assertRaises(TypeError):
            Position("90", 0, 0)

    def test_longitude_as_string(self):
        with self.assertRaises(TypeError):
            Position(0, "180", 0)  
    
    def test_latitude_none_value(self):
        with self.assertRaises(TypeError):
            Position(None, 0, 0)  
    
    def test_longitude_none_value(self):
        with self.assertRaises(TypeError):
            Position(0, None, 0)  

class TestDistanceClient(unittest.TestCase):

    @classmethod #Levantamiento de servidor y cliente
    def setUpClass(cls):
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_DistanceServiceServicer_to_server(DistanceServicer(), cls.server)
        cls.port = cls.server.add_insecure_port('[::]:0')
        cls.server.start()
        
        cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
        cls.stub = pb2_grpc.DistanceServiceStub(cls.channel)

    @classmethod #Cierre de servidor y cliente
    def tearDownClass(cls):
        cls.channel.close()
        cls.server.stop(None) 

    def test_no_unit_specified(self):
        message =  pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=0),
            unit=""
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.unit, "km")
    
    def test_invalid_unit(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=0),
            unit="invalid"  
        )
        with self.assertRaises(grpc.RpcError):
            self.stub.geodesic_distance(message)

class TestDistanceKm(unittest.TestCase):

    @classmethod #Levantamiento de servidor y cliente
    def setUpClass(cls):
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_DistanceServiceServicer_to_server(DistanceServicer(), cls.server)
        cls.port = cls.server.add_insecure_port('[::]:0')
        cls.server.start()
        
        cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
        cls.stub = pb2_grpc.DistanceServiceStub(cls.channel)

    @classmethod #Cierre de servidor y cliente
    def tearDownClass(cls):
        cls.channel.close()
        cls.server.stop(None)

    def test_no_distance_km(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),  
            destination=pb2.Position(latitude=0, longitude=0),
            unit="km"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, 0)
        self.assertEqual(response.unit, "km")

    def test_very_close_distance_km(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0.000001, longitude=0.000001),
            unit="km"  
        )
        
        response = self.stub.geodesic_distance(message)
        self.assertAlmostEqual(response.distance, 0.000144, None, "Los resultados no coinciden", 0.001)
    
    def test_very_far_distance_km(self): #Antípoda Chile y Asia central
        message = pb2.SourceDest(
            source=pb2.Position(latitude=45, longitude=90),
            destination=pb2.Position(latitude=-45, longitude=-90),
            unit="km"
        )
        
        response = self.stub.geodesic_distance(message)
        self.assertAlmostEqual(response.distance, 20020, None, "Los resultados no coinciden", 10)

class TestDistanceNm(unittest.TestCase):

    @classmethod #Levantamiento de servidor y cliente
    def setUpClass(cls):
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_DistanceServiceServicer_to_server(DistanceServicer(), cls.server)
        cls.port = cls.server.add_insecure_port('[::]:0')
        cls.server.start()
        
        cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
        cls.stub = pb2_grpc.DistanceServiceStub(cls.channel)

    @classmethod #Cierre de servidor y cliente
    def tearDownClass(cls):
        cls.channel.close()
        cls.server.stop(None)

    def test_no_distance_nm(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),  
            destination=pb2.Position(latitude=0, longitude=0),
            unit="nm"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, 0)
        self.assertEqual(response.unit, "nm")

    def test_very_close_distance_nm(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0.000001, longitude=0.000001),
            unit="nm"  
        )
        
        response = self.stub.geodesic_distance(message)
        self.assertAlmostEqual(response.distance, 0.0000849, None, "Los resultados no coinciden", 0.0005)
    
    def test_very_far_distance_nm(self): #Antípoda Chile y Asia central
        message = pb2.SourceDest(
            source=pb2.Position(latitude=45, longitude=90),
            destination=pb2.Position(latitude=-45, longitude=-90),
            unit="nm"
        )
        
        response = self.stub.geodesic_distance(message)
        self.assertAlmostEqual(response.distance, 10809.93, None, "Los resultados no coinciden", 5)

def suite():
    test_suite = unittest.TestSuite()

    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPositionLatitude))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPositionLongitude))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPositionTypeValues))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDistanceClient))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDistanceKm))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDistanceNm))
    
    return test_suite

if __name__ == "__main__": 
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())