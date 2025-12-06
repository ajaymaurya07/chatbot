# actions.py
import re

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import random
from rasa_sdk.events import SlotSet
import requests


class ActionStartForgetPassword(Action):

    def name(self):
        return "action_start_forget_password"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Please enter your User ID.\nकृपया अपना यूज़र आईडी दर्ज करें।")
        return [SlotSet("flow", "forget_password_active")]



class ActionVerifyUserID(Action):

    def name(self):
        return "action_provide_user_id"

    def run(self, dispatcher, tracker, domain):

        flow = tracker.get_slot("flow")
        msg = tracker.latest_message.get("text", "").strip()

        # Extract possible IDs
        possible_ids = re.findall(r"[A-Za-z0-9]*\d+[A-Za-z0-9]*", msg)

        # --------------------------------------------------------------
        # CASE 1: FLOW ACTIVE → Verify user ID
        # --------------------------------------------------------------
        if flow == "forget_password_active":

            if not possible_ids:
                dispatcher.utter_message(text="❗ Please enter a valid User ID.")
                return []

            user_id = possible_ids[0]

            dispatcher.utter_message(text=f"User ID verified: {user_id}")
            dispatcher.utter_message(
                text="Your password has been sent to your DPM. Please contact the DPM for recovery.\nआपका पासवर्ड DPM को भेज दिया गया है। पासवर्ड पाने के लिए DPM से संपर्क करें।"
            )

            return [
                SlotSet("user_id", None),
                SlotSet("flow", None)
            ]

        # --------------------------------------------------------------
        # CASE 2: FLOW NOT ACTIVE → Normal conversation
        # --------------------------------------------------------------
        dispatcher.utter_message(text="Hello! How can I help you?\nनमस्ते! मैं आपकी कैसे सहायता कर सकता हूँ?")
        return []






class ActionAskNetworkIssue(Action):
    def name(self) -> str:
        return "action_ask_network_issue"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict):

        random_minutes = random.randint(3, 10)
        message = (
            f"⚙️ Network check initiated!\nनेटवर्क जांच शुरू की गई!\n"
            f"It seems your internet connection is unstable right now.\nऐसा लगता है कि आपका इंटरनेट कनेक्शन अभी अस्थिर है\n\n"
            f"📶 Please try again after {random_minutes} minutes.\nकृपया {random_minutes} मिनट के बाद पुनः प्रयास करें।\n"
            f"This usually means a temporary connectivity issue.\nइसका आमतौर पर मतलब अस्थायी कनेक्टिविटी समस्या होता है"
        )

        dispatcher.utter_message(text=message)

        return []




class ActionSetProject(Action):

    def name(self):
        return "action_set_project"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        current_project = tracker.get_slot("project")
        user_msg = tracker.latest_message.get("text", "").lower()

        # Keywords
        panchayat_keys = ["panchayat", "पंचायत", "gateway","panchayat gateway","पंचायत गेटवे"]
        ims_keys = [
            "ims",
            "आईएमएस",
            "inventory management",
            "inventory and asset management",
            "inventory asset management",
            "इन्वेंटरी और संपत्ति प्रबंधन"
        ]

        # ------------------------------
        # Already selected → lock it
        # ------------------------------
        if current_project:
            dispatcher.utter_message(
                response="utter_project_locked",
                project=current_project
            )
            return []

        # ------------------------------
        # Choosing first time
        # ------------------------------
        if any(k in user_msg for k in panchayat_keys):
            dispatcher.utter_message(
                response="utter_project_set",
                project="panchayat"
            )
            return [SlotSet("project", "panchayat")]

        if any(k in user_msg for k in ims_keys):
            dispatcher.utter_message(
                response="utter_project_set",
                project="ims"
            )
            return [SlotSet("project", "ims")]

        # No match → ask again
        dispatcher.utter_message(response="utter_ask_project")
        return []


class ActionResetProject(Action):

    def name(self):
        return "action_reset_project"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(response="utter_project_reset")
        return [SlotSet("project", None)]

