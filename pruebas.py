import unittest
import grpc
from concurrent import futures
import distance_unary_pb2_grpc as pb2_grpc
import distance_unary_pb2 as pb2
from distance_grpc_service import DistanceServicer
from geo_location import Position

# Se usará ❗como indicador visual de pruebas con fallos

class TestPositionLatitude(unittest.TestCase):
    # Verifica la validación de latitudes en la clase Position
    # Se considerarán los valores frontera -90 y 90 para las pruebas

    #❗Permite ingresar latitudes con valores negativos fuera de rango
    def test_negative_latitude_out_of_range(self):
        with self.assertRaises(ValueError):
            Position(-90.001, 0, 0)

    def test_positive_latitude_out_of_range(self):
        with self.assertRaises(ValueError):
            Position(90.001, 0, 0)

    def test_negative_latitude_edge(self):
        posicion = Position(-90, 0, 0)
        self.assertEqual(posicion, posicion, "El objeto no se creó correctamente.")
    
    def test_positive_latitude_edge(self):
        posicion = Position(90, 0, 0)
        self.assertEqual(posicion, posicion, "El objeto no se creó correctamente.")

class TestPositionLongitude(unittest.TestCase):
    # Verifica la validación de longitudes en la clase Position
    # Se considerarán los valores frontera -180 y 180 para las pruebas

    #❗Permite ingresar longitudes con valores negativos fuera de rango
    def test_negative_longitude_out_of_range(self):
        with self.assertRaises(ValueError):
            Position(0, -180.001, 0)

    def test_positive_longitude_out_of_range(self):
        with self.assertRaises(ValueError):
            Position(0, 180.001, 0)
    
    def test_positive_longitude_edge(self):
        posicion = Position(0, 180, 0)
        self.assertEqual(posicion, posicion, "El objeto no se creó correctamente.")


class TestPositionBothCoords(unittest.TestCase):
    # Verifica la validación de latitudes y longitudes en conjunto en la clase Position
    # Se considerarán los valores frontera -90, 90 para latitud y -180, 180 para longitud

    #❗Permite ingresar latitudes y longitudes con valores negativos fuera de rango
    def test_negative_coords_out_of_range(self):
        with self.assertRaises(ValueError):
            Position(-90.001, -180.001, 0)

    def test_positive_coords_out_of_range(self):
        with self.assertRaises(ValueError):
            Position(90.001, 180.001, 0)

    def test_latitude_negative_longitude_positive_out_of_range(self):
        with self.assertRaises(ValueError):
            Position(-90.001, 180.001, 0)

    def test_latitude_positive_longitude_negative_out_of_range(self):
        with self.assertRaises(ValueError):
            Position(90.001, -180.001, 0)

    def test_negative_coords_edge(self):
        posicion = Position(-90, -180, 0)
        self.assertEqual(posicion, posicion, "El objeto no se creó correctamente.")
    
    def test_positive_coords_edge(self):
        posicion = Position(90, 180, 0)
        self.assertEqual(posicion, posicion, "El objeto no se creó correctamente.")

class TestPositionTypeValues(unittest.TestCase):
    # Verifica que el comportamiento de la clase Position sea el esperado al ingresar valores de tipo incorrecto

    def test_latitude_as_string(self):
        with self.assertRaises(TypeError):
            Position("90", 0, 0)

    def test_longitude_as_string(self):
        with self.assertRaises(TypeError):
            Position(0, "180", 0) 

    def test_both_coords_as_string(self):
        with self.assertRaises(TypeError):
            Position("90", "180", 0)

    def test_all_coords_as_string(self):
        with self.assertRaises(TypeError):
            Position("90", "180", "0")   
    
    def test_latitude_none_value(self):
        with self.assertRaises(TypeError):
            Position(None, 0, 0)  
    
    def test_longitude_none_value(self):
        with self.assertRaises(TypeError):
            Position(0, None, 0) 

    def test_both_coords_none_value(self):
        with self.assertRaises(TypeError):
            Position(None, None, 0)

    def test_all_coords_none_value(self):
        with self.assertRaises(TypeError):
            Position(None, None, None) 

class TestDistanceClientUnits(unittest.TestCase):

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

    # Verifica que al no especificar unidad, el servicio retorne unidad "km"
    def test_no_unit_specified(self):
        message =  pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=0),
            unit=""
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.unit, "km")
    
    # Verifica que al especificar una unidad inválida, el servicio retorne un error
    def test_invalid_unit(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=0),
            unit="invalid"  
        )
        with self.assertRaises(grpc.RpcError):
            self.stub.geodesic_distance(message)

