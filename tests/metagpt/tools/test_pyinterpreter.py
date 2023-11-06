import pytest

from metagpt.tools.pyinterpreter import PyInterpreter


@pytest.mark.asyncio
async def test_code_running():
    pi = PyInterpreter()
    output = await pi.run("print('hello world!')")
    assert output == "code running successful\nhello world!\n"
    assert "successful" in output


@pytest.mark.asyncio
async def test_split_code_running():
    pi = PyInterpreter()
    output = await pi.run("x=1\ny=2")
    output = await pi.run("z=x+y")
    output = await pi.run("assert z==3")
    assert "successful" in output


@pytest.mark.asyncio
async def test_file_code_running():
    pi = PyInterpreter()
    code_path = "tests/data/python_code.py"
    output = await pi.run(code_path)
    assert "successful" in output
