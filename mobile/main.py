import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.network.urlrequest import UrlRequest


class DisasterAidMobileApp(App):
    def build(self):
        self.title = "DisasterAid AI"
        self.root_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Title Label
        self.root_layout.add_widget(
            Label(
                text="DisasterAid AI Mobile App",
                font_size="20sp",
                size_hint_y=None,
                height=40,
            )
        )

        # API Endpoint configuration
        api_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=40, spacing=5
        )
        api_layout.add_widget(Label(text="API URL:", size_hint_x=0.2))
        self.api_input = TextInput(
            text="http://10.0.2.2:5000/api/process/file",
            multiline=False,
            size_hint_x=0.8,
        )
        api_layout.add_widget(self.api_input)
        self.root_layout.add_widget(api_layout)

        # File selection buttons
        btn_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50, spacing=10
        )
        self.select_btn = Button(
            text="Select Image / Audio File", on_release=self.show_file_chooser
        )
        self.upload_btn = Button(
            text="Process Report File", on_release=self.process_file, disabled=True
        )
        btn_layout.add_widget(self.select_btn)
        btn_layout.add_widget(self.upload_btn)
        self.root_layout.add_widget(btn_layout)

        # Selected File Label
        self.file_label = Label(text="No file selected", size_hint_y=None, height=30)
        self.root_layout.add_widget(self.file_label)

        # Result Display Area
        self.root_layout.add_widget(
            Label(text="Structured JSON Result:", size_hint_y=None, height=20)
        )
        self.result_input = TextInput(
            text="Result will be shown here...", readonly=True, multiline=True
        )
        self.root_layout.add_widget(self.result_input)

        self.selected_file_path = None
        return self.root_layout

    def show_file_chooser(self, instance):
        content = BoxLayout(orientation="vertical")
        file_chooser = FileChooserIconView(
            filters=["*.png", "*.jpg", "*.jpeg", "*.mp3", "*.wav", "*.pdf"]
        )
        content.add_widget(file_chooser)

        select_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=40, spacing=10
        )
        cancel_btn = Button(text="Cancel")
        confirm_btn = Button(text="Select")
        select_layout.add_widget(cancel_btn)
        select_layout.add_widget(confirm_btn)
        content.add_widget(select_layout)

        popup = Popup(title="Select File", content=content, size_hint=(0.9, 0.9))

        cancel_btn.bind(on_release=popup.dismiss)

        def confirm_selection(btn_inst):
            if file_chooser.selection:
                self.selected_file_path = file_chooser.selection[0]
                self.file_label.text = (
                    f"Selected: {os.path.basename(self.selected_file_path)}"
                )
                self.upload_btn.disabled = False
            popup.dismiss()

        confirm_btn.bind(on_release=confirm_selection)
        popup.open()

    def process_file(self, instance):
        if not self.selected_file_path:
            self.result_input.text = "Error: Please select a file first."
            return

        self.result_input.text = "Uploading and processing file..."

        # Read the file data
        try:
            with open(self.selected_file_path, "rb") as f:
                file_data = f.read()
        except Exception as e:
            self.result_input.text = f"Error reading file: {e}"
            return

        url = self.api_input.text.strip()
        filename = os.path.basename(self.selected_file_path)

        # Build multipart/form-data payload
        boundary = "---DisasterAidAIBoundary"
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}

        # Simple multipart body generation
        body = []
        body.append(f"--{boundary}".encode("utf-8"))
        body.append(
            f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode(
                "utf-8"
            )
        )

        # Determine content type
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        content_type = "application/octet-stream"
        if ext in ["png", "jpg", "jpeg"]:
            content_type = "image/jpeg"
        elif ext in ["mp3", "wav"]:
            content_type = "audio/mpeg"
        elif ext == "pdf":
            content_type = "application/pdf"

        body.append(f"Content-Type: {content_type}\r\n".encode("utf-8"))
        body.append(file_data)
        body.append(f"\r\n--{boundary}--".encode("utf-8"))

        req_body = b"".join(body)

        def on_success(req, result):
            self.result_input.text = json.dumps(result, indent=2)

        def on_failure(req, result):
            self.result_input.text = f"Request failed: {result}"

        def on_error(req, error):
            self.result_input.text = f"Error communicating with local server: {error}\n\nFalling back to local simulation...\n\n"
            # Offline mock parser logic
            self.simulate_offline_result(filename)

        UrlRequest(
            url,
            req_body=req_body,
            req_headers=headers,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error,
            method="POST",
        )

    def simulate_offline_result(self, filename):
        # Simulate local parsing
        disaster_type = "Flood"
        severity = "High"
        priority_score = 65
        location = "Local Mobile Simulation"
        people_trapped = 3

        if "fire" in filename.lower():
            disaster_type = "Fire"
            severity = "Critical"
            priority_score = 85
        elif "quake" in filename.lower() or "earthquake" in filename.lower():
            disaster_type = "Earthquake"
            severity = "High"
            priority_score = 75

        mock_record = {
            "disaster_type": disaster_type,
            "people_trapped": people_trapped,
            "children": 1,
            "elderly": 0,
            "injuries": True,
            "medical_help": True,
            "food_needed": True,
            "water_needed": True,
            "location": location,
            "severity": severity,
            "priority_score": priority_score,
            "status": "Immediate Rescue" if priority_score >= 75 else "Urgent",
            "mock_mode": True,
            "extraction_engine": "local_mobile_simulation",
            "extracted_text": f"Simulation of offline parsing for mobile file {filename}.",
        }
        self.result_input.text += json.dumps(mock_record, indent=2)


if __name__ == "__main__":
    DisasterAidMobileApp().run()
