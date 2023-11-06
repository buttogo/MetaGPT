import asyncio
import subprocess
import sys
from pathlib import Path

from metagpt.tools.base import Tool


class PyInterpreter(Tool):
    def __init__(self) -> None:
        self.process = None

    async def build(self):
        # 启动子进程，将其标准输入和标准输出设置为管道
        self.process = await asyncio.create_subprocess_shell(
            sys.executable + " -i -q -u",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=False,
        )

    async def run(self, code: str) -> str:
        await self.build()

        code = self.preprocess_code(code)
        try:
            if not self.process.stdin.is_closing():
                self.process.stdin.write(code)
                await self.process.stdin.drain()
            else:
                # 连接已经关闭，可以重新建立连接或采取其他措施
                await self.build()
                self.process.stdin.write(code)
                await self.process.stdin.drain()
        except Exception as e:
            return str(e)

        if not self.process.stdin.is_closing():
            self.process.stdin.close()  # 关闭标准输入，以便子进程知道输入结束
        await self.process.wait()

        # 重定向标准输出，并等待子进程执行完成
        output, errors = await asyncio.gather(
            self.capture_output(self.process.stdout),
            self.capture_output(self.process.stderr),
        )

        if self.process.returncode == 0:
            return "code running successful\n" + output.decode("utf-8")
        elif self.process.returncode == 1:
            return "code running failed\n" + errors.decode("utf-8")
        return errors.decode("utf-8")

    async def exit(self):
        if self.process:
            await self.process.wait()
            if self.process.returncode is None:
                self.process.terminate()

    def preprocess_code(self, code: str) -> str:
        if code.endswith((".py", ".txt")):
            code = Path(code).read_text("utf-8")

        code = code.strip() + "\n"
        return code.encode("utf-8")

    async def capture_output(self, stream):
        output = "".encode("utf-8")
        async for line in stream:
            output += line
        return output

    def reset(self):
        self.process = None
