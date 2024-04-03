import time
import requests
import io
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pydicom
import matplotlib.pyplot as plt
from PIL import Image
import base64
import json

url = 'https://umss-api.terio.xyz/api/ultrasonidos'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

class DirectoryHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.src_path.endswith(".dcm"):
            return

        print(f"Archivo creado: {event.src_path}")
        self.process_dcm_file(event.src_path)

    def on_modified(self, event):
        if not event.src_path.endswith(".dcm"):
            return

        print(f"Archivo modificado: {event.src_path}")
        self.process_dcm_file(event.src_path)

    def process_dcm_file(self, file):
        # Crear un diccionario para almacenar la información del paciente
        study_data = {
            "titulo": "Dumb title",
            "folio": "",
            "descripcion": "",
            "telefono_paciente": "",
            "fecha_de_nacimiento": "",
            "imagenes": [],
            "videos": []
        }

        # Cargar el archivo DICOM
        dicom_file = pydicom.dcmread(file)
        print(dicom_file)

        # Obtener la información deseada del encabezado DICOM
        patient_id = dicom_file.PatientID
        patient_name = dicom_file.PatientName
        patient_birthdate = dicom_file.PatientBirthDate
        study_id = dicom_file.StudyID
        study_date = dicom_file.StudyDate

        if hasattr(dicom_file, 'PatientPhoneNumber'):
            patient_phone = dicom_file.PatientPhoneNumber
        else:
            patient_phone = '4431466216'

        print("ID del Paciente: ", patient_id)
        print("Nombre del Paciente: ", patient_name)
        print("Fecha de nacimiento: ", patient_birthdate)
        print("Teléfono: ", patient_phone)
        print("ID del estudio: ", study_id)
        print("Fecha del estudio: ", study_date)

        # Actualizar la información del paciente
        study_data["folio"] = str(study_id)
        study_data[
            "descripcion"] = f"Estudio del paciente {patient_name} con ID {patient_id} realizado en la fecha {study_date}"
        study_data["telefono_paciente"] = str(patient_phone)
        study_data["fecha_de_nacimiento"] = str(patient_birthdate)

        # Acceder a los datos de píxeles
        pixel_data = dicom_file.pixel_array
        # Crear un objeto de imagen PIL a partir de los datos de píxeles
        image = Image.fromarray(pixel_data)
        # Guardar la imagen en formato JPEG
        image_filename = f"{patient_id}_{study_date}.jpg"
        image.save(image_filename, format='JPEG')
        # Convertir la imagen a formato base64
        with open(image_filename, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        # Agregar la imagen al diccionario
        study_data["imagenes"].append(encoded_image)

        # Enviar la peticion
        x = requests.post(url, json=study_data, headers=headers)
        print(x.content)

        # Convertir el diccionario a formato JSON
        json_data = json.dumps(study_data, indent=4)

        # Guardar el JSON en un archivo
        with open(f"{patient_name}.json", "w") as json_file:
            json_file.write(json_data)
        print("Datos exportados a JSON exitosamente.")
        # print("JSON generado:")
        # print(json_data)

        # Verificar las imágenes decodificándolas desde el JSON
        decoded_patient_data = json.loads(json_data)
        for i, encoded_image in enumerate(decoded_patient_data["imagenes"]):
            # Decodificar la imagen en base64
            decoded_image = base64.b64decode(encoded_image)
            # Crear un objeto de imagen PIL desde los datos decodificados
            image = Image.open(io.BytesIO(decoded_image))
            # Mostrar la imagen
            plt.imshow(image)
            plt.title(f"Imagen {i + 1}")
            plt.axis('off')
            plt.show()
            # Guardar la imagen decodificada (opcional)
            image.save(f"decoded_image_{i + 1}.jpg")


if __name__ == "__main__":
    # Crea una instancia del observador
    observer = Observer()
    # Crea una instancia del controlador de eventos
    event_handler = DirectoryHandler()
    # Registra el controlador de eventos para el directorio actual
    observer.schedule(event_handler, path='./testing_dir', recursive=True)
    # Inicia el observador
    observer.start()
    try:
        # Mantiene el observador en ejecución hasta que se presione Ctrl+C
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        # Detiene el observador cuando se presiona Ctrl+C
        observer.stop()
    # Espera a que el observador termine
    observer.join()
