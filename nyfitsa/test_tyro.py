"""Sum two numbers by calling a function with tyro."""
import tyro

def main(
        field1: str,
        field2: int = 3,
) -> None:
    """Function, whose arguments will be populated from a CLI interface.


    Args:

        field1: A string field.

        field2: A numeric field, with a default value.

    """

    print(field1, field2)

if __name__ == "__main__":
    tyro.cli(main)