import time
import pyttsx3
import speech_recognition as sr
from threading import Lock

speech_lock = Lock()


def speak(text):

    with speech_lock:
        try:
            engine = pyttsx3.init()

            
            engine.setProperty("rate", 170)
            engine.setProperty("volume", 1.0)

            
            engine.say(str(text))
            engine.runAndWait()

            
            engine.stop()

            
            del engine

        except Exception as e:
            print(f"Speech Error: {e}")

    
    time.sleep(1.5)


def listen():

    try:
       
        time.sleep(0.5)

        
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1.2
        recognizer.operation_timeout = None

        
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            print("Listening... Please speak now.")
            audio = recognizer.listen(
                source,
                timeout=15,          
                phrase_time_limit=90 
            )

        print("Converting speech to text...")

        
        text = recognizer.recognize_google(
            audio,
            language="en-US"
        )

        print(f"You said: {text}")
        return text.strip()

    except sr.WaitTimeoutError:
        return "[Speech Recognition Error] No speech detected within the timeout period."

    except sr.UnknownValueError:
        return "[Speech Recognition Error] Could not understand the audio."

    except sr.RequestError as e:
        return f"[Speech Recognition Error] Google Speech Recognition service error: {e}"

    except OSError as e:
        return f"[Speech Recognition Error] Microphone device error: {e}"

    except Exception as e:
        return f"[Speech Recognition Error] {e}"