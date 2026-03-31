from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QListWidget,
    QStackedWidget,
    QFrame
) 

from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QTimer, Signal, Qt, QThread
import requests
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from pathlib import Path

class RecognitionWorker(QThread):
    success = Signal(dict, bytes)
    error = Signal(str)
    
    def __init__(self, api_client, meme_name, confidence):
        super().__init__()
        self.api_client = api_client
        self.meme_name = meme_name
        self.confidence = confidence
        
    def run(self):
        try:
            result = self.api_client.recognize_meme(self.meme_name, self.confidence)
            
            media_url = result["media_url"]
            full_url = self.api_client.build_url(media_url)
            
            response = requests.get(full_url, timeout=10)
            response.raise_for_status()
            
            image_data = response.content
            
            self.success.emit(result, image_data)
            
        except Exception as e:
            self.error.emit(str(e))
            
            
class CameraWorker(QThread):
    frame_ready = Signal(QImage, object)
    error = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.cap = None
        self.running = False
        
    def run(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.error.emit("Não foi possivel abrir a camera")
            return
        
        self.running = True
        
        while self.running:
            ret, frame = self.cap.read()
            
            if not ret:
                continue
            
            frame  = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            
            qt_image = QImage(
                frame.data,
                w,
                h,
                bytes_per_line,
                QImage.Format_RGB888
            )
            
            self.frame_ready.emit(qt_image.copy(), frame.copy())
            
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
    def stop(self):
        self.running = False
        self.wait()

class MainWindow(QWidget):
    def __init__(self, api_client, user_data):
        
      super().__init__()

      self.api_client = api_client
      self.user_data = user_data
      
      self.recognition_worker = None
      self.recognition_in_progress = False
      
      self.camera_on = False
      self.camera_worker = None
      
      self.auto_recognition_enabled = False
      
      self.current_frame = None
      
      self.last_detected_meme = None
      
      self.last_face_box = None
      self.smoothed_face_box = None
      
      self.last_detected_label = ""
      
      self.face_detector =  None
      self.init_mediapipe_face_detector()
      
      self.camera_button = QPushButton("Ligar camera")
      self.camera_button.clicked.connect(self.toggle_camera)
      
      self.setWindowTitle("MemeCam - Tela Principal")
      self.resize(1000, 650)
      
      #layout principal
      self.main_layout = QHBoxLayout()
      
      self.sidebar = QVBoxLayout()
      
      self.recognition_page_button = QPushButton("Reconhecimento")
      self.history_page_button = QPushButton("Historico")
      
      self.recognition_page_button.clicked.connect(self.show_recognition_page)
      self.history_page_button.clicked.connect(self.show_history_page)
      
      self.sidebar.addWidget(self.recognition_page_button)
      self.sidebar.addWidget(self.history_page_button)
      self.sidebar.addStretch()
      
      self.sidebar_frame = QFrame()
      self.sidebar_frame.setLayout(self.sidebar)
      self.sidebar_frame.setFixedWidth(180)
      self.sidebar_frame.setStyleSheet("border-right: 1px solid white; padding: 8px;")
      
      self.stacked_widget = QStackedWidget()
      
      self.layout = QVBoxLayout()
      
      self.user_label = QLabel(
          f"Usuário logado: {self.user_data['username']} ({self.user_data['email']})"
      )
      
      #====parte do reconhecimento de meme=====
      
      self.recognition_page = QWidget()
      self.recognition_layout = QVBoxLayout()
      
      self.meme_input = QLineEdit()
      self.meme_input.setPlaceholderText("Digite o nome do meme, ex: side_ey")
      
      self.confidence_input = QLineEdit()
      self.confidence_input.setPlaceholderText("Digite a confiança, ex: 0.91 ")
      
      self.recognize_button = QPushButton("Testar Recognition Manual")
      self.recognize_button.clicked.connect(self.handle_recognition)
      
      self.auto_button = QPushButton("Ativar reconhecimento automatico")
      
      self.recognition_timer = QTimer()
      self.recognition_timer.timeout.connect(self.run_auto_recognition)
      self.auto_button.clicked.connect(self.toggle_auto_recognition)
      
      self.result_label = QLabel("Resultado aparecerá aqui")
      
      
      #====parte da camera=====
      self.imagem_label = QLabel("Imagem do meme aparecerá aqui")
      self.imagem_label.setFixedHeight(200)
      self.imagem_label.setStyleSheet("border: 1px solid gray;")
      self.imagem_label.setAlignment(Qt.AlignCenter)  
      
      self.camera_label = QLabel("Camera desligada")
      self.camera_label.setFixedHeight(220)
      self.camera_label.setStyleSheet("border: 1px solid blue;")
      self.camera_label.setAlignment(Qt.AlignCenter)
      
      self.recognition_layout.addWidget(self.user_label)
      self.recognition_layout.addWidget(self.meme_input)
      self.recognition_layout.addWidget(self.confidence_input)
      self.recognition_layout.addWidget(self.recognize_button)
      self.recognition_layout.addWidget(self.result_label)
      self.recognition_layout.addWidget(self.imagem_label)
      self.recognition_layout.addWidget(self.auto_button)
      self.recognition_layout.addWidget(self.camera_label)
      self.recognition_layout.addWidget(self.camera_button)
      
      self.recognition_page.setLayout(self.recognition_layout)
      
      
      
      
      
     #====parte do historico=====
     
      self.history_page = QWidget()
      self.history_layout = QVBoxLayout()
      
      
      self.history_title = QLabel("Historico:")
      self.history_list = QListWidget()
      
      self.history_layout.addWidget(self.history_title)
      self.history_layout.addWidget(self.history_list)
      
      self.history_page.setLayout(self.history_layout)
      
      
      self.stacked_widget.addWidget(self.recognition_page)
      self.stacked_widget.addWidget(self.history_page)
      
      self.main_layout.addWidget(self.sidebar_frame)
      self.main_layout.addWidget(self.stacked_widget)
      
      self.setLayout(self.main_layout)
      
      self.show_recognition_page()
    
      
    # funcao de navegação
    def show_recognition_page(self):
        self.stacked_widget.setCurrentWidget(self.recognition_page)
        
    def show_history_page(self):
        self.stacked_widget.setCurrentWidget(self.history_page)
        self.load_history()
    # funções do reconhecimento manual
      
    def execute_recognition(self, meme_name, confidence):
        if self.recognition_in_progress:
            return
        
        self.recognition_in_progress = True
        self.recognize_button.setEnabled(False)
        self.auto_button.setEnabled(False)
        self.result_label.setText("Reconhecendo...")
        
        self.recognition_worker = RecognitionWorker(
            self.api_client,
            meme_name,
            confidence
        )
        
        self.recognition_worker.success.connect(self.on_recognition_success)
        self.recognition_worker.error.connect(self.on_recognition_error)
        self.recognition_worker.finished.connect(self.on_recognition_finished)
        
        self.recognition_worker.start()
        
    def on_recognition_finished(self):
        self.recognition_in_progress = False
        self.recognition_worker = None
        self.recognize_button.setEnabled(True)
        self.auto_button.setEnabled(True)

        
        
    def on_recognition_success(self, result, image_data):
        self.result_label.setText(
            f"Meme: {result['meme_name']} | "
            f"Confidence: {result['confidence']} | "
            f"Tipo: {result['media_type']}"
        )
         
        pixmap = QPixmap()
        loaded = pixmap.loadFromData(image_data)
        
        if not loaded:
            QMessageBox.warning(
                self,
                "Erro",
                "A midia foi encontrada, mas não pode ser carregada como imagem"
            )
            return
            
        self.imagem_label.setPixmap(
                pixmap.scaled(
                self.imagem_label.width(),
                self.imagem_label.height(),
                Qt.KeepAspectRatio
                
            )
        )
            
        
    def on_recognition_error(self, error_message):
        QMessageBox.critical(self, "Erro", f"Falha na reconition: {error_message}")
        
        self.result_label.setText("Resultado aparecerá aqui")
      
    def handle_recognition(self):
        meme_name = self.meme_input.text().strip()
        confidence_text = self.confidence_input.text().strip()
        
        if not meme_name or not confidence_text:
            QMessageBox.warning(self, "Atenção", "Preencha meme e confidence")
            return
        
        try:
            confidence = float(confidence_text)
            self.execute_recognition(meme_name, confidence)
            
        except ValueError:
            QMessageBox.warning(self, "Erro", "Confidence deve ser numero")
        except Exception as error:
            QMessageBox.critical(self, "Erro", f"Falha no recognition: {error}")
            
    #funcoes da camera        
            
    def on_camera_frame(self, qt_image, frame):
        self.current_frame = frame
        
        display_frame = frame.copy()
        
        if self.last_face_box is not None:
            x,y,w,h = self.last_face_box
        
            cv2.rectangle(display_frame,
                        (x, y),
                        (x + w, y + h),
                        (0,255, 0),
                        2
                        )
        
            if self.last_detected_label:
                cv2.putText(
                    display_frame,
                    self.last_detected_label,
                    (x,y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.8,
                    (0, 255, 0),
                    2
                 )
            
        h, w, ch = display_frame.shape
        bytes_per_line = ch * w
            
        qt_image = QImage(
            display_frame.data, 
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        ).copy()
        
        pixmap = QPixmap.fromImage(qt_image)
        
        self.camera_label.setPixmap(
            pixmap.scaled
            (
                self.camera_label.width(),
                self.camera_label.height(),
                Qt.KeepAspectRatio
            )
        )
        
    def init_mediapipe_face_detector(self):
        model_path = Path(__file__).resolve().parent.parent / "models" / "face_detection_short_range.tflite"

        print("MODEL PATH:", model_path)
        print("MODEL EXISTS:", model_path.exists())

        if not model_path.exists():
            raise FileNotFoundError(f"Modelo não encontrado em: {model_path}")

        base_options = python.BaseOptions(
            model_asset_path=str(model_path)
        )

        options = vision.FaceDetectorOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            min_detection_confidence=0.6
        )

        self.face_detector = vision.FaceDetector.create_from_options(options)
        
    def detect_meme_from_frame(self, frame):
        if frame is None or self.face_detector is None:
            return None
        
        frame_height,frame_width, _ = frame.shape
        
        mp_image = mp.Image(
            image_format = mp.ImageFormat.SRGB,
            data=frame
        )
        
        results = self.face_detector.detect(mp_image)
        
        if not results.detections:
            return None
        
        detection = max(
            results.detections,
            key=lambda d: d.bounding_box.width *
                          d.bounding_box.height
        )
        
        bbox = detection.bounding_box
        
        x = int(bbox.origin_x)
        y = int(bbox.origin_y)
        w = int(bbox.width)
        h = int(bbox.height)
        
        x = max(0,x)
        y = max(0,y)
        w = max(1,w)
        h = max(1,h)
        
        face_area = w * h
        frame_area = frame_width * frame_height
        ratio = face_area / frame_area
        
        face_center_x = x + (w // 2)
        
        left_limit = frame_width * 0.35
        right_limit = frame_width * 0.65
        
        if face_center_x < left_limit:
            meme_name = "side_ey"
            confidence = 0.80
            
        elif face_center_x > right_limit:
            meme_name = "sus"
            confidence = 0.76
            
        elif ratio > 0.18:
            meme_name = "closed_face"
            confidence = 0.82
            
        else:
            meme_name = "confused__"
            confidence = 0.62
            
        return {
            "meme_name": meme_name,
            "confidence": confidence,
            "face_box": (x, y, w, h)
        }
        
        
    def smooth_face_box(self, new_box, alpha=0.75):
        if new_box is None:
            self.smoothed_face_box = None
            return None

        if self.smoothed_face_box is None:
            self.smoothed_face_box = new_box
            return new_box

        old_x, old_y, old_w, old_h = self.smoothed_face_box
        new_x, new_y, new_w, new_h = new_box

        x = int(alpha * old_x + (1 - alpha) * new_x)
        y = int(alpha * old_y + (1 - alpha) * new_y)
        w = int(alpha * old_w + (1 - alpha) * new_w)
        h = int(alpha * old_h + (1 - alpha) * new_h)

        self.smoothed_face_box = (x, y, w, h)
        return self.smoothed_face_box    
        
        
    def on_camera_error(self, error_message):
        QMessageBox.warning(self, "Erro na camera", error_message)
        self.stop_camera()
        
    def on_camera_finished(self):
        self.camera_on = False
        self.camera_label.setText("camera desligada")
            
    def toggle_camera(self):
        if not self.camera_on:
            self.start_camera()
        else:
            self.stop_camera()      
            
            
            
    def start_camera(self):
        if self.camera_on:
            return
        
        self.camera_worker = CameraWorker()
        self.camera_worker.frame_ready.connect(self.on_camera_frame)
        self.camera_worker.error.connect(self.on_camera_error)
        self.camera_worker.finished.connect(self.on_camera_finished)
        
        self.camera_on = True
        self.camera_button.setText("Desligar camera")    
        self.camera_label.setText("Abrindo camera...")
        self.camera_worker.start()
        
        
    def stop_camera(self):
        
        if self.camera_worker is not None:
            self.camera_worker.stop()
            self.camera_worker = None
            
        self.camera_on = False
        self.camera_button.setText("Ligar camera")
            
        self.camera_label.clear()
        self.camera_label.setText("camera desligada")
        
        self.disable_auto_recognition()
            
        
    #funções do reconhecimento automatico
    
    def toggle_auto_recognition(self):
        
        if not self.camera_on:
            self.disable_auto_recognition()
            QMessageBox.warning(
                self,
                "Erro",
                "Ligue a camera para o reconhecimento automatico"
                )
            return
        
        if not self.auto_recognition_enabled:
            self.auto_recognition_enabled = True
            self.auto_button.setText("Desativar reconhecimento automatico")
            self.recognition_timer.start(5000)
            
        else:
            self.disable_auto_recognition()
    
    def run_auto_recognition(self):
        
        if self.recognition_in_progress:
            return
        
        if not self.camera_on:
            self.disable_auto_recognition()
            return
        
        if self.current_frame is None:
            return
        
        detection = self.detect_meme_from_frame(self.current_frame)
        print("Resultado detecção:", detection)
        
        if detection is None:
            self.last_detected_meme = None
            self.smoothed_face_box = None
            self.last_face_box = None
            self.last_detected_label = ""
            self.result_label.setText("Nenhum rosto detectado")
            return
        
        meme_name = detection["meme_name"]
        confidence = detection["confidence"]
        print("AUTO RECOGNITION CHAMADO")
        print("Tem frame?", self.current_frame is not None)
        
        self.last_face_box = self.smooth_face_box(detection["face_box"])
        self.last_detected_label = detection["meme_name"]
        
        if meme_name == self.last_detected_meme:
            return
        
        self.last_detected_meme = meme_name
        self.execute_recognition(meme_name, confidence)
        

        
        
        
    def disable_auto_recognition(self):
        self.auto_recognition_enabled = False
        self.recognition_timer.stop()
        self.auto_button.setText("Ativar reconhecimento automatico")
        
        
    def load_history(self):
        try:
            history_items = self.api_client.get_my_history()
            self.history_list.clear()

            for item in history_items:
                text = (
                    f"Meme: {item['meme_name']} | "
                    f"Confidence: {item['confidence']} | "
                    f"Tipo: {item['media_type']} | "
                    f"data: {item['created_at']}"
                )
                self.history_list.addItem(text)

        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Falha ao carregar histórico: {e}")
        
    def closeEvent(self, event):
        self.disable_auto_recognition()
        
        if self.face_detector is not None:
            self.face_detector.close()
            self.face_detector = None
        
        if self.camera_worker is not None:
            self.camera_worker.stop()
            self.camera_worker = None
        if self.recognition_worker is not None and self.recognition_worker.isRunning():
            self.recognition_worker.wait()
            
        event.accept()