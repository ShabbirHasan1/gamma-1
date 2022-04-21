from typing import Awaitable, Any
import asyncio

class runAsync:
    def __init__(self):
        """This class exposes two methods to gain more control over the asynchronous execution of the program
           
           self.runParallel(*functions: Awaitable[Any]) -> None

           self.runSequential(*functions: Awaitable[Any]) -> None
        """
        return

    async def runParallel(*functions: Awaitable[Any]) -> None:
        await asyncio.gather(*functions)
    
    async def runSequential(*functions: Awaitable[Any]) -> None:
        for function in functions:
            await function