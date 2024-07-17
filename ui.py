from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.graphics import Color, Rectangle
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivy.core.audio  import SoundLoader
from gtts import gTTS
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDRaisedButton,MDRoundFlatIconButton
from kivymd.uix.card import MDSeparator
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserListView
#from plyer import filechooser
from kivy.metrics import dp
#from kivy.uix.filechooser import  FileChooser
from kivymd.uix.picker import MDTimePicker
from datetime import datetime, timedelta
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
import csv
import pygame

KV = '''
ScreenManager:
    MyScreen:
        name: "main"

    EditToneScreen:
        name: "edit_tone"

<MyScreen>:
    BoxLayout:
        orientation: "vertical"
        MDToolbar:
            title: "Alarm Clock"
            elevation: 10
            pos_hint: {"top": 1}
        ScrollView:
            GridLayout:
                id: grid_layout
                cols: 1
                size_hint_y: None
                height: self.minimum_height

        MDFloatingActionButton:
            icon: "plus"
            pos_hint: {"center_x": 0.5, "center_y": 0.1}
            on_release: app.show_time_picker()

<EditToneScreen>:
'''

class MyScreen(Screen):
    pass


class EditToneScreen(Screen):
    pass


class MyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alarm_times = []
        self.alarm_tones = []
        self.sound = None
        self.dialog = None
        self.popup = Popup()
        self.dialog1 = MDDialog()
        pygame.mixer.init()

    def build(self):
        Clock.schedule_interval(self.check_alarms, 1)
        Clock.schedule_once(self.load_alarms, 1)
        return Builder.load_string(KV)

    def load_alarms(self, *args):
        try:
            with open("alarms.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    time_str = row[0]
                    tone = row[1] if len(row) > 1 else "default"
                    active = row[2].lower() == 'true' if len(row) > 2 else True
                    time_12hr = datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
                    self.add_time_to_scrollview(time_12hr, tone, active)
        except FileNotFoundError:
            pass

    def show_time_picker(self):
        time_picker = MDTimePicker()
        time_picker.bind(on_save=self.save_time)
        time_picker.open()

    def save_time(self, instance, time):
        time_str_24 = time.strftime("%H:%M")
        time_str_12 = time.strftime("%I:%M %p")
        tone = "default"  # Default tone for new alarms
        active = True  # Default state for new alarms is active (True)
        with open("alarms.csv", "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time_str_24, tone, active])
        self.add_time_to_scrollview(time_str_12, tone, active)

    def add_time_to_scrollview(self, time_str, tone, active=True):
        grid_layout = self.root.get_screen('main').ids.grid_layout
        box_layout = MDBoxLayout(
            size_hint_y=None,
            height=158,
            padding=52,
        )
    
        label = MDLabel(
            text=f"{time_str}'",
            halign="left",
        )
        switch = MDSwitch(pos_hint={"center_y": 0.5})
        switch.active = active
        switch.bind(active=lambda instance, value: self.on_switch_active(instance, value, time_str))
        divider = MDSeparator(height=1)
        icon_button1 = MDIconButton(
            icon="dots-vertical",
            pos_hint={"center_y": 0.5},
            on_release=lambda x: self.open_menu(icon_button1, time_str, box_layout, divider, tone),
        )
    
        box_layout.add_widget(label)
        box_layout.add_widget(icon_button1)
        box_layout.add_widget(switch)
    
        grid_layout.add_widget(box_layout)
        grid_layout.add_widget(divider)
    
        self.alarm_tones.append({time_str: tone})
        self.alarm_times.append({'time': time_str, 'active': active, 'switch': switch, 'tone': tone})
        

    def open_menu(self, caller, time_str, box_layout, divider, tone):
        menu_items = [
            {
                "text": "alarm tone setting",
                "viewclass": "OneLineListItem",
                "on_release": lambda x='edit': self.menu_callback(x, time_str, box_layout, divider,tone),
            },
            {
                "text": "Delete alarm",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="delete", y=time_str, z=box_layout, a=divider: self.menu_callback(x, y, z, a,tone),
            },
        ]
        
        # Calculate the height based on the number of items
        item_height = 48  # Assuming each item height is 48dp
        menu_height = len(menu_items) * item_height
    
        self.menu = MDDropdownMenu(
            caller=caller,
            items=menu_items,
            width_mult=3, 
            max_height=menu_height+95,  # Set max_height to fit the content
        )
        self.menu.open()

    def menu_callback(self, action, time_str, box_layout, divider,tone):
        time_obj = datetime.strptime(time_str, '%I:%M %p')
        
        # Convert the datetime object to a 24-hour format time string
        time=time_obj.strftime('%H:%M')
        print(f"menu_callback{time}")
        if action == "edit":
            self.add_edit_tone_content(time,tone)
        elif action == "delete":
            self.remove_box(time_str, box_layout, divider)

        self.menu.dismiss()

    def update_alarm_tone(self, time_str, tone):
        # Open the CSV file in read mode
        with open('alarms.csv', mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        #print(rows)
        # Update the rows if time_str matches
        for row in rows:
            print(time_str)
            #print(row)
            #print(row[0],time_str)
            if row[0] == time_str:
                
                row[1] = tone
                print("mil gya")
                
                
                break
        print(rows)          
        
        # Write the updated rows back to the CSV file
        with open('alarms.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
            print("done")
    #def update_alarm_tone(self):
        
        
        
        
        
    def on_switch_active(self, switch_instance, is_active, time_str):
        for alarm in self.alarm_times:
            if alarm['time'] == time_str:
                alarm['active'] = is_active
                break
        self.update_alarms_csv()
        print(f"Switch for {time_str} is now {'ON' if is_active else 'OFF'}")

    def check_alarms(self, dt):
        now = datetime.now().strftime("%I:%M %p")
        for alarm in self.alarm_times:
            #print(f"Checking alarm: {alarm['time']} against current time: {now}")
            if alarm['active'] and alarm['time'] == now:
                self.play_alarm_sound(alarm)
                self.show_alarm_dialog()
                alarm['active'] = False
                alarm['switch'].active = False

    def play_alarm_sound(self, alarm):
        try:
            # Open the CSV file and read the alarms
            with open('alarms.csv', 'r') as file:
                reader = csv.reader(file)
                alarm_tone = "default.mp3"  # Default tone in case no match is found
    
                # Ensure 'alarm' is a dictionary
                if isinstance(alarm, dict) and 'time' in alarm:
                    alarm_time = alarm['time']
                else:
                    print("Invalid alarm format, expected a dictionary with a 'time' key.")
                    return
                
                time_24hr = datetime.strptime(alarm_time, "%I:%M %p").strftime("%H:%M")
                print(f"time_24hr: {time_24hr}")
    
                for row in reader:
                    print(f"row: {row}")
                    if row[0] == time_24hr:
                        alarm_tone = row[1]
                        print(f"alarm tone: {alarm_tone}")
                        break
    
            # Play the sound based on the alarm tone found
            if alarm_tone == "default":
                pygame.mixer.music.load('default.mp3')
            else:
                pygame.mixer.music.load(alarm_tone)
            
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Error loading sound: {e}")
  
    def show_alarm_dialog(self):
        self.dialog = MDDialog(
            title="Alarm",
            text="The alarm is ringing!",
            buttons=[
                MDFlatButton(
                    text="Dismiss",
                    on_release=self.dismiss_alarm
                ),
                MDFlatButton(
                    text="Snooze",
                    on_release=self.snooze_alarm
                ),
            ],
        )
        self.dialog.open()

    def dismiss_alarm(self, *args):
        pygame.mixer.music.stop()
        if self.dialog:
            self.dialog.dismiss()

    def snooze_alarm(self, *args):
        pygame.mixer.music.stop()
        if self.dialog:
            self.dialog.dismiss()

        snooze_time = (datetime.now() + timedelta(minutes=5)).strftime("%I:%M %p")
        self.add_time_to_scrollview(snooze_time, "default")

    def remove_box(self, time_str, box_layout, divider):
        grid_layout = self.root.get_screen('main').ids.grid_layout
        grid_layout.remove_widget(box_layout)
        grid_layout.remove_widget(divider)
        self.alarm_times = [alarm for alarm in self.alarm_times if alarm['time'] != time_str]
        self.update_alarms_csv(time_str)
        print(f"Removed alarm set for {time_str}")
        self.msg_dialog("Action","Alarm deleted")

    def update_alarms_csv(self):
        with open("alarms.csv", "w", newline='') as file:
            writer = csv.writer(file)
            for alarm in self.alarm_times:
                time_24hr = datetime.strptime(alarm['time'], "%I:%M %p").strftime("%H:%M")
                writer.writerow([time_24hr, alarm['tone'], alarm['active']])

    def msg_dialog(self, title,message):
        self.dialog1 = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=self.close_msg_dialog
                ),
            ],
        )
        self.dialog1.open()

    def close_msg_dialog(self, *args):
        self.dialog1.dismiss()

    def add_edit_tone_content(self, time_str,tone):
        # Find the edit_tone screen
        with open ("alarms.csv","r") as file:
            data=csv.reader(file)
            for row in data:
                if row[0]==time_str:
                    tone1=row[1]
                    
        edit_tone_screen = self.root.get_screen('edit_tone')
    
        # Clear previous content
        edit_tone_screen.clear_widgets()
    
        # Create a BoxLayout to hold the content
        layout = MDBoxLayout(orientation='vertical', padding=(50, 350, 50, 350), spacing=10)
    
        # Add the MDLabel for time
        alarm_time_but = MDLabel(
            text=f"{time_str}",
            halign="center",
            font_style="H2",
        )
    
        # Add canvas.before to set background color
        with alarm_time_but.canvas.before:
            Color(1, 1,1, 1)  # Set the color to white (RGBA)
            Rectangle(pos=alarm_time_but.pos, size=alarm_time_but.size)
    
        # Add the MDLabel for tone
        alarm_tone_but = MDLabel(
            text=f"[alarm_tone] : {tone1}",
            halign="center",
            font_style="Caption"
        )
    
        # Add canvas.before to set background color
        with alarm_tone_but.canvas.before:
            Color(1, 1, 1, 1)  # Set the color to white (RGBA)
            Rectangle(pos=alarm_tone_but.pos, size=alarm_tone_but.size)
    
        layout.add_widget(alarm_time_but)
        layout.add_widget(alarm_tone_but)
    
        # Add the "Set Default Alarm Tone" button
        set_default_alarm_button = MDRaisedButton(
            text="Set Default Alarm Tone",
            on_release=lambda x: self.set_default_alarm_tone(time_str)
        )
        layout.add_widget(set_default_alarm_button)
    
        # Add the "Select Alarm Tone from System" button
        select_alarm_tone_button = MDRaisedButton(
            text="Select Alarm Tone from System",
            on_release=lambda x: self.select_alarm_tone(time_str)
        )
        layout.add_widget(select_alarm_tone_button)
    
        # Add the "Text to Speech Alarm Tone" button
        tts_alarm_tone_button = MDRaisedButton(
            text="Text to Speech Alarm Tone",
            on_release=lambda x: self.text_to_speech_alarm_tone(time_str)
        )
        layout.add_widget(tts_alarm_tone_button)
    
        # Add the "Back" button
        back_button = MDFlatButton(
            text="Back",
            on_release=lambda x: self.back_to_main()
        )
        layout.add_widget(back_button)

        # Add the layout to the screen
        edit_tone_screen.add_widget(layout)
        self.root.current = "edit_tone"

    def set_default_alarm_tone(self,time_str):
        self.update_alarm_tone(time_str,"default.mp3")
        self.msg_dialog('Action','Alarm tone selected to default!!')
        self.back_to_main()

    def select_alarm_tone(self, time_str):
        filechooser = FileChooserListView(filters=['*.mp3'])
        popup = Popup(title="Select Alarm Tone", content=filechooser, size_hint=(0.9, 0.4))
        filechooser.bind(on_submit=lambda instance, selection, touch: self.load_selected_tone(selection, time_str,popup))
        
        popup.open()
        
    
    def load_selected_tone(self, selection, time_str,popup):
        if selection:
            selected_file = selection[0]
            self.update_alarm_tone(time_str, selected_file)
            popup.dismiss()
            self.back_to_main()
            self.msg_dialog("Action",f"alarm tone selected to : {selected_file}")

    from kivy.metrics import dp
    
    def text_to_speech_alarm_tone(self, time_str):
        # Create the text field
        self.text_field = MDTextField(
            hint_text="Enter something for text to speech",
            size_hint=(1, None),
            multiline=True,
            height=dp(40)
        )
    
        # Create the dialog
        self.dialog = MDDialog(
            title="Text to Speech",
            type="custom",
            content_cls=self.text_field,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.close_dialog
                ),
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.process_tts_input(self.text_field.text, time_str)
                ),
            ],
        )
    
        # Open the dialog
        self.dialog.open()
        self.text_field.focus = True
    
    def close_dialog(self, instance):
        self.dialog.dismiss()
    
    def process_tts_input(self, text, time_str):
        # Process the text for text-to-speech functionality
        # Close the dialog after processing
        if text:
            filename=text.replace(" ","_")
            tts = gTTS(text=text, lang='en')
            tts.save(f"{filename}.mp3")
            sound = SoundLoader.load("output.mp3")
            file=f"{filename}.mp3"
            self.update_alarm_tone(time_str, file)
        self.dialog.dismiss()
        self.msg_dialog("Action","alarm tone selected successfully!!")
        self.back_to_main()
    
    def back_to_main(self):
        self.root.current = "main"

if __name__ == '__main__':
    MyApp().run()

