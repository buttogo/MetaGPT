#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/11/6 20:16
# @Author  : lidanyang
# @File    : test_code_executor
# @Desc    :
import pytest

from metagpt.tools.code_executor import PythonExecutor


@pytest.mark.asyncio
async def test_python_executor():
    executor = PythonExecutor()
    await executor.run("a = 1")
    await executor.run("b = 2")
    res = await executor.run("a + b")
    assert res["success"] is True and res["result"] == "3"
    history_code = executor.get_history_code()
    assert history_code == ["a = 1", "b = 2", "a + b"]
