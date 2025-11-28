import muselsl as muse
from muselsl import record, list_muses
import time
import threading
import signal
import sys

class EEGRecorder:
    def __init__(self, duration, filename):
        self.date_str = time.strftime("%Y%m%d")
        self.duration = duration
        self.filename = f"data/cualitative/cual_survey_{filename}_{self.date_str}.csv"
        self.recording_start_time = None # None elimina ambiguedad. NO HA INICIADO.
        self.is_recording = False
        self.additional_sensors = False
    
    # 1. CONFIRMAR PAIRING CON MUSE
    def confirm_pairing(self):
        paired = muse.list_muses()
        mi_muse = paired[0]
        if not paired:
            print(f"NO SE ENCONTRÓ LA MUSE 2.")
            return None
        else:
            print(f"SE ENCONTRÓ LA MUSE 2: {mi_muse['name']} - {mi_muse['address']}")
            return mi_muse

    def activate_additionals(self):
        mi_muse = self.confirm_pairing()
        if mi_muse:
            print("ACTIVANDO GIROSCOPIO...")
            self.additional_sensors = True
        
        print("No se encontró ninguna Muse, activación de giroscopio fallida.")
        self.additional_sensors = False
    
    
    def start_recording(self, view_stream=False, ):
        mi_muse = self.confirm_pairing()
        if mi_muse:
            print(f"******** Recording Started for {self.duration} seconds ********")
            # Variables de update de recordign #
            self.recording_start_time = time.time()
            if view_stream:
                muse.stream(
                    ppg_enabled=True,
                    acc_enabled=True,
                    gyro_enabled=True,
                )
            self.is_recording = True
            record(
                duration=self.duration,
                filename=self.filename
            )
            self.is_recording = False
            print(f"Recording Successfully Saved. Data saved at: {self.filename}")
            if view_stream:
                print("Stopping View Stream...")
        else:
            print("No se pudo iniciar la grabación ❌ Muse no está emparejada.")
    
    def recording_timer(self):
        """
        Verifica si la grabación aún está activa basándose en el tiempo transcurrido.
        Returns:
            tuple: (is_active, elapsed_time, remaining_time)
        """
        # Base Case: No hemos iniciado la grabación
        if not self.recording_start_time:
            return (False, 0, 0)
        
        elapsed_time = time.time() - self.recording_start_time # INTEGRAL (?) DELTA T
        remaining_time = max(0, self.duration - elapsed_time) # Clampeaa a 0.
        is_active = elapsed_time < self.duration and self.is_recording
        
        return (is_active, elapsed_time, remaining_time)
    
    def get_recording_progress(self):
        """
        Obtiene el progreso de la grabación como porcentaje.
        Returns:
            float: Porcentaje de progreso (0-100)
        """
        is_active, elapsed, remaining = self.recording_timer()
        if self.duration == 0:
            return 100.0
        progress = (elapsed / self.duration) * 100
        return min(progress, 100.0) # calculamos min para encapsular en el rango 0-100.
    
    def wait_for_recording(self, update_interval=1.0):
        """
        Loop que espera hasta que la grabación termine, 
        mostrando el progreso cada update_interval segundos.
        
        Args:
            update_interval: Tiempo en segundos entre actualizaciones de progreso
        """
        if not self.is_recording:
            print("No hay grabación activa.")
            return
        
        print("\n--- Recording Progress ---")
        while self.is_recording:
            is_active, elapsed, remaining = self.recording_timer()
            if not is_active:
                break
            
            progress = self.get_recording_progress()
            print(f"Tiempo transcurrido: {elapsed:.1f}s | Restante: {remaining:.1f}s | Progreso: {progress:.1f}%")
            time.sleep(update_interval)
        
        print("Grabación completada :) .\n")
    
    def view_stream(self, duration=None):
        """
        Visualiza el stream de EEG en tiempo real.
        
        Args:
            duration: Tiempo en segundos para visualizar (None = indefinido hasta cerrar ventana)
        """
        mi_muse = self.confirm_pairing()
        if mi_muse:
            print("******** Viewing Stream ********")
            if duration:
                print(f"Visualizando stream por {duration} segundos...")
                
                # Iniciar timer
                self.recording_start_time = time.time()
                self.is_recording = True
                
                # Ejecutar view() en un thread separado porque es blocking
                # Estamos dándole un thread nuevo para que se ejecute en paralelo.
                view_thread = threading.Thread(target=muse.view, daemon=True)
                view_thread.start()
                
                # Monitorear el tiempo mientras view() corre
                while self.is_recording:
                    is_active, elapsed, remaining = self.recording_timer()
                    if elapsed >= duration:
                        self.is_recording = False
                        print(f"\n Visualización completada por ({duration}s).")
                        print("CERRARla ventana MANUALMENTE para terminar.")
                        break
                    time.sleep(0.1)
                
            else:
                print("Visualizando stream (cierra la ventana para terminar)...")
                muse.view()
            
        else:
            print("No se pudo iniciar la visualización ❌ Muse no está emparejada.")


        

        

    




    
  