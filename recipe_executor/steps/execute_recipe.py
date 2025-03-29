import os

from recipe_executor.context import Context
from recipe_executor.executor import RecipeExecutor
from recipe_executor.steps.base import BaseStep, StepConfig


class ExecuteRecipeConfig(StepConfig):
    """Config for ExecuteRecipeStep."""

    recipe_path: str


class ExecuteRecipeStep(BaseStep):
    """
    Step that executes a sub-recipe using the same context.
    """

    def __init__(self, config: dict, logger=None) -> None:
        super().__init__(ExecuteRecipeConfig(**config), logger)

    def execute(self, context: Context) -> None:
        recipe_path = self.config.recipe_path

        if not os.path.exists(recipe_path):
            raise FileNotFoundError(f"Sub-recipe file not found: {recipe_path}")

        self.logger.info(f"Executing sub-recipe: {recipe_path}")

        executor = RecipeExecutor()
        executor.execute(recipe=recipe_path, context=context, logger=self.logger)

        self.logger.info(f"Completed sub-recipe: {recipe_path}")
