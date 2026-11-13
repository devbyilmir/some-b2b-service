import time


class ASGITimingMiddleware:
    '''
    asgi middleware
    
    '''
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = time.perf_counter() - start

                headers = list(message["headers"])
                headers.append(
                    (
                        b"x-asgi-process-time",
                        str(process_time).encode()
                    )
                )

                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_wrapper)

        process_time = time.perf_counter() - start
        print(f"ASGI middleware: {process_time:.6f} sec")