import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# telefono, titulo, desc, multimedia
class DirectoryHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            print(f"Directorio {'creado' if event.event_type == 'created' else 'modificado'}: {event.src_path}")
        elif os.path.isfile(event.src_path):
            print(f"Archivo {'creado' if event.event_type == 'created' else 'modificado'}: {event.src_path}")
        else:
            print(f"Evento desconocido: {event.event_type} - {event.src_path}")
        
        # Aquí puedes agregar el código para hacer algo cuando ocurre cualquier cambio en el directorio
        # Por ejemplo, puedes copiar archivos, enviar una notificación, etc.

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