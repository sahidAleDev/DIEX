import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pydicom
import csv
import matplotlib.pyplot as plt
from PIL import Image
import io
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pydicom
import csv
import matplotlib.pyplot as plt
from PIL import Image
import base64
import json

class DirectoryHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory and event.event_type == 'created':
            print(f"Directorio creado: {event.src_path}")
            # Aquí puedes agregar el código para procesar los archivos .dcm en el directorio
            self.process_dcm_files(event.src_path)
        elif os.path.isfile(event.src_path):
            print(f"Archivo {'creado' if event.event_type == 'created' else 'modificado'}: {event.src_path}")
        else:
            print(f"Evento desconocido: {event.event_type} - {event.src_path}")

    def process_dcm_files(self, directory):
        # Obtener una lista de todos los archivos .dcm en el directorio
        dcm_files = [file for file in os.listdir(directory) if file.endswith(".dcm")]
        
        # Crear un diccionario para almacenar la información del paciente
        patient_data = {
            "nombre_paciente": "",
            "descripcion": "",
            "imagenes": [],
            "videos": []
        }
        
        # Procesar cada archivo .dcm
        for filename in dcm_files:
            file_path = os.path.join(directory, filename)
            # Cargar el archivo DICOM
            dicom_file = pydicom.dcmread(file_path)
            # Obtener la información deseada del encabezado DICOM
            patient_name = dicom_file.PatientName
            patient_id = dicom_file.PatientID
            study_date = dicom_file.StudyDate
            dicom_file.phone = "1234567890"  # Agregar una nueva propiedad personalizada
            print("ID del Paciente: ", patient_id)
            print("Nombre del Paciente: ", patient_name)
            print("Teléfono: ", dicom_file.phone)
            print(dicom_file)
            
            # Actualizar la información del paciente
            patient_data["nombre_paciente"] = str(patient_name)
            patient_data["descripcion"] = f"Estudio del paciente {patient_name} con ID {patient_id} realizado en la fecha {study_date}"
            
            # Acceder a los datos de píxeles
            pixel_data = dicom_file.pixel_array
            # Crear un objeto de imagen PIL a partir de los datos de píxeles
            image = Image.fromarray(pixel_data)
            # Guardar la imagen en formato JPEG
            image_filename = f"{patient_name}_{filename}.jpg"
            image.save(image_filename, format='JPEG')
            # Convertir la imagen a formato base64
            with open(image_filename, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            # Agregar la imagen al diccionario
            patient_data["imagenes"].append(encoded_image)
        
        # Convertir el diccionario a formato JSON
        json_data = json.dumps(patient_data, indent=4)
        # Guardar el JSON en un archivo
        with open(f"{patient_name}.json", "w") as json_file:
            json_file.write(json_data)
        print("Datos exportados a JSON exitosamente.")
        print("JSON generado:")
        print(json_data)

        # Verificar las imágenes decodificándolas desde el JSON
        decoded_patient_data = json.loads(json_data)
        for i, encoded_image in enumerate(decoded_patient_data["imagenes"]):
            # Decodificar la imagen en base64
            decoded_image = base64.b64decode(encoded_image)
            # Crear un objeto de imagen PIL desde los datos decodificados
            image = Image.open(io.BytesIO(decoded_image))
            # Mostrar la imagen
            plt.imshow(image)
            plt.title(f"Imagen {i+1}")
            plt.axis('off')
            plt.show()
            # Guardar la imagen decodificada (opcional)
            image.save(f"decoded_image_{i+1}.jpg")  

if __name__ == "__main__":
    # Obtiene el directorio actual donde se encuentra el archivo de Python
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Crea una instancia del observador
    observer = Observer()
    # Crea una instancia del controlador de eventos
    event_handler = DirectoryHandler()
    # Registra el controlador de eventos para el directorio actual
    observer.schedule(event_handler, current_directory, recursive=False)
    # Inicia el observador
    observer.start()
    try:
        while True:
            # Mantiene el observador en ejecución hasta que se presione Ctrl+C
            pass
    except KeyboardInterrupt:
        # Detiene el observador cuando se presiona Ctrl+C
        observer.stop()
    # Espera a que el observador termine
    observer.join()