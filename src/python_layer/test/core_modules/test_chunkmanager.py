import shutil
import tempfile
from queue import Queue

import unittest
from unittest import mock

from core_modules.chunkmanager import ChunkManager


class TestChunkManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        logger = mock.MagicMock()
        todolist = Queue()

        self.cs = ChunkManager(logger, 0, self.test_dir, [], mn_manager, todolist)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_index(self):
        pass
