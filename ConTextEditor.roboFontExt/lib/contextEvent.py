from mojo.subscriber import registerSubscriberEvent, getRegisteredSubscriberEvents
from context import DEFAULT_KEY

def register_custom_event():
    eventName = f"{DEFAULT_KEY}.changed"

    # we register the subscriber event only if necessary
    if eventName not in getRegisteredSubscriberEvents():
        registerSubscriberEvent(
            subscriberEventName=eventName,
            methodName="contexteditorDidChangeSettings",
            lowLevelEventNames=[eventName],
            dispatcher="roboFont",
            documentation="Send when the settings palette did change parameters.",
            delay=0,
            debug=True
        )
    print("registering event")
    print(eventName in getRegisteredSubscriberEvents())