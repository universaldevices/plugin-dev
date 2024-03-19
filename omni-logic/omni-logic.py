#!/usr/bin/env python3
"""
Polyglot v3 plugin for Hayward OmniLogic Pool Controllers 
Copyright (C) 2024  Universal Devices
"""
import asyncio

from omnilogic import OmniLogic


async def do_test():
    api_client=OmniLogic("greg@dixons.net","paiw9duc*SLEH_nuth")
    telemetry_data = await api_client.get_telemetry_data()
    print (telemetry_data)

def do_plugin():
    polyglot = udi_interface.Interface([])
    polyglot.start('1.3.0')


    # subscribe to the events we want
    polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
    polyglot.subscribe(polyglot.POLL, poll)

    # Start running
    polyglot.ready()
    polyglot.setCustomParamsDoc()

    # Just sit and wait for events
    polyglot.runForever()


if __name__ == "__main__":
    try:
#        do_plugin()
        asyncio.run(do_test())

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
