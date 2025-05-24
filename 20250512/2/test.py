import unittest
import mood.client as client
from unittest.mock import MagicMock, patch

class TestClient(unittest.TestCase):
    def setUp(self):
        self.mocker = MagicMock()
        self.cmdline = client.Client(socket=self.mocker)

    def test_1(self):
        """Test up"""
        self.cmdline.do_down("")
        self.mocker.sendall.assert_called_with("move 0 1\n".encode())

    def test_2(self):
        """Test left"""
        self.cmdline.do_right("")
        self.mocker.sendall.assert_called_with("move 1 0\n".encode())

    @patch('builtins.input', side_effect=['admon', EOFError])
    def test_3(self, inp):
        """Test incorrect"""
        with patch('builtins.print') as mock_print:
            self.cmdline.prompt = ''
            self.cmdline.cmdloop()
            self.mocker.sendall.assert_not_called()
            mock_print.assert_called()
            error_message = mock_print.call_args[0][0]
            self.assertIn("Invalid command", error_message)


    def tearDown(self):
        """Очистка после каждого теста"""
        self.mocker.reset_mock()