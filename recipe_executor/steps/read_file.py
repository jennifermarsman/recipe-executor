import os
import logging
from typing import Optional

from recipe_executor.steps.base import BaseStep, StepConfig
from recipe_executor.context import Context
from recipe_executor.utils import render_template


class ReadFileConfig(StepConfig):
    """
    Configuration for ReadFileStep.

    Fields:
        path (str): Path to the file to read (may be templated).
        artifact (str): Name to store the file contents in context.
        optional (bool): Whether to continue if the file is not found.
    """
    path: str
    artifact: str
    optional: bool = False


class ReadFileStep(BaseStep[ReadFileConfig]):
    """
    ReadFileStep component reads a file from the filesystem and stores its contents into the execution context.

    This step renders the file path using the given context, reads the contents of the file, and assigns it to a specified key.
    It handles missing files based on the 'optional' configuration flag. If the file is optional and not found,
    an empty string is stored in the context, otherwise a FileNotFoundError is raised.
    """
    
    def __init__(self, config: dict, logger: Optional[logging.Logger] = None) -> None:
        # Convert the provided config dictionary into a ReadFileConfig instance and initialize the base step
        super().__init__(ReadFileConfig(**config), logger)

    def execute(self, context: Context) -> None:
        """
        Execute the ReadFileStep:
          - Render the file path using template rendering
          - Check for file existence
          - Read file content using UTF-8 encoding
          - Store the content into the context under the specified artifact key
          - Handle missing files based on the 'optional' flag

        Args:
            context (Context): The shared execution context.

        Raises:
            FileNotFoundError: If the file is not found and the step is not marked as optional.
        """
        # Render the file path using values from the execution context
        path: str = render_template(self.config.path, context)
        self.logger.debug(f"Rendered file path: {path}")

        # Check if the file exists at the rendered path
        if not os.path.exists(path):
            if self.config.optional:
                self.logger.warning(f"Optional file not found at path: {path}, continuing without file.")
                context[self.config.artifact] = ""
                return
            else:
                error_msg: str = f"ReadFileStep: file not found at path: {path}"
                self.logger.error(error_msg)
                raise FileNotFoundError(error_msg)

        # File exists, attempt to read its contents with UTF-8 encoding
        self.logger.info(f"Reading file from path: {path}")
        try:
            with open(path, "r", encoding="utf-8") as file:
                content: str = file.read()
        except Exception as e:
            self.logger.error(f"Error reading file at {path}: {e}")
            raise

        # Store the file content into the context under the specified artifact key
        context[self.config.artifact] = content
        self.logger.debug(f"Stored file contents in context under key: '{self.config.artifact}'")
