import pydicom
import csv
import pydicom
import matplotlib.pyplot as plt
from PIL import Image

# Cargar el archivo DICOM
dicom_file = pydicom.dcmread("IMG_20240402_1_5.dcm")

# Obtener la información deseada del encabezado DICOM
patient_name = dicom_file.PatientName
patient_id = dicom_file.PatientID
study_date = dicom_file.StudyDate

dicom_file.phone = "1234567890"

# Agregar una nueva propiedad personalizada
dicom_file.phone = "1234567890"

print("ID del Paciente: ", patient_id)
print("Nombre del Paciente: ", patient_name)
print("Teléfono: ", dicom_file.phone)

print(dicom_file)

# Acceder a los datos de píxeles
pixel_data = dicom_file.pixel_array
# Crear un objeto de imagen PIL a partir de los datos de píxeles
image = Image.fromarray(pixel_data)

# Guardar la imagen en formato JPEG
image.save(str(patient_name) + ".jpg", format='JPEG')
# Visualizar la imagen
plt.imshow(pixel_data, cmap='gray')
plt.axis('off')
plt.show()

# ... Obtener otros campos según sea necesario

# Crear una lista con los datos extraídos
data = [patient_name, patient_id, study_date]

# Especificar la ruta y el nombre del archivo CSV de salida
csv_file = "out2.csv"

# Escribir los datos en el archivo CSV
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Nombre del Paciente", "ID del Paciente", "Fecha del Estudio"])
    writer.writerow(data)



print("Datos exportados a CSV exitosamente.")