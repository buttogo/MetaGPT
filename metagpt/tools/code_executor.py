#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/11/6 15:51
# @Author  : lidanyang
# @File    : code_executor
# @Desc    :
from abc import ABC, abstractmethod

import nbformat
from nbclient import NotebookClient

from metagpt.const import DATA_PATH


class CodeExecutor(ABC):
    def __init__(self):
        self.workspace = DATA_PATH / "code_executor"
        self.workspace.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def run(self, code: str):
        raise NotImplementedError


class PythonExecutor(CodeExecutor):
    def __init__(self):
        super().__init__()
        self.nb = nbformat.v4.new_notebook()
        self.nb_client = NotebookClient(self.nb)

    async def _is_kernel_alive(self):
        if self.nb_client.kc is not None:
            return await self.nb_client.kc.is_alive()
        return False

    async def _cleanup_kernel(self):
        if await self._is_kernel_alive():
            await self.nb_client._async_cleanup_kernel()

    async def _start_kernel(self):
        self.nb_client.create_kernel_manager()
        self.nb_client.start_new_kernel()
        self.nb_client.start_new_kernel_client()

    async def reset(self):
        await self._cleanup_kernel()
        await self._start_kernel()

    async def run(self, code: str, reset: bool = False):
        if reset or not await self._is_kernel_alive():
            await self.reset()
        self.nb.cells.append(nbformat.v4.new_code_cell(code))
        cell_index = len(self.nb.cells) - 1

        try:
            await self.nb_client.async_execute_cell(self.nb.cells[-1], cell_index)
            return self.format_outputs(self.nb.cells[-1].outputs)
        except Exception as e:
            return {
                "success": False,
                "result": str(e),  # TODO: better error message
            }

    def format_outputs(self, outputs):
        formatted_output = {
            "success": True,
            "result": "",
            "images": [],
        }
        # TODO: support more output types
        for output in outputs:
            if output.output_type == "execute_result":
                formatted_output["result"] = output.data["text/plain"]
            elif output.output_type == "display_data":
                formatted_output["images"].append(output.data["image/png"])
        return formatted_output

    async def close(self):
        await self._cleanup_kernel()

    def get_history_code(self):
        return [cell.source for cell in self.nb.cells]
