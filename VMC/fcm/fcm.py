import asyncio

from fcc_library import FlightControlComputer, PyMAVLinkAgent


class FlightControlModule:
    def __init__(self) -> None:
        super().__init__()

        # create the FCC objects
        self.fcc = FlightControlComputer()
        self.gps_fcc = PyMAVLinkAgent()

    async def run(self) -> None:
        self.gps_fcc.run_non_blocking()

        asyncio.gather(self.fcc.run_non_blocking())

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    fcm = FlightControlModule()
    asyncio.run(fcm.run())
