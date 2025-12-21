import unittest
from unittest.mock import patch, MagicMock
import chat
from lifet.memory.memory import InMemoryMemory
from lifet.coder.llm_adapters.llm_adapter_protocol import ResponseLLM, RequestLLM

class TestChat(unittest.TestCase):

    @patch('chat.prompt')
    @patch('chat.initialize_coder')
    @patch('chat.console.print')
    def test_exit_command(self, mock_print, mock_initialize_coder, mock_prompt):
        """Test that the /exit command breaks the loop."""
        mock_prompt.return_value = '/exit'
        mock_coder = MagicMock()
        mock_initialize_coder.return_value = mock_coder
        chat.main()
        mock_print.assert_any_call("[yellow]Ending chat session. Goodbye![/yellow]")

    @patch('chat.prompt')
    @patch('chat.initialize_coder')
    @patch('chat.console.print')
    def test_reset_command(self, mock_print, mock_initialize_coder, mock_prompt):
        """Test that the /reset command resets the memory."""
        mock_prompt.side_effect = ['/reset', '/exit']
        
        mock_coder = MagicMock()
        initial_memory = InMemoryMemory()
        mock_coder.memory = initial_memory
        
        mock_initialize_coder.return_value = mock_coder

        chat.main()

        self.assertIsNot(mock_coder.memory, initial_memory)
        mock_print.assert_any_call("[yellow]Memory has been reset.[/yellow]")


    @patch('chat.prompt')
    @patch('chat.initialize_coder')
    @patch('chat.console.print')
    @patch('chat.display_agent_thought')
    def test_agent_interaction(self, mock_display, mock_print, mock_initialize_coder, mock_prompt):
        """Test a simple user input and agent response."""
        user_input = "Hello, agent!"
        agent_response = "Hello, user!"
        mock_prompt.side_effect = [user_input, '/exit']
        
        mock_coder = MagicMock()
        response = ResponseLLM(
            reasoning="Thinking...", 
            response=agent_response, 
            tool_calls=[], 
            task_end=True
        )
        mock_coder.code.return_value = response
        mock_initialize_coder.return_value = mock_coder

        chat.main()
        
        self.assertTrue(mock_coder.code.called)
        call_args = mock_coder.code.call_args[0][0]
        self.assertIsInstance(call_args, RequestLLM)
        self.assertEqual(call_args.request_user, user_input)
        
        mock_display.assert_called_once_with(response)
        mock_print.assert_any_call(f"\n[blue]Agent:[/blue] {agent_response}")

    @patch('chat.prompt', side_effect=KeyboardInterrupt)
    @patch('chat.initialize_coder')
    @patch('chat.console.print')
    def test_keyboard_interrupt(self, mock_print, mock_initialize_coder, mock_prompt):
        """Test that KeyboardInterrupt is handled gracefully."""
        mock_coder = MagicMock()
        mock_initialize_coder.return_value = mock_coder

        chat.main()
        
        mock_print.assert_any_call("\n\n[yellow]Ending chat session. Goodbye![/yellow]")

    @patch('chat.prompt')
    @patch('chat.initialize_coder')
    @patch('chat.console.print')
    def test_agent_failure(self, mock_print, mock_initialize_coder, mock_prompt):
        """Test that the CLI handles the agent failing to complete the task."""
        mock_prompt.side_effect = ['some input', '/exit']
        
        mock_coder = MagicMock()
        mock_coder.code.return_value = None  # Simulate Coder failing
        mock_initialize_coder.return_value = mock_coder

        chat.main()
        
        mock_print.assert_any_call("\n[bold red]Agent could not complete the task after several attempts.[/bold red]")


if __name__ == '__main__':
    unittest.main()
