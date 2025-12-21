import unittest
import os
import shutil
from lifet.tools.read_file_tool import ReadFileTool
from lifet.tools.write_file_tool import WriteFileTool
from lifet.tools.list_files_tool import ListFilesTool

class TestTools(unittest.TestCase):

    def setUp(self):
        self.test_dir = "test_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        self.test_content = "Hello, world!"
        with open(self.test_file, "w") as f:
            f.write(self.test_content)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read_file_tool(self):
        read_tool = ReadFileTool()
        response = read_tool.execute(file_path=self.test_file)
        self.assertIsNone(response.error)
        self.assertEqual(response.result, self.test_content)

    def test_read_file_tool_not_found(self):
        read_tool = ReadFileTool()
        response = read_tool.execute(file_path="non_existent_file.txt")
        self.assertIsNotNone(response.error)
        self.assertIn("File not found", response.error)

    def test_write_file_tool(self):
        write_tool = WriteFileTool()
        new_content = "This is new content."
        new_file_path = os.path.join(self.test_dir, "new_file.txt")
        response = write_tool.execute(file_path=new_file_path, content=new_content)
        self.assertIsNone(response.error)
        self.assertTrue(os.path.exists(new_file_path))
        with open(new_file_path, "r") as f:
            self.assertEqual(f.read(), new_content)

    def test_list_files_tool(self):
        list_tool = ListFilesTool()
        response = list_tool.execute(path=self.test_dir)
        self.assertIsNone(response.error)
        self.assertIn("test_file.txt", response.result)

if __name__ == '__main__':
    unittest.main()