class TestDistanceInKm(unittest.TestCase):

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

    # Error permitido de 0.001 km ≈ 1 metro. Muy preciso.
    def test_very_close_distance_km(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0.000001, longitude=0.000001),
            unit="km"  
        )
        
        response = self.stub.geodesic_distance(message)
        self.assertAlmostEqual(response.distance, 0.000144, None, "Los resultados no coinciden", 0.001)
    
    #❗El error en el cálculo de la distancia es mayor al esperado (10 km)
    def test_very_far_distance_km(self): # Antípoda polo a polo
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=180),
            unit="km"
        )
        
        response = self.stub.geodesic_distance(message)
        self.assertAlmostEqual(response.distance, 20020, None, "Los resultados no coinciden", 10)

    def test_distance_positive_values_out_of_range_km(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=90.001, longitude=180.001),
            destination=pb2.Position(latitude=91, longitude=181),
            unit="km"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

    def test_distance_negative_values_out_of_range_km(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=-90.001, longitude=-180.001),
            destination=pb2.Position(latitude=-91, longitude=-181),
            unit="km"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")
    
    def test_distance_values_out_of_range_km(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=-90.001, longitude=-180.001),
            destination=pb2.Position(latitude=90.001, longitude=180.001),
            unit="km"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

    def test_distance_source_negative_out_of_range_km(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=-91, longitude=-181),
            destination=pb2.Position(latitude=0, longitude=0),
            unit="km"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

    def test_distance_source_positive_out_of_range_km(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=91, longitude=181),
            destination=pb2.Position(latitude=0, longitude=0),
            unit="km"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

    def test_distance_destination_negative_out_of_range_km(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=-91, longitude=-181),
            unit="km"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

    def test_distance_destination_positive_out_of_range_km(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=91, longitude=181),
            unit="km"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

class TestDistanceInNm(unittest.TestCase):

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

    # Error permitido de 0.0005 nm ≈ 93 cm. Muy preciso.
    def test_very_close_distance_nm(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0.000001, longitude=0.000001),
            unit="nm"  
        )
        
        response = self.stub.geodesic_distance(message)
        self.assertAlmostEqual(response.distance, 0.0000849, None, "Los resultados no coinciden", 0.0005)
    
    #❗El error en el cálculo de la distancia es mayor al esperado (5.5 nm ≈ 10.2 km)
    def test_very_far_distance_nm(self): # Antípoda polo a polo
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=180),
            unit="nm"
        )
        
        response = self.stub.geodesic_distance(message)
        self.assertAlmostEqual(response.distance, 10809.93, None, "Los resultados no coinciden", 5.5)

    def test_distance_positive_values_out_of_range_nm(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=90.001, longitude=180.001),
            destination=pb2.Position(latitude=91, longitude=181),
            unit="nm"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

    def test_distance_negative_values_out_of_range_nm(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=-90.001, longitude=-180.001),
            destination=pb2.Position(latitude=-91, longitude=-181),
            unit="nm"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")
    
    def test_distance_values_out_of_range_nm(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=-90.001, longitude=-180.001),
            destination=pb2.Position(latitude=90.001, longitude=180.001),
            unit="nm"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

    def test_distance_source_negative_out_of_range_nm(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=-91, longitude=-181),
            destination=pb2.Position(latitude=0, longitude=0),
            unit="nm"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

    def test_distance_source_positive_out_of_range_nm(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=91, longitude=181),
            destination=pb2.Position(latitude=0, longitude=0),
            unit="nm"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

    def test_distance_destination_negative_out_of_range_nm(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=-91, longitude=-181),
            unit="nm"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

    def test_distance_destination_positive_out_of_range_nm(self):
        message = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=91, longitude=181),
            unit="nm"
        )

        response = self.stub.geodesic_distance(message)
        self.assertEqual(response.distance, -1, "Los resultados no coinciden")

class TestDistanceNoUnitEqualsKm(unittest.TestCase):

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

    # Verifica que al no especificar unidad, el resultado de distancia sea igual al obtenido al usar "km" al ser la unidad por defecto

    def test_no_distance_no_unit_equals_km(self):
        message_nu = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),  
            destination=pb2.Position(latitude=0, longitude=0),
            unit=""
        )
        message_km = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),  
            destination=pb2.Position(latitude=0, longitude=0),
            unit="km"
        )

        response_nu = self.stub.geodesic_distance(message_nu)
        response_km = self.stub.geodesic_distance(message_km)
        self.assertEqual(response_nu.distance, response_km.distance, "Los resultados no coinciden")

    def test_very_close_distance_no_unit_equals_km(self):
        message_nu = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0.000001, longitude=0.000001),
            unit=""  
        )
        message_km = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0.000001, longitude=0.000001),
            unit="km"
        )
        
        response_nu = self.stub.geodesic_distance(message_nu)
        response_km = self.stub.geodesic_distance(message_km)
        self.assertEqual(response_nu.distance, response_km.distance, "Los resultados no coinciden")
    
    def test_very_far_distance_no_unit_equals_km(self):
        message_nu = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=180),
            unit=""
        )
        message_km = pb2.SourceDest(
            source=pb2.Position(latitude=0, longitude=0),
            destination=pb2.Position(latitude=0, longitude=180),
            unit="km"
        )
        
        response_nu = self.stub.geodesic_distance(message_nu)
        response_km = self.stub.geodesic_distance(message_km)
        self.assertEqual(response_nu.distance, response_km.distance, "Los resultados no coinciden")

def suite():
    test_suite = unittest.TestSuite()

    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPositionLatitude))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPositionLongitude))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPositionBothCoords))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPositionTypeValues))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDistanceClientUnits))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDistanceInKm))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDistanceInNm))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDistanceNoUnitEqualsKm))
    
    return test_suite

if __name__ == "__main__": 
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())